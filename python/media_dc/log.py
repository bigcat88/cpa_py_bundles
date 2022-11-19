from os import environ

from python.nc_py_api import LOGGER

MDC_LOGGER = LOGGER.getChild("mediadc")
MDC_LOGGER.setLevel(level=environ.get("LOGLEVEL", "INFO").upper())


def exception(msg, *args, **kwargs):
    MDC_LOGGER.exception(msg, *args, **kwargs)


def critical(*args, **kwargs):
    MDC_LOGGER.critical(*args, **kwargs)


def error(*args, **kwargs):
    MDC_LOGGER.error(*args, **kwargs)


def warning(*args, **kwargs):
    MDC_LOGGER.warning(*args, **kwargs)


def info(*args, **kwargs):
    MDC_LOGGER.info(*args, **kwargs)


def debug(*args, **kwargs):
    MDC_LOGGER.debug(*args, **kwargs)
