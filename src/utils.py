import logging
import os

import yaml
from dotenv import load_dotenv


def load_config(app_env="dev", config_path="config.yaml"):
    dotenv_path = f".env.{app_env}"
    load_dotenv(dotenv_path)

    with open(config_path, "r") as file:
        raw_config = file.read()

    expanded_config = os.path.expandvars(raw_config)
    return yaml.safe_load(expanded_config)


def setup_logging(level, logfile=None, stream_handler=True):
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Stream handler for console output
    if stream_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler if logfile is specified
    if logfile:
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
