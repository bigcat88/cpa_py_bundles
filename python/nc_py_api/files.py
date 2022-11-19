"""
Helper functions related to get files content or storages info.
"""
from pathlib import Path

from .db_requests import get_storages_info
from .log import cpa_logger as log
from .occ import occ_call

STORAGES_INFO = get_storages_info()


def get_file_data(file_info: dict, data_dir: str, remote_filesize_limit: int) -> bytes:
    direct = can_directly_access_file(file_info)
    while direct:
        full_path = get_file_full_path(data_dir, file_info["storage"], file_info["path"])
        if not full_path:
            break
        try:
            with open(full_path, "rb") as h_file:
                data = h_file.read()
                return data
        except Exception:  # noqa # pylint: disable=broad-except
            log.exception("Exception during reading: %s-%s-%s:", file_info["storage"], data_dir, file_info["path"])
            break
    if file_info["size"] > remote_filesize_limit:
        return b""
    return request_file_from_php(file_info)


def request_file_from_php(file_info: dict) -> bytes:
    user_id = get_storage_user_id(file_info["storage"])
    if not user_id:
        return b""
    err_or_data = occ_call("mediadc:tasks:filecontents", str(file_info["fileid"]), user_id, decode=False)
    if isinstance(err_or_data, bytes):
        return err_or_data
    log.warning("get_file_data: %s", err_or_data)
    return b""


def get_file_full_path(data_dir: str, storage_id: int, relative_path: str) -> bytes:
    storage_info = get_storage_info(storage_id)
    if not storage_info:
        return b""
    path_data = storage_info["id"].split(sep="::", maxsplit=1)
    if len(path_data) != 2:
        log.warning("get_file_full_path: cant parse: %s", storage_info["id"])
        return b""
    if path_data[0] not in ["local", "home"]:
        return b""
    if path_data[1].startswith("/"):
        return path_data[1].encode("utf-8") + relative_path.encode("utf-8")
    data_dir_path = data_dir
    if not data_dir_path.endswith("/"):
        data_dir_path = data_dir_path + "/"
    if not path_data[1].endswith("/"):
        if not relative_path.startswith("/"):
            path_data[1] = path_data[1] + "/"
    return data_dir_path.encode("utf-8") + path_data[1].encode("utf-8") + relative_path.encode("utf-8")


def can_directly_access_file(file_info: dict) -> bool:
    if file_info["encrypted"] == 1:
        return False
    storage_info = get_storage_info(file_info["storage"])
    if not storage_info:
        return False
    if storage_info["available"] == 0:
        return False
    if storage_info.get("storage_backend") is None or storage_info.get("storage_backend") == "local":
        storage_txt_id = storage_info["id"]
        supported_start_list = ("local::", "home::")
        if storage_txt_id.startswith(supported_start_list):
            return True
    return False


def get_storage_info(storage_id: int) -> dict:
    for storage_info in STORAGES_INFO:
        if storage_info["numeric_id"] == storage_id:
            return storage_info
    return {}


def get_storage_mount_point(storage_id: int, encode: bool = True):
    for storage_info in STORAGES_INFO:
        if storage_info["numeric_id"] == storage_id:
            if encode:
                return storage_info["mount_point"].encode("utf-8")
            return storage_info["mount_point"]
    if encode:
        return b""
    return ""


def get_storage_user_id(storage_id: int) -> bytes:
    for storage_info in STORAGES_INFO:
        if storage_info["numeric_id"] == storage_id:
            return storage_info["user_id"].encode("utf-8")
    return b""


def get_mounts_to(storage_id: int, path: str) -> list[int]:
    return_list: list[int] = []
    mount_to = get_storage_mount_point(storage_id, encode=False) + path
    if not mount_to:
        return return_list
    for storage_info in STORAGES_INFO:
        if storage_info["mount_point"]:
            if mount_to == str(Path(storage_info["mount_point"]).parent):
                return_list.append(storage_info["root_id"])
    return return_list
