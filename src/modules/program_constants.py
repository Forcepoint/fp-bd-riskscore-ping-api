from itertools import chain

USER_CONFIG_FILE = "cfg.yml"
LOG_FILE_NAME = "risk-score-api.log"
CASB_DB_FILE = "casb_risk_score.sqlite"
FBA_DB_FILE = "fba_risk_score.sqlite"
CASB_LOGIN_FORM_ACTION_PATH = "/cm/j_spring_security_check"
CASB_USERS_CSV_PATH = (
    "/cm/rs/0/human_risk/accounts/reports/csv?sortBy=riskScore&sortDirection=DESC"
)
# CASB_USERS_CSV_PATH = "/cm/rs/0/human_risk/accounts/reports/csv?search=%2BriskScore%3A(%22%5B1%20TO%20*%5D%22)&sortBy=riskScore&sortDirection=DESC"
RISK_LEVEL_TOPIC_NAME = "ENTITY_RISK_LEVEL"
KAFKA_SECURITY_PROTOCOL = "SSL"
KAFKA_CONSUMER_GROUP_ID = None
KAFKA_PORT = 9093
NO_VALUE_PROVIDED = "NO_VALUE_PROVIDED"
CASB_FETCH_DATA_PERIOD_IN_MIN = "casb_fetch_data_period_in_min"
API_PORT = "api_port"
CASB_RISK_SCORE_FETCH_ENABLE = "casb_risk_score_fetch_enable"
SSL_PASSWORD = "ssl_password"

SSL_CAFILE = "ssl_cafile"
SSL_CERTFILE = "ssl_certfile"
SSL_KEYFILE = "ssl_keyfile"
SSL_CERTFILE_DEFAULT = "/app/fp-riskexporter-api/certs/server.crt"
SSL_KEYFILE_DEFAULT = "/app/fp-riskexporter-api/certs/server.key"
SSL_CAFILE_DEFAULT = "/app/fp-riskexporter-api/certs/kafka-ca.crt"

RISK_LEVEL_VALUES_DICT = {
    "risk_level_1": 1,
    "risk_level_2": 2,
    "risk_level_3": 3,
    "risk_level_4": 4,
    "risk_level_5": 5,
}
CASB_REQUIRED_CONFIGS_LIST = [
    "casb_saas_url",
    "casb_login_name",
    "casb_login_password",
    "risk_level_1",
    "risk_level_2",
    "risk_level_3",
    "risk_level_4",
    "risk_level_5",
]
FBA_RISK_SCORE_FETCH_ENABLE = "fba_risk_score_fetch_enable"
FBA_REQUIRED_CONFIGS_LIST = [
    "kafka_server_name",
    "kafka_server_ip",
]
USER_CONFIGS_LIST = chain(
    [
        CASB_FETCH_DATA_PERIOD_IN_MIN,
        CASB_RISK_SCORE_FETCH_ENABLE,
        FBA_RISK_SCORE_FETCH_ENABLE,
        API_PORT,
        SSL_PASSWORD,
        SSL_CAFILE,
        SSL_CERTFILE,
        SSL_KEYFILE,
    ],
    CASB_REQUIRED_CONFIGS_LIST,
    FBA_REQUIRED_CONFIGS_LIST,
)
