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
    log.info("Python: ", sys.version)
    log.info("CloudPyApi:", __version__)
    log.info("pg8000: ", pg8000.__version__)
    log.info("pymysql: ", pymysql.__version__)
    log.info("pillow: ", PIL.__version__)
    log.info("pi_heif: ", pi_heif.__version__)
    log.info("numpy: ", numpy.__version__)
    log.info("scipy: ", scipy.__version__)
    log.info("pywavelets: ", pywt.__version__)
