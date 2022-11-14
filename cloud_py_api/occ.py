""" Functions wrappers around OCC utility """

import logging
import os
import re
import subprocess
from typing import Union


Log = logging.getLogger("occ")
Log.propagate = False


def get_cloud_config_value(value_name: str, default=None) -> Union[str, None]:
    """Returns decoded utf8 output of `occ config:system:get {value}` command."""

    _ = occ_call("config:system:get", value_name)
    return _ if _ is not None else default


def get_cloud_app_config_value(app_name: str, value_name: str, default=None) -> Union[str, None]:
    """Returns decoded utf8 output of `occ config:app:get {app} {value}` command."""

    _ = occ_call('config:app:get', app_name, value_name)
    return _ if _ is not None else default


def occ_call(occ_task, *params, decode: bool = True)  -> Union[str, bytes, None]:
    """Wrapper for occ calls. If decode=False then raw stdout data will be returned from occ."""

    result = _php_call(_OCC_PATH, '--no-warnings', occ_task, *params, decode=decode)
    if result is not None and decode:
        clear_result = re.sub(r'.*app.*require.*upgrade.*\n?', '', result, flags=re.IGNORECASE)
        clear_result = re.sub(r'.*occ.*upgrade.*command.*\n?', '', clear_result, flags=re.IGNORECASE)
        return clear_result.strip('\n')
    return result


def _php_call(*params, decode=True) -> Union[str, bytes, None]:
    """Calls PHP interpreter with the specified `params`.

    :param decode: boolean value indicating that the output should be decoded from bytes to a string. Default=``True``

    :returns: output from executing PHP interpreter."""

    _dev_ex_params = ["sudo", "-u", "www-data"] if _DEV else []
    try:
        result = subprocess.run(
            _dev_ex_params + [_PHP_PATH, *params],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True
            )
    except Exception as exception_info:
        Log.exception(exception_info)
        return None
    return result.stdout.decode('utf-8').rstrip('\n') if decode else result.stdout


_OCC_PATH = os.environ.get("SERVER_ROOT", "/var/www/nextcloud")
_PHP_PATH = os.environ.get("PHP_PATH", "php")
_DEV = os.environ.get("DEV_MODE", False)
