import json
import logging

import requests
from program_constants import (
    CASB_DB_FILE,
    CASB_LOGIN_FORM_ACTION_PATH,
    CASB_USERS_CSV_PATH,
)
from sqlitedict import SqliteDict


def _map_account_name_to_login_names(accounts):
    """
    Maps the accounts name to the login names. this method simply groups the csv rows by the account name
    :param accounts: list of accounts records
    :return: dict
    """
    accounts_dict = {}

    for account in accounts:
        columns = account.decode("utf-8").split(",")

        if len(columns) >= 3:
            account, login_name, risk_score = columns[0], columns[1], columns[2]

            if account not in accounts_dict:
                accounts_dict[account] = {"login_names": set(), "score": 0}

            accounts_dict[account]["login_names"].add(login_name)

            # Only insert the highest risk score for the login names belong to the account.
            if accounts_dict[account]["score"] < int(float(risk_score)):
                accounts_dict[account]["score"] = int(float(risk_score))

    return accounts_dict


def _get_risk_score_accounts(configs):
    """
    login to CASB and download csv file
    :return: unique accounts
    :exception: KeyboardInterrupt: to terminate the application
    """
    distinct_accounts = {}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    login_data = {
        "j_username": configs.user_config["casb_login_name"],
        "j_password": configs.user_config["casb_login_password"],
        "submit": "Login",
    }
    with requests.session() as session_1:
        session_1.post(
            "{}{}".format(
                configs.user_config["casb_saas_url"], CASB_LOGIN_FORM_ACTION_PATH
            ),
            data=login_data,
            headers=headers,
        )
        response = session_1.get(
            "{}{}".format(configs.user_config["casb_saas_url"], CASB_USERS_CSV_PATH)
        )
        if response.status_code == 200:
            if len(list(response.iter_lines())) > 1:
                content = str(response.content)
                if "<title>Forcepoint CASB - Login</title>" in content:
                    error_msg = "CASB login failure, please check credentials"
                    logging.error(error_msg)
                    raise Exception(error_msg)
                distinct_accounts = _map_account_name_to_login_names(
                    list(response.iter_lines())[1:]
                )
        else:
            print(
                "Failed in downloading risk score csv file with response code: {}".format(
                    response.status_code
                )
            )
    return distinct_accounts


def load_casb_risk_scores(configs):
    try:
        casb_risk_score_data = _get_risk_score_accounts(configs)
        casb_risk_score_data_source = SqliteDict(
            "{}/{}".format(configs.db_dir, CASB_DB_FILE),
            autocommit=True,
            encode=json.dumps,
        )
        for account in casb_risk_score_data:
            for login_name in casb_risk_score_data[account]["login_names"]:
                casb_risk_score_data_source[login_name] = casb_risk_score_data[account][
                    "score"
                ]
        casb_risk_score_data_source.close()
    except Exception as err:
        error_msg = (
            "load_casb_risk_scores - error connecting to casb url: {}, {}".format(
                configs.user_config["casb_saas_url"], err
            )
        )
        logging.error(error_msg)
        print(error_msg)


# Only used for testing
def _print_all_casb_risk_scores(db_dir):
    casb_risk_score_data_source = SqliteDict(
        "{}/{}".format(db_dir, CASB_DB_FILE), decode=json.loads
    )
    for key, value in casb_risk_score_data_source.iteritems():
        print("Entity: {} - Risk: {}".format(key, value))
    print("Total stored: {}".format(len(casb_risk_score_data_source)))
    casb_risk_score_data_source.close()
