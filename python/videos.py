"""
Videos processing functions.
"""

from json import dumps
from typing import Any, Optional, Union

import numpy
from nc_py_api import FsNodeInfo, fs_file_data, fs_sort_by_id

from .db_requests import (
    get_videos_caches,
    store_err_video_hash,
    store_task_files_group,
    store_video_hash,
)
from .ffmpeg_probe import ffprobe_get_video_info, stub_call_ff
from .images import arr_hash_from_bytes, arr_hash_to_string, calc_hash
from .log import logger as log

try:
    from hexhamming import check_hexstrings_within_dist
except ImportError:
    check_hexstrings_within_dist = None


class MdcVideoInfo(FsNodeInfo):
    hash: Optional[Union[bytes, str]]
    duration: Optional[int]
    timestamps: Optional[list[int]]
    skipped: Optional[int]


class InvalidVideo(Exception):
    """Exception for use inside `process_video_hash` function."""


VideoGroups: dict[int, list[int]] = {}
SetOfGroups: list[Any] = []  # hashes[ABCD+EFGH+IMGH+ZXCV,xx1+xx2+xx3+xx4]
MIN_VIDEO_DURATION = 3000
FIRST_FRAME_RESOLUTION = 64


def process_videos(settings: dict, fs_objs: list[FsNodeInfo]):
    mdc_videos_info = load_videos_caches(fs_objs)
    for mdc_video_info in mdc_videos_info:
        if mdc_video_info["skipped"] is not None:
            if mdc_video_info["skipped"] >= 2:
                continue
            if mdc_video_info["skipped"] != 0:
                mdc_video_info["hash"] = None
        else:
            mdc_video_info["skipped"] = 0
        if mdc_video_info["hash"] is None:
            log.debug("processing video: fileid = %u", mdc_video_info["id"])
            process_video_hash(
                settings["hash_algo"],
                settings["hash_size"],
                mdc_video_info,
            )
        else:
            if check_hexstrings_within_dist:
                mdc_video_info["hash"] = mdc_video_info["hash"].hex()
            else:
                mdc_video_info["hash"] = arr_hash_from_bytes(mdc_video_info["hash"])
        if mdc_video_info["hash"] is not None:
            process_video_record(settings["precision_vid"], mdc_video_info)


def process_video_record(precision: int, mdc_video_info: MdcVideoInfo):
    video_group_number = len(VideoGroups)
    if check_hexstrings_within_dist:
        for i in range(video_group_number):
            if check_hexstrings_within_dist(SetOfGroups[i], mdc_video_info["hash"], precision):
                VideoGroups[i].append(mdc_video_info["id"])
                return
    else:
        for i in range(video_group_number):
            if numpy.count_nonzero(SetOfGroups[i] != mdc_video_info["hash"]) <= precision:
                VideoGroups[i].append(mdc_video_info["id"])
                return
    SetOfGroups.append(mdc_video_info["hash"])
    VideoGroups[video_group_number] = [mdc_video_info["id"]]


def reset_videos():
    VideoGroups.clear()
    SetOfGroups.clear()


def process_video_hash(algo: str, hash_size: int, mdc_video_info: MdcVideoInfo):
    ff_info = {}
    try:
        while True:
            if not mdc_video_info["direct_access"]:
                break
            ff_info = ffprobe_get_video_info(mdc_video_info["abs_path"], None)
            if not ff_info:
                break
            if not do_hash_video(algo, hash_size, ff_info, mdc_video_info, mdc_video_info["abs_path"], None):
                raise InvalidVideo
            return
        if mdc_video_info["name"].lower().endswith((".mkv",)):
            return
        data = fs_file_data(mdc_video_info)
        if len(data) == 0:
            return
        ff_info = ffprobe_get_video_info(None, data)
        if not ff_info.get("fast_start", False):
            raise InvalidVideo
        if not do_hash_video(algo, hash_size, ff_info, mdc_video_info, None, data):
            raise InvalidVideo
    except Exception as exception_info:  # noqa # pylint: disable=broad-except
        store_err_video_hash(
            mdc_video_info["id"], ff_info.get("duration", 0), mdc_video_info["mtime"], mdc_video_info["skipped"] + 1
        )
        exception_name = type(exception_info).__name__
        if exception_name != "InvalidVideo":
            log.debug("Exception in video processing:\n%s\n%s", mdc_video_info["internal_path"], str(exception_info))


def do_hash_video(algo: str, hash_size: int, video_info: dict, mdc_video_info: MdcVideoInfo, path, data) -> bool:
    """Accepts path(bytes/str) or data for processing in memory."""

    if video_info["duration"] < MIN_VIDEO_DURATION:
        if video_info["duration"] < 0:
            video_info["duration"] = 0
        return False
    if video_info["duration"] > 24 * 60 * 60 * 1000:  # let's only process videos with duration <= 24 hours.
        video_info["duration"] = 1 + 24 * 60 * 60 * 1000
        return False
    first_timestamp = get_first_timestamp(video_info, path, data)
    if first_timestamp == -1:
        return False
    frames_timestamps = build_times_for_hashes(video_info["duration"], first_timestamp)
    ex = ()
    res = get_frames(frames_timestamps, path, data, *ex)
    if not res[0]:
        return False
    if any(len(x) == 0 for x in res[1:]):
        return False
    hashes_l = [
        calc_hash(algo, hash_size, res[1]),
        calc_hash(algo, hash_size, res[2]),
        calc_hash(algo, hash_size, res[3]),
        calc_hash(algo, hash_size, res[4]),
    ]
    if any(x is None for x in hashes_l):
        return False
    hashes = numpy.concatenate((hashes_l[0], hashes_l[1], hashes_l[2], hashes_l[3]), axis=0)
    hashes_str = arr_hash_to_string(hashes)
    if check_hexstrings_within_dist:
        mdc_video_info["hash"] = hashes_str
    else:
        mdc_video_info["hash"] = hashes
    mdc_video_info["timestamps"] = frames_timestamps
    mdc_video_info["duration"] = video_info["duration"]
    store_video_hash(
        mdc_video_info["id"], video_info["duration"], dumps(frames_timestamps), hashes_str, mdc_video_info["mtime"]
    )
    return True


def build_times_for_hashes(total_duration_ms: int, first_hash_timestamp: int) -> list:
    pre_interval = int((total_duration_ms - first_hash_timestamp) / 10)
    round_factor = len(str(pre_interval)) - 1
    rounded_hash_timestamp = round(pre_interval, ndigits=-round_factor)
    return [first_hash_timestamp, rounded_hash_timestamp, rounded_hash_timestamp * 2, rounded_hash_timestamp * 4]


def get_max_first_frame_time(duration_ms) -> int:
    max_timestamp = int(duration_ms / 10)
    if max_timestamp > 14 * 1000:
        return 14 * 1000
    return max_timestamp


def get_first_timestamp(video_info: dict, path, data) -> int:
    """Accepts path(bytes/str) or data for processing in memory."""
    max_timestamp = get_max_first_frame_time(video_info["duration"])
    ffmpeg_input_params = ["-hide_banner", "-loglevel", "fatal", "-an", "-sn", "-dn", "-to", f"{max_timestamp}ms"]
    if path is not None:
        result, err = stub_call_ff(
            "ffmpeg",
            *ffmpeg_input_params,
            "-i",
            path,
            "-f",
            "rawvideo",
            "-s",
            f"{FIRST_FRAME_RESOLUTION}x{FIRST_FRAME_RESOLUTION}",
            "-pix_fmt",
            "rgb24",
            "pipe:",
        )
    elif data is not None:
        result, err = stub_call_ff(
            "ffmpeg",
            *ffmpeg_input_params,
            "-i",
            "pipe:0",
            "-f",
            "rawvideo",
            "-s",
            f"{FIRST_FRAME_RESOLUTION}x{FIRST_FRAME_RESOLUTION}",
            "-pix_fmt",
            "rgb24",
            "pipe:1",
            stdin_data=data,
        )
    else:
        raise ValueError("`path` or `data` argument must be specified.")
    if err:
        log.debug("get_first_timestamp error: %s", err)
        return -1
    frame_size = FIRST_FRAME_RESOLUTION * FIRST_FRAME_RESOLUTION * 3
    frames_count = int(len(result.stdout) / frame_size)
    frames_per_second = round(frames_count / (max_timestamp / 1000))
    if frames_per_second == 0:
        frames_per_second = 1
    video_info["fps"] = frames_per_second
    for i in range(frames_count):
        if is_frame_too_dark(result.stdout, i, frame_size):
            continue
        if is_frame_too_bright(result.stdout, i, frame_size):
            continue
        return int(i / frames_per_second * 1000)
    return 0


def get_frames(timestamps: list, path, data, *ffmpeg_out_params) -> list:
    """Accepts path(bytes/str) or data for processing in memory."""

    ret: list[Any] = [False]
    for _ in range(len(timestamps)):
        ret.append(b"")
    if path is None and data is None:
        raise ValueError("`path` or `data` argument must be specified.")
    ffmpeg_input_params = ["-hide_banner", "-loglevel", "fatal", "-an", "-sn", "-dn"]
    for index, timestamp in enumerate(timestamps):
        if path is not None:
            result, err = stub_call_ff(
                "ffmpeg",
                *ffmpeg_input_params,
                "-ss",
                f"{timestamp}ms",
                "-i",
                path,
                "-f",
                "image2",
                "-c:v",
                "bmp",
                "-frames",
                "1",
                *ffmpeg_out_params,
                "pipe:",
            )
        else:
            result, err = stub_call_ff(
                "ffmpeg",
                *ffmpeg_input_params,
                "-ss",
                f"{timestamp}ms",
                "-i",
                "pipe:0",
                "-f",
                "image2",
                "-c:v",
                "bmp",
                "-frames",
                "1",
                *ffmpeg_out_params,
                "pipe:1",
                stdin_data=data,
            )
        if err:
            log.debug("get_frames error: %s", err)
            return ret
        ret[index + 1] = result.stdout
    ret[0] = True
    return ret


def is_frame_too_dark(data: bytes, frame_offset: int, frame_size: int) -> bool:
    dark_allow_percent = 80
    total_allowed_dark_pixels = int(((frame_size / 3) / 100) * dark_allow_percent)
    dark_pixels = 0
    frame_bytes = data[frame_size * frame_offset : frame_size * (frame_offset + 1)]
    for pixel_index in range(int(len(frame_bytes) / 3)):
        pixel_data = frame_bytes[pixel_index * 3 : pixel_index * 3 + 3]
        if pixel_data[0] <= 0x20 and pixel_data[1] <= 0x20 and pixel_data[2] <= 0x20:
            dark_pixels += 1
    if dark_pixels > total_allowed_dark_pixels:
        return True
    return False


def is_frame_too_bright(data: bytes, frame_offset: int, frame_size: int) -> bool:
    bright_allow_percent = 90
    total_allowed_bright_pixels = int(((frame_size / 3) / 100) * bright_allow_percent)
    bright_pixels = 0
    frame_bytes = data[frame_size * frame_offset : frame_size * (frame_offset + 1)]
    for pixel_index in range(int(len(frame_bytes) / 3)):
        pixel_data = frame_bytes[pixel_index * 3 : pixel_index * 3 + 3]
        brightness = int(sum([pixel_data[0], pixel_data[1], pixel_data[2]]) / 3)
        if brightness >= 0xFA:
            bright_pixels += 1
    if bright_pixels > total_allowed_bright_pixels:
        return True
    return False


def remove_solo_groups():
    groups_to_remove = []
    for group_key, files_id in VideoGroups.items():
        if len(files_id) == 1:
            groups_to_remove.append(group_key)
    for key in groups_to_remove:
        del VideoGroups[key]


def save_video_results(task_id: int, group_offset: int):
    remove_solo_groups()
    log.debug("Videos: Number of groups: %u", len(VideoGroups))
    n_group = group_offset
    for files_id in VideoGroups.values():
        for file_id in files_id:
            store_task_files_group(task_id, n_group, file_id)
        n_group += 1


def load_videos_caches(images: list[FsNodeInfo]) -> list[MdcVideoInfo]:
    if not images:
        return []
    images = fs_sort_by_id(images)
    cache_records = get_videos_caches([image["id"] for image in images])
    return [images[i] | cache_records[i] for i in range(len(images))]
