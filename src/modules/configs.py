import logging
import os

from common import (
    create_dir,
    get_user_config_env_values,
    get_user_defined_configuration,
    get_yaml_content,
    is_user_configurations_complete,
)
from log_config import LogConfig
from program_constants import (
    CASB_REQUIRED_CONFIGS_LIST,
    FBA_REQUIRED_CONFIGS_LIST,
    LOG_FILE_NAME,
    NO_VALUE_PROVIDED,
    SSL_CAFILE,
    SSL_CAFILE_DEFAULT,
    SSL_CERTFILE,
    SSL_CERTFILE_DEFAULT,
    SSL_KEYFILE,
    SSL_KEYFILE_DEFAULT,
    SSL_PASSWORD,
    USER_CONFIG_FILE,
    USER_CONFIGS_LIST,
)


class Configs:
    def __init__(self):
        self._modules_dir = None
        self._source_dir = None
        self._home_dir = None
        self._config_file = None
        self.user_config = None
        self.db_dir = None
        self.log_dir = None
        self._init()
        print("Configs Initialized")

    def _init(self):
        """ Configs for the configuration file """
        self._modules_dir = os.path.dirname(os.path.realpath(__file__))
        self._source_dir = os.path.abspath(os.path.join(self._modules_dir, os.pardir))
        self._home_dir = os.path.abspath(os.path.join(self._source_dir, os.pardir))
        self._config_file = "{}/{}".format(self._home_dir, USER_CONFIG_FILE)
        """ Configs for the logging """
        self.log_dir = "{}/{}".format(self._home_dir, "logs")
        create_dir(self.log_dir)
        LogConfig(self.log_dir, LOG_FILE_NAME, logging.ERROR)
        """ Configs for the db directory """
        self.db_dir = "{}/{}".format(self._home_dir, "db")
        create_dir(self.db_dir)
        """ User defined Configs """
        self.user_config = get_yaml_content(self._config_file)
        # overwrite cfg.yml values into env values if they exist.
        self.user_config = get_user_config_env_values(
            self.user_config, USER_CONFIGS_LIST
        )
        # Defaults
        self.user_config[SSL_CERTFILE] = get_user_defined_configuration(
            self.user_config, SSL_CERTFILE, SSL_CERTFILE_DEFAULT
        )
        self.user_config[SSL_KEYFILE] = get_user_defined_configuration(
            self.user_config, SSL_KEYFILE, SSL_KEYFILE_DEFAULT
        )
        self.user_config[SSL_PASSWORD] = get_user_defined_configuration(
            self.user_config, SSL_PASSWORD, NO_VALUE_PROVIDED
        )
        self.user_config[SSL_CAFILE] = get_user_defined_configuration(
            self.user_config, SSL_CAFILE, SSL_CAFILE_DEFAULT
        )
        self._user_defind_required_configs(self.user_config)
        self._user_defind_runtime_safeguard(self.user_config)

    def _user_defind_required_configs(self, user_config):
        """ CASB Configs """
        casb_risk_score_fetch_enable = get_user_defined_configuration(
            user_config, "casb_risk_score_fetch_enable", False
        )
        if casb_risk_score_fetch_enable:
            is_user_configurations_complete(user_config, CASB_REQUIRED_CONFIGS_LIST)

        """ FBA Configs """
        fba_risk_score_fetch_enable = get_user_defined_configuration(
            user_config, "fba_risk_score_fetch_enable", False
        )
        if fba_risk_score_fetch_enable:
            is_user_configurations_complete(user_config, FBA_REQUIRED_CONFIGS_LIST)

    def _user_defind_runtime_safeguard(self, user_config):
        """ CASB Configs """
        user_config["casb_risk_score_fetch_enable"] = get_user_defined_configuration(
            user_config, "casb_risk_score_fetch_enable", False
        )
        if not user_config["casb_risk_score_fetch_enable"]:
            user_config["casb_saas_url"] = get_user_defined_configuration(
                user_config, "casb_saas_url", NO_VALUE_PROVIDED
            )
            user_config["casb_login_name"] = get_user_defined_configuration(
                user_config, "casb_login_name", NO_VALUE_PROVIDED
            )
            user_config["casb_login_password"] = get_user_defined_configuration(
                user_config, "casb_login_password", NO_VALUE_PROVIDED
            )

        """ FBA Configs """
        user_config["fba_risk_score_fetch_enable"] = get_user_defined_configuration(
            user_config, "fba_risk_score_fetch_enable", False
        )
        if not user_config["fba_risk_score_fetch_enable"]:
            user_config["kafka_server_name"] = get_user_defined_configuration(
                user_config, "kafka_server_name", NO_VALUE_PROVIDED
            )
