import logging
from ssl import PROTOCOL_TLSv1_2, SSLContext
from time import sleep

from flask import Flask
from gevent.pywsgi import WSGIServer

from casb_risk_score_util import load_casb_risk_scores
from common import (
    convert_mints_to_secs,
    get_only_digits,
    get_risk_level_map,
    get_user_defined_configuration,
)
from fba_risk_level_util import load_fba_risk_levels
from risk_level_api import risk_level_api


def load_casb_data(configs):
    period_in_min_config_value = get_user_defined_configuration(
        configs.user_config, "casb_fetch_data_period_in_min", 10
    )
    casb_fetch_data_period_in_min = get_only_digits(period_in_min_config_value)
    fetch_period_in_secs = convert_mints_to_secs(casb_fetch_data_period_in_min)
    while True:
        logging.info("Loading CASB Data")
        load_casb_risk_scores(configs)
        sleep(fetch_period_in_secs)


def load_fba_data(configs):
    logging.info("Loading FBA Data and Listening to FBA Data stream")
    load_fba_risk_levels(configs)


def _create_risk_level_flask_app(configs):
    flask_app = Flask(__name__)
    flask_app.url_map.strict_slashes = False
    risk_level_dict = get_risk_level_map(configs.user_config)
    flask_app.config.update(
        DB_DIR=configs.db_dir,
        SSL_CAFILE=configs.user_config["ssl_cafile"],
        SSL_CERTFILE=configs.user_config["ssl_certfile"],
        SSL_KEYFILE=configs.user_config["ssl_keyfile"],
        SSL_PASSWORD=configs.user_config["ssl_password"],
        FBA_RISK_SCORE_ENABLE=configs.user_config["fba_risk_score_fetch_enable"],
        KAFKA_SERVER_NAME=configs.user_config["kafka_server_name"],
        CASB_RISK_SCORE_ENABLE=configs.user_config["casb_risk_score_fetch_enable"],
        CASB_SAAS_URL=configs.user_config["casb_saas_url"],
        CASB_LOGIN_NAME=configs.user_config["casb_login_name"],
        CASB_LOGIN_PASSWORD=configs.user_config["casb_login_password"],
        RISK_LEVEL_MAPPING=risk_level_dict,
    )
    flask_app.register_blueprint(risk_level_api)
    return flask_app


def run_risk_level_api(configs):
    flask_app = _create_risk_level_flask_app(configs)
    port = int(get_user_defined_configuration(configs.user_config, "api_port", 5000))
    host = get_user_defined_configuration(configs.user_config, "host", "0.0.0.0")
    flask_only = get_user_defined_configuration(
        configs.user_config, "flask_only", False
    )
    http_only = get_user_defined_configuration(configs.user_config, "http_only", False)
    logging.info("Risk Level API Started...")

    ssl_context = None
    if not http_only:
        ssl_context = SSLContext(PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(
            certfile=configs.user_config["ssl_certfile"],
            keyfile=configs.user_config["ssl_keyfile"],
            password=configs.user_config["ssl_password"],
        )

    if flask_only:
        flask_app.run(host=host, port=port, ssl_context=ssl_context)
    else:
        if ssl_context:
            http_server = WSGIServer((host, port), flask_app, ssl_context=ssl_context)
        else:
            http_server = WSGIServer((host, port), flask_app)
        http_server.serve_forever()
