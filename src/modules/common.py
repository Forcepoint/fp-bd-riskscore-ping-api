import calendar
import datetime as dt
import logging
import os
import time
from collections.abc import Iterable
from subprocess import getstatusoutput

import requests
import yaml
from kafka import KafkaConsumer
from requests import session

from program_constants import (
    CASB_LOGIN_FORM_ACTION_PATH,
    KAFKA_PORT,
    KAFKA_SECURITY_PROTOCOL,
    RISK_LEVEL_TOPIC_NAME,
    RISK_LEVEL_VALUES_DICT,
)


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_yaml_content(file_path):
    if os.path.isfile(file_path):
        with open(file_path) as yaml_file:
            return yaml.safe_load(yaml_file)
    return {}


def convert_epoch_to_iso8601_format(seconds_since_epoch):
    return dt.datetime.utcfromtimestamp(seconds_since_epoch).isoformat()


def get_seconds_since_epoch():
    return calendar.timegm(time.gmtime())


def get_current_iso8601_format():
    return "{}Z".format(convert_epoch_to_iso8601_format(int(get_seconds_since_epoch())))


def is_url_available(url):
    if url:
        try:
            with session() as s:
                response = s.get(url)
                if response.status_code == 200:
                    return True, "{} available - OK".format(url)
        except:
            pass
    return False, "{} is not reachable - ERROR".format(url)


def is_login_success(url, username, password):
    if url:
        try:
            login_data = {
                "j_username": username,
                "j_password": password,
                "submit": "Login",
            }
            with requests.session() as login_session:
                response = login_session.post(
                    "{}{}".format(url, CASB_LOGIN_FORM_ACTION_PATH), data=login_data
                )
                if response.status_code == 200:
                    if len(list(response.iter_lines())) > 1:
                        content = str(response.content)
                        if "<title>Forcepoint CASB</title>" in content:
                            return True, "{} login success - OK".format(url)
        except:
            pass
    return False, "{} login failure - ERROR".format(url)


def is_host_available(host_name):
    if host_name:
        status, _ = getstatusoutput("ping -c 1 {}".format(host_name))
        if status == 0:
            return True, "{} available - OK".format(host_name)
    return False, "{} is not reachable - ERROR".format(host_name)


def is_kafka_connection_successful(
    host_name, ssl_cafile, ssl_certfile, ssl_keyfile, ssl_password
):
    try:
        consumer = KafkaConsumer(
            RISK_LEVEL_TOPIC_NAME,
            bootstrap_servers=["{}:{}".format(host_name, KAFKA_PORT)],
            security_protocol=KAFKA_SECURITY_PROTOCOL,
            ssl_cafile=ssl_cafile,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile,
            ssl_password=ssl_password,
            auto_offset_reset="latest",
        )
        consumer.close()
        return True, "{} connection is successful - OK".format(host_name)
    except:
        return False, "{} connection is not successful - ERROR".format(host_name)


def get_only_digits(value):
    return int("".join(c for c in str(value) if c.isdigit()))


def convert_mints_to_secs(minutes_amount):
    return int(minutes_amount) * 60


def get_user_defined_configuration(user_configs_dict, user_key, default_value):
    try:
        value = user_configs_dict[user_key]
        if value is not None and value != "":
            return value
    except KeyError:
        pass
    logging.warning(
        "{} is missing from the config file, defaulting to value of {}".format(
            user_key, default_value
        )
    )
    return default_value


def is_user_configurations_complete(user_config, required_configs_list):
    for conf_key in required_configs_list:
        conf_value = get_user_defined_configuration(user_config, conf_key, None)
        if conf_value is None:
            error_msg = "User Configurations are not complete, missing {}".format(
                conf_key
            )
            logging.error(error_msg)
            raise SystemExit(error_msg)
    return True


def load_env_value(env_key):
    try:
        return os.environ[env_key]
    except KeyError:
        logging.info("Missing env value for : {}".format(env_key))
        return None


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def parse_env_value(s):
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    elif isfloat(s):
        if s.lower() in ("nan", "inf", "infinity"):
            return s
        else:
            return float(s)
    return s


def get_user_config_env_values(user_config, user_configs_list):
    new_user_config = user_config.copy()
    for key in user_configs_list:
        env_value = load_env_value(key)
        if env_value is not None:
            value = parse_env_value(env_value)
            new_user_config.update({key: value})
    return new_user_config


def parse_risk_level_value(risk_level_user_provided_value):
    value = risk_level_user_provided_value.strip()
    if "-1" == value:
        return []
    elif "-" in value:
        return list(range(int(value.split("-")[0]), int(value.split("-")[1]) + 1))
    elif "+" in value:
        return int(value.split("+")[0])
    return int(value)


def get_risk_level_map(user_config):
    risk_level_map = dict()
    for risk_level, level_value in RISK_LEVEL_VALUES_DICT.items():
        risk_level_user_provided_value = get_user_defined_configuration(
            user_config, risk_level, "-1"
        )
        risk_level_parsed_value = parse_risk_level_value(risk_level_user_provided_value)
        risk_level_map[level_value] = risk_level_parsed_value
    return risk_level_map


def get_risk_level(risk_level_dict, risk_score):
    for level, scores in risk_level_dict.items():
        if isinstance(scores, Iterable):
            for score in scores:
                if score == risk_score:
                    return level
        elif isfloat(scores):
            if scores == risk_score:
                return level
    if isinstance(risk_level_dict[5], Iterable) or (
        isfloat(risk_level_dict[5]) and risk_score < risk_level_dict[5]
    ):
        logging.warning(
            "this risk score {} is not mapped in the configuration, defaulting to risk level 5".format(
                risk_score
            )
        )
    return 5
