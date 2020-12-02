import json
from http import HTTPStatus

from flask import Blueprint
from flask import current_app as app
from flask import jsonify
from healthcheck import HealthCheck
from sqlitedict import SqliteDict

from common import (
    get_current_iso8601_format,
    get_risk_level,
    is_host_available,
    is_kafka_connection_successful,
    is_login_success,
    is_url_available,
)
from program_constants import CASB_DB_FILE, FBA_DB_FILE

risk_level_api = Blueprint("risk_level_api", __name__)


@risk_level_api.route("/riskexporter", methods=["GET"])
def _risk_level_api():
    response = {"name": "Risk Exporter Service"}
    return jsonify(response), HTTPStatus.OK


@risk_level_api.route("/fba/risk/level/<path:entity>", methods=["GET"])
def _risk_level_fba(entity):
    if app.config["FBA_RISK_SCORE_ENABLE"]:
        risk_level = -1
        iso_timestamp = get_current_iso8601_format()
        fba_risk_level_dict = SqliteDict(
            "{}/{}".format(app.config["DB_DIR"], FBA_DB_FILE), decode=json.loads
        )
        if entity in fba_risk_level_dict:
            risk_level = fba_risk_level_dict[entity]
        fba_risk_level_dict.close()
        response = {
            "user_id": entity,
            "timestamp": iso_timestamp,
            "risk_level": risk_level,
        }
        return jsonify(response), HTTPStatus.OK
    else:
        response = {
            "fba_risk_score_fetch_enable": "Set this flag to True and restart the service in order to enable this endpoint."
        }
        return jsonify(response), HTTPStatus.NOT_IMPLEMENTED


@risk_level_api.route("/casb/risk/level/<path:entity>", methods=["GET"])
def _risk_level_casb(entity):
    if app.config["CASB_RISK_SCORE_ENABLE"]:
        risk_level = -1
        iso_timestamp = get_current_iso8601_format()
        casb_risk_score_dict = SqliteDict(
            "{}/{}".format(app.config["DB_DIR"], CASB_DB_FILE), decode=json.loads
        )
        if entity in casb_risk_score_dict:
            risk_score = casb_risk_score_dict[entity]
            risk_level = get_risk_level(app.config["RISK_LEVEL_MAPPING"], risk_score)
        casb_risk_score_dict.close()
        response = {
            "user_id": entity,
            "timestamp": iso_timestamp,
            "risk_level": risk_level,
        }
        return jsonify(response), HTTPStatus.OK
    else:
        response = {
            "casb_risk_score_fetch_enable": "Set this flag to True and restart the service in order to enable this endpoint."
        }
        return jsonify(response), HTTPStatus.NOT_IMPLEMENTED


@risk_level_api.route("/riskexporter/dummy/event", methods=["POST"])
def _dummy_event():
    return jsonify({}), HTTPStatus.OK


@risk_level_api.after_request
def _add_header(response):
    response.headers["Version"] = 1
    response.headers["Content-Type"] = "application/json"
    return response


def _not_found_response():
    response = {"code": 404, "message": "HTTP 404 Not Found"}
    return jsonify(response), HTTPStatus.NOT_FOUND


@risk_level_api.route("/<path:invalid_path>")
def _page_not_found(*args, **kwargs):
    return _not_found_response()


casb_health = HealthCheck()
casb_health.add_check(lambda: is_url_available(app.config["CASB_SAAS_URL"]))
casb_health.add_check(
    lambda: is_login_success(
        app.config["CASB_SAAS_URL"],
        app.config["CASB_LOGIN_NAME"],
        app.config["CASB_LOGIN_PASSWORD"],
    )
)


@risk_level_api.route("/casb/healthcheck", methods=["GET"])
def _casb_risk_level_api_health_check():
    if app.config["CASB_RISK_SCORE_ENABLE"]:
        return casb_health.run()
    else:
        return _not_found_response()


fba_health = HealthCheck()
fba_health.add_check(lambda: is_host_available(app.config["KAFKA_SERVER_NAME"]))
fba_health.add_check(
    lambda: is_kafka_connection_successful(
        app.config["KAFKA_SERVER_NAME"],
        app.config["SSL_CAFILE"],
        app.config["SSL_CERTFILE"],
        app.config["SSL_KEYFILE"],
        app.config["SSL_PASSWORD"],
    )
)


@risk_level_api.route("/fba/healthcheck", methods=["GET"])
def _fba_risk_level_api_health_check():
    if app.config["FBA_RISK_SCORE_ENABLE"]:
        return fba_health.run()
    else:
        return _not_found_response()
