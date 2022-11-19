""" Functions wrappers around OCC utility """

import os
import re
import subprocess
from typing import Union

from .log import cpa_logger as log


def get_cloud_config_value(value_name: str, default=None) -> Union[str, None]:
    """Returns decoded utf8 output of `occ config:system:get {value}` command."""

    _ = occ_call("config:system:get", value_name, log_error=default is None)
    return _ if _ is not None else default


def get_cloud_app_config_value(app_name: str, value_name: str, default=None) -> Union[str, None]:
    """Returns decoded utf8 output of `occ config:app:get {app} {value}` command."""

    _ = occ_call("config:app:get", app_name, value_name, log_error=default is None)
    return _ if _ is not None else default


def occ_call(occ_task, *params, decode: bool = True, log_error=True) -> Union[str, bytes, None]:
    """Wrapper for occ calls. If decode=False then raw stdout data will be returned from occ."""

    result = php_call(_OCC_PATH, "--no-warnings", occ_task, *params, decode=decode, log_error=log_error)
    if isinstance(result, str):
        clear_result = re.sub(r".*app.*require.*upgrade.*\n?", "", result, flags=re.IGNORECASE)
        clear_result = re.sub(r".*occ.*upgrade.*command.*\n?", "", clear_result, flags=re.IGNORECASE)
        return clear_result.strip("\n")
    return result


def php_call(*params, decode=True, log_error=True) -> Union[str, bytes, None]:
    """Calls PHP interpreter with the specified `params`.

    :param decode: boolean value indicating that the output should be decoded from bytes to a string. Default=``True``
    :param log_error: boolean value indicating should be exception info logged or not. Default=``True``

    :returns: output from executing PHP interpreter."""

    try:
        result = subprocess.run([_PHP_PATH, *params], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    except Exception:  # noqa # pylint: disable=broad-except
        if log_error:
            log.exception("php_call exception:")
        return None
    return result.stdout.decode("utf-8").rstrip("\n") if decode else result.stdout


_OCC_PATH = os.path.join(os.environ.get("SERVER_ROOT", "/var/www/nextcloud"), "occ")
_PHP_PATH = os.environ.get("PHP_PATH", "php")
