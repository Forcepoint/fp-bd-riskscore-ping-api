#!/usr/bin/env python3

import logging
from multiprocessing import Process

from gevent import monkey
# Monkey-patching need to be loaded before importing SSL
monkey.patch_all()

from configs import Configs
from risk_level_service import load_casb_data, load_fba_data, run_risk_level_api


if __name__ == "__main__":
    configs = Configs()

    """ Load CASB Data """
    if configs.user_config["casb_risk_score_fetch_enable"]:
        casb_data_load_batch = Process(target=load_casb_data, args=(configs,))
        casb_data_load_batch.start()

    """ Load FBA Data """
    if configs.user_config["fba_risk_score_fetch_enable"]:
        fba_data_load_batch = Process(target=load_fba_data, args=(configs,))
        fba_data_load_batch.start()

    """ Run API """
    if (
        configs.user_config["casb_risk_score_fetch_enable"]
        or configs.user_config["fba_risk_score_fetch_enable"]
    ):
        run_risk_level_api(configs)
    else:
        error_msg = "PLease enable casb_risk_score_fetch_enable OR fba_risk_score_fetch_enable first in the config file then run this again."
        logging.error(error_msg)
        print(error_msg)
