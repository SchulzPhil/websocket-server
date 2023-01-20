import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    c_handler = logging.StreamHandler()

    cf_format = logging.Formatter('%(process)d - %(asctime)s - %(levelname)s - %(message)s')

    c_handler.setFormatter(cf_format)

    logger.addHandler(c_handler)

    logger.setLevel(logging.INFO)

    return logger
