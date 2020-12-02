RISK_LEVEL_MAPPING_1 = {
    1: list(range(0, 20)),
    2: list(range(20, 50)),
    3: list(range(50, 80)),
    4: list(range(80, 100)),
    5: 100,
}

RISK_LEVEL_MAPPING_2 = {
    1: list(range(0, 20)),
    2: list(range(20, 50)),
    3: list(range(50, 80)),
    4: list(range(80, 100)),
    5: list(range(100, 110)),
}

RISK_LEVEL_MAPPING_3 = {
    1: list(range(0, 10)),
    2: list(range(20, 50)),
    3: 50,
    4: [],
    5: 100,
}

RISK_LEVEL_USER_CONFIG_MAPPING_3 = {
    "risk_level_1": "0-9",
    "risk_level_2": "20-49",
    "risk_level_3": "50",
    "risk_level_5": "100+",
}

USER_CONFIGS_CASB = {
    "casb_saas_url": "www.example.com",
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

USER_CONFIGS_CASB_MISSING_VALUES = {
    "casb_saas_url": "www.example.com",
    "casb_login_name": "rob",
    "risk_level_2": "20-19",
}
