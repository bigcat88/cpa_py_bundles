import logging
from os import environ

logging.basicConfig(format="%(levelname)s:%(message)s")
LOGGER = logging.getLogger("nc_py_api")
LOGGER.setLevel(level=environ.get("LOGLEVEL", "INFO").upper())


def exception(msg, *args, **kwargs):
    LOGGER.exception(msg, *args, **kwargs)


def critical(*args, **kwargs):
    LOGGER.critical(*args, **kwargs)


def error(*args, **kwargs):
    LOGGER.error(*args, **kwargs)


def warning(*args, **kwargs):
    LOGGER.warning(*args, **kwargs)


def info(*args, **kwargs):
    LOGGER.info(*args, **kwargs)


def debug(*args, **kwargs):
    LOGGER.debug(*args, **kwargs)
