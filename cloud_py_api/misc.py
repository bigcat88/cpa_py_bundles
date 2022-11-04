import sys

import numpy
import pg8000
import pi_heif
import PIL
import pymysql
import pywt
import scipy

from cloud_py_api.version import __version__


def print_versions():
    print("Python: ", sys.version)
    print("CloudPyApi:", __version__)
    print("pg8000: ", pg8000.__version__)
    print("pymysql: ", pymysql.__version__)
    print("pillow: ", PIL.__version__)
    print("pi_heif: ", pi_heif.__version__)
    print("numpy: ", numpy.__version__)
    print("scipy: ", scipy.__version__)
    print("pywavelets: ", pywt.__version__)
