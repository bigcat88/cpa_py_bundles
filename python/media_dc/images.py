"""
Images processing functions.
"""

from io import BytesIO
from typing import Any

import numpy
from pi_heif import register_heif_opener
from PIL import Image, ImageOps

from python.nc_py_api import get_file_data, log

from .db_requests import store_err_image_hash, store_image_hash, store_task_files_group
from .imagehash import average_hash, dhash, phash, whash

try:
    from hexhamming import check_hexstrings_within_dist
except ImportError:
    check_hexstrings_within_dist = None

register_heif_opener()

ImagesGroups: dict[int, list[int]] = {}
SetOfGroups: list[Any] = []  # [flat_numpy_array1,flat_numpy_array2,flat_numpy_array3]


def process_images(settings: dict, image_records: list):
    for image_record in image_records:
        if image_record["skipped"] is not None:
            if image_record["skipped"] >= 2:
                continue
            if image_record["skipped"] != 0:
                image_record["hash"] = None
        else:
            image_record["skipped"] = 0
        if image_record["hash"] is None:
            log.debug("calculating hash for image: fileid = %u", image_record["fileid"])
            image_record["hash"] = process_hash(
                settings["hash_algo"],
                settings["hash_size"],
                image_record,
                settings["data_dir"],
                settings["remote_filesize_limit"],
            )
        else:
            if check_hexstrings_within_dist:
                image_record["hash"] = image_record["hash"].hex()
            else:
                image_record["hash"] = arr_hash_from_bytes(image_record["hash"])
        if image_record["hash"] is not None:
            process_image_record(settings["precision_img"], image_record)


def process_hash(algo: str, hash_size: int, image_info: dict, data_dir: str, remote_filesize_limit: int):
    data = get_file_data(image_info, data_dir, remote_filesize_limit)
    if len(data) == 0:
        return None
    hash_of_image = calc_hash(algo, hash_size, data)
    if hash_of_image is None:
        store_err_image_hash(image_info["fileid"], image_info["mtime"], image_info["skipped"] + 1)
        return None
    hash_str = arr_hash_to_string(hash_of_image)
    store_image_hash(image_info["fileid"], hash_str, image_info["mtime"])
    if check_hexstrings_within_dist:
        return hash_str
    return hash_of_image


def arr_hash_from_bytes(buf: bytes):
    return numpy.unpackbits(numpy.frombuffer(buf, dtype=numpy.uint8), axis=None)


def arr_hash_to_string(arr) -> str:
    return numpy.packbits(arr, axis=None).tobytes().hex()


def calc_hash(algo: str, hash_size: int, image_data: bytes):
    image_hash = hash_image_data(algo, hash_size, image_data)
    if image_hash is None:
        return None
    return image_hash.flatten()


def process_image_record(precision: int, image_record: dict):
    img_group_number = len(ImagesGroups)
    if check_hexstrings_within_dist:
        for i in range(img_group_number):
            if check_hexstrings_within_dist(SetOfGroups[i], image_record["hash"], precision):
                ImagesGroups[i].append((image_record["fileid"]))
                return
    else:
        for i in range(img_group_number):
            if numpy.count_nonzero(SetOfGroups[i] != image_record["hash"]) <= precision:
                ImagesGroups[i].append((image_record["fileid"]))
                return
    SetOfGroups.append(image_record["hash"])
    ImagesGroups[img_group_number] = [(image_record["fileid"])]


def reset_images():
    ImagesGroups.clear()
    SetOfGroups.clear()


def remove_solo_groups():
    groups_to_remove = []
    for group_key, files_id in ImagesGroups.items():
        if len(files_id) == 1:
            groups_to_remove.append(group_key)
    for key in groups_to_remove:
        del ImagesGroups[key]


def save_image_results(task_id: int) -> int:
    remove_solo_groups()
    log.debug("Images: Number of groups: %u", len(ImagesGroups))
    n_group = 1
    for files_id in ImagesGroups.values():
        for file_id in files_id:
            store_task_files_group(task_id, n_group, file_id)
        n_group += 1
    return n_group


def pil_to_hash(algo: str, hash_size: int, pil_image):
    pil_image = ImageOps.exif_transpose(pil_image)
    if algo == "phash":
        image_hash = phash(pil_image, hash_size=hash_size)
    elif algo == "dhash":
        image_hash = dhash(pil_image, hash_size=hash_size)
    elif algo == "whash":
        image_hash = whash(pil_image, hash_size=hash_size)
    elif algo == "average":
        image_hash = average_hash(pil_image, hash_size=hash_size)
    else:
        image_hash = None
    return image_hash


def hash_image_data(algo: str, hash_size: int, image_data: bytes):
    try:
        pil_image = Image.open(BytesIO(image_data))
        return pil_to_hash(algo, hash_size, pil_image)
    except Exception as exception_info:  # noqa # pylint: disable=broad-except
        log.debug("Exception during image processing:\n%s", str(exception_info))
        return None
