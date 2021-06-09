import json
import logging
import os
from signal import SIGTERM
from time import sleep

from kafka import KafkaConsumer, KafkaProducer
from program_constants import (
    FBA_DB_FILE,
    KAFKA_CONSUMER_GROUP_ID,
    KAFKA_PORT,
    KAFKA_SECURITY_PROTOCOL,
    RISK_LEVEL_TOPIC_NAME,
)
from sqlitedict import SqliteDict


def _value_deserializer(serialized_value):
    try:
        return json.loads(serialized_value.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _update_fab_data_store(kafka_message, data_source_dir):

    serialized_value = kafka_message.value
    value = _value_deserializer(serialized_value)
    if value:
        fba_risk_level_data_source = SqliteDict(
            "{}/{}".format(data_source_dir, FBA_DB_FILE),
            autocommit=True,
            encode=json.dumps,
        )
        entity = value["user_id"]
        risk_level_level = value["risk_level"]
        if entity:
            fba_risk_level_data_source[entity] = risk_level_level
        fba_risk_level_data_source.close()


def _create_fba_kafka_consumer(configs):

    return KafkaConsumer(
        RISK_LEVEL_TOPIC_NAME,
        bootstrap_servers=[
            "{}:{}".format(configs.user_config["kafka_server_name"], KAFKA_PORT)
        ],
        security_protocol=KAFKA_SECURITY_PROTOCOL,
        ssl_cafile=configs.user_config["ssl_cafile"],
        ssl_certfile=configs.user_config["ssl_certfile"],
        ssl_keyfile=configs.user_config["ssl_keyfile"],
        ssl_password=configs.user_config["ssl_password"],
        auto_offset_reset="earliest",
        group_id=KAFKA_CONSUMER_GROUP_ID,
    )


def load_fba_risk_levels(configs):

    try:
        consumer = _create_fba_kafka_consumer(configs)

        for kafka_message in consumer:
            logging.info(kafka_message.value)
            _update_fab_data_store(kafka_message, configs.db_dir)

    except Exception as err:
        error_msg = "load_fba_risk_levels - error connecting to fba kafka hostname: {}, {}".format(
            configs.user_config["kafka_server_name"], err
        )
        logging.error(error_msg)
        print(error_msg)
        # try again in 10 mints, in case of connection got lost
        sleep(600)
        load_fba_risk_levels(configs)


def _create_fba_kafka_producer(configs):

    return KafkaProducer(
        bootstrap_servers=[
            "{}:{}".format(configs.user_config["kafka_server_name"], KAFKA_PORT)
        ],
        security_protocol=KAFKA_SECURITY_PROTOCOL,
        ssl_cafile=configs.user_config["ssl_cafile"],
        ssl_certfile=configs.user_config["ssl_certfile"],
        ssl_keyfile=configs.user_config["ssl_keyfile"],
        ssl_password=configs.user_config["ssl_password"],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )


# Only used for testing
def publish_fba_risk_level(configs, kafka_message_lst):

    try:
        producer = _create_fba_kafka_producer(configs)
        for message in kafka_message_lst:
            producer.send(RISK_LEVEL_TOPIC_NAME, value=message)
            sleep(1)
        producer.close()
    except Exception as err:
        error_msg = "publish_fba_risk_level - error connecting to fba kafka hostname: {}, {}".format(
            configs.user_config["kafka_server_name"], err
        )
        logging.error(error_msg)
        print(error_msg)
        os.killpg(os.getpgid(os.getpid()), SIGTERM)
