import sys

import numpy
import pg8000
import pi_heif
import PIL
import pymysql
import pywt
import scipy

from cloud_py_api import log
from cloud_py_api._version import __version__


def print_versions():
    log.info("Python: %s", sys.version)
    log.info("CloudPyApi: %s", __version__)
    log.info("pg8000: %s", pg8000.__version__)
    log.info("pymysql: %s", pymysql.__version__)
    log.info("pillow: %s", PIL.__version__)
    log.info("pi_heif: %s", pi_heif.__version__)
    log.info("numpy: %s", numpy.__version__)
    log.info("scipy: %s", scipy.__version__)
    log.info("pywavelets: %s", pywt.__version__)
