import logging
from logging.handlers import RotatingFileHandler


class LogConfig:
    def __init__(self, log_dir, log_file_name, log_level=logging.INFO):
        self.log_dir = log_dir
        self.log_file_name = log_file_name
        self.log_file_path = None
        self.log_level = log_level
        self._init()

    def _init(self):
        self.log_file_path = "{}/{}".format(self.log_dir, self.log_file_name)
        self._setup_log_configs()

    def _setup_log_configs(self):
        logging_handler = RotatingFileHandler(
            self.log_file_path, maxBytes=int(1e7), backupCount=2
        )
        logging.basicConfig(
            level=self.log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging_handler],
        )
