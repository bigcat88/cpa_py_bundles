import sys

import numpy
import pg8000
import pi_heif
import PIL
import pymysql
import pywt
import scipy

from python import media_dc, nc_py_api

from .log import logger as log


def bundle_info():
    log.info("Python: %s", sys.version)
    log.info("nc_py_api: %s", nc_py_api.__version__)
    log.info("mediadc: %s", media_dc.__version__)
    log.info("pg8000: %s", pg8000.__version__)
    log.info("pymysql: %s", pymysql.__version__)
    log.info("pillow: %s", PIL.__version__)
    log.info("pi_heif: %s", pi_heif.__version__)
    log.info("numpy: %s", numpy.__version__)
    log.info("scipy: %s", scipy.__version__)
    log.info("pywavelets: %s", pywt.__version__)
