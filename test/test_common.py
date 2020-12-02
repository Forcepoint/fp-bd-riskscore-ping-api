from pytest import raises

from src.modules import common as c
from src.modules import program_constants as const

from .t_data import (
    RISK_LEVEL_MAPPING_1,
    RISK_LEVEL_MAPPING_2,
    RISK_LEVEL_MAPPING_3,
    RISK_LEVEL_USER_CONFIG_MAPPING_3,
    USER_CONFIGS_CASB,
    USER_CONFIGS_CASB_MISSING_VALUES,
)
from .t_helper_utils import create_env_varaible, create_file, delete_files


def test_get_yaml_content() -> None:
    assert c.get_yaml_content("no-file.yaml") == dict()
    create_file("test-file.yaml", """ "casb_saas_url": "new.com" """)
    assert c.get_yaml_content("test-file.yaml") == {"casb_saas_url": "new.com"}
    delete_files(["test-file.yaml"])


def test_convert_epoch_to_iso8601_format() -> None:
    assert c.convert_epoch_to_iso8601_format(1575971969) == "2019-12-10T09:59:29"


def test_is_url_available() -> None:
    assert c.is_url_available("https://google.com") == (
        True,
        "https://google.com available - OK",
    )
    assert c.is_url_available("...") == (False, "... is not reachable - ERROR")
    assert c.is_url_available("") == (False, " is not reachable - ERROR")


def test_is_host_available() -> None:
    assert c.is_host_available("google.com") == (True, "google.com available - OK")
    assert c.is_host_available("...") == (False, "... is not reachable - ERROR")
    assert c.is_host_available("") == (False, " is not reachable - ERROR")


def test_get_only_digits() -> None:
    with raises(Exception):
        c.get_only_digits("")
    assert c.get_only_digits(123) == 123
    assert c.get_only_digits("123 minutes") == 123
    assert c.get_only_digits("... 1") == 1
    assert c.get_only_digits("2m") == 2


def test_convert_mints_to_secs() -> None:
    with raises(Exception):
        c.get_only_digits("")
    with raises(Exception):
        c.get_only_digits("m")
    assert c.convert_mints_to_secs(10) == 600
    assert c.convert_mints_to_secs("10") == 600


def test_get_user_defined_configuration() -> None:
    assert c.get_user_defined_configuration(USER_CONFIGS_CASB, "not_available", 4) == 4
    assert (
        c.get_user_defined_configuration(USER_CONFIGS_CASB, "password", "default")
        == "default"
    )
    assert (
        c.get_user_defined_configuration(USER_CONFIGS_CASB, "casb_saas_url", 4)
        == "www.example.com"
    )
    assert (
        c.get_user_defined_configuration(
            USER_CONFIGS_CASB, "casb_login_name", "default"
        )
        == "rob"
    )


def test_is_user_configurations_complete() -> None:
    with raises(SystemExit):
        c.is_user_configurations_complete(
            USER_CONFIGS_CASB_MISSING_VALUES, const.CASB_REQUIRED_CONFIGS_LIST
        )
    assert (
        c.is_user_configurations_complete(
            USER_CONFIGS_CASB, const.CASB_REQUIRED_CONFIGS_LIST
        )
        is True
    )


def test_load_env_value() -> None:
    assert c.load_env_value("NO_EXIST") is None
    create_env_varaible("HOME_DIR", "/tmp")
    assert c.load_env_value("HOME_DIR") == "/tmp"


def test_isfloat() -> None:
    assert c.isfloat("123") is True
    assert c.isfloat("-123") is True
    assert c.isfloat("12.3") is True
    assert c.isfloat("-12.3") is True
    assert c.isfloat("NaN") is True
    assert c.isfloat("nan") is True
    assert c.isfloat("inf") is True
    assert c.isfloat("InF") is True
    assert c.isfloat("InFiNiTy") is True
    assert c.isfloat("infinity") is True
    assert c.isfloat("tRueo") is False
    assert c.isfloat("10.1.19.1") is False
    assert c.isfloat("None") is False
    with raises(Exception):
        c.isfloat(None)


def test_parse_env_value() -> None:
    assert c.parse_env_value("true") is True
    assert c.parse_env_value("True") is True
    assert c.parse_env_value("TRUE") is True
    assert c.parse_env_value("false") is False
    assert c.parse_env_value("False") is False
    assert c.parse_env_value("FALSE") is False
    assert c.parse_env_value("tRueo") == "tRueo"
    assert c.parse_env_value("10.1.19.1") == "10.1.19.1"
    assert c.parse_env_value("123") == 123
    assert c.parse_env_value("-123") == -123
    assert c.parse_env_value("12.3") == 12.3
    assert c.parse_env_value("-12.3") == -12.3
    assert c.parse_env_value("NaN") == "NaN"
    assert c.parse_env_value("nan") == "nan"
    assert c.parse_env_value("inf") == "inf"
    assert c.parse_env_value("InF") == "InF"
    assert c.parse_env_value("InFiNiTy") == "InFiNiTy"
    assert c.parse_env_value("infinity") == "infinity"
    assert c.parse_env_value("None") == "None"


def test_get_user_config_env_values() -> None:
    assert (
        c.get_user_config_env_values(
            USER_CONFIGS_CASB, const.CASB_REQUIRED_CONFIGS_LIST
        )
        == USER_CONFIGS_CASB
    )
    create_env_varaible("casb_saas_url", "new.com")
    assert c.get_user_config_env_values(
        USER_CONFIGS_CASB, const.CASB_REQUIRED_CONFIGS_LIST
    ) == {
        "casb_saas_url": "new.com",
        "casb_login_name": "rob",
        "casb_login_password": "123",
        "password": "",
        "ssl_certfile": "server.crt",
        "ssl_keyfile": "server.key",
        "risk_level_1": "0-19",
        "risk_level_2": "20-49",
        "risk_level_3": "50-79",
        "risk_level_4": "80-99",
        "risk_level_5": "100+",
    }
    test_date = {"casb_risk_score_fetch_enable": False}
    create_env_varaible("casb_risk_score_fetch_enable", "False")
    assert (
        c.get_user_config_env_values(test_date, [const.CASB_RISK_SCORE_FETCH_ENABLE])
        == test_date
    )
    create_env_varaible("casb_risk_score_fetch_enable", "True")
    assert c.get_user_config_env_values(
        test_date, [const.CASB_RISK_SCORE_FETCH_ENABLE]
    ) == {"casb_risk_score_fetch_enable": True}


def test_parse_risk_level_value() -> None:
    assert c.parse_risk_level_value("1-1") == [1]
    assert c.parse_risk_level_value("1-2") == [1, 2]
    assert c.parse_risk_level_value("1-3 ") == [1, 2, 3]
    assert c.parse_risk_level_value("3-2") == []
    assert c.parse_risk_level_value("100+") == 100
    assert c.parse_risk_level_value("-1") == []
    assert c.parse_risk_level_value(" 50") == 50
    with raises(Exception):
        c.parse_risk_level_value("+100")
    with raises(Exception):
        c.parse_risk_level_value("other")


def test_get_risk_level_map() -> None:
    assert c.get_risk_level_map(USER_CONFIGS_CASB) == RISK_LEVEL_MAPPING_1
    assert (
        c.get_risk_level_map(RISK_LEVEL_USER_CONFIG_MAPPING_3) == RISK_LEVEL_MAPPING_3
    )
    assert c.get_risk_level_map(USER_CONFIGS_CASB_MISSING_VALUES) == {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
    }


def test_get_risk_level() -> None:
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 0) == 1
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 7) == 1
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 20) == 2
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 21) == 2
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 50) == 3
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 59) == 3
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 80) == 4
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 99) == 4
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 100) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 101) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_1, 10000) == 5

    assert c.get_risk_level(RISK_LEVEL_MAPPING_2, 100) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_2, 111) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_2, 10000) == 5

    assert c.get_risk_level(RISK_LEVEL_MAPPING_3, 11) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_3, 50) == 3
    assert c.get_risk_level(RISK_LEVEL_MAPPING_3, 51) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_3, 80) == 5
    assert c.get_risk_level(RISK_LEVEL_MAPPING_3, 101) == 5
