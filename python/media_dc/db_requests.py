import os
from json import loads

from python.nc_py_api import CONFIG, TABLES, execute_commit, execute_fetchall, get_time

from .db_tables import MDC_TABLES


def get_tasks() -> list:
    """Return list of all tasks(each task is a dict)."""

    _where = ""
    if CONFIG["dbtype"] == "mysql":
        _where = " WHERE 1"
    query = (
        "SELECT id, target_directory_ids, exclude_list, collector_settings, files_scanned, "
        "updated_time , finished_time, errors, py_pid "
        f"FROM {MDC_TABLES.tasks}{_where};"
    )
    tasks_list = execute_fetchall(query)
    if CONFIG["dbtype"] == "mysql":
        for task in tasks_list:
            if isinstance(task["exclude_list"], str):
                task["exclude_list"] = loads(task["exclude_list"])
            if isinstance(task["collector_settings"], str):
                task["collector_settings"] = loads(task["collector_settings"])
            if isinstance(task["target_directory_ids"], str):
                task["target_directory_ids"] = loads(task["target_directory_ids"])
    return tasks_list


def lock_task(task_id: int, old_updated_time: int) -> bool:
    """Returns True if task was locked(set py_pid to id of current process, updated_time = current time)."""

    query = (
        f"UPDATE {MDC_TABLES.tasks} "
        f"SET py_pid = {os.getpid()}, finished_time = 0, updated_time = {get_time()}, errors = '' "
        f"WHERE id = {task_id} AND updated_time = {old_updated_time};"
    )
    if execute_commit(query) > 0:
        return True
    return False


def unlock_task(task_id: int) -> None:
    """Set `py_pid` to zero for specified task."""

    query = f"UPDATE {MDC_TABLES.tasks} SET py_pid = 0 WHERE id = {task_id};"
    execute_commit(query)


def finalize_task(task_id: int) -> None:
    """Set `finished_time` to zero for specified task."""

    query = f"UPDATE {MDC_TABLES.tasks} SET finished_time = {get_time()} WHERE id = {task_id};"
    execute_commit(query)


def clear_task_files_scanned_groups(task_id: int) -> int:
    """Prepare task for re-run, cleat count of scanned files."""

    query = f"UPDATE {MDC_TABLES.tasks} SET files_scanned = 0 WHERE id = {task_id};"
    execute_commit(query)
    query = f"DELETE FROM {MDC_TABLES.tasks_details} WHERE task_id = {task_id};"
    return execute_commit(query)


def increase_processed_files_count(task_id: int, count: int) -> None:
    """Increases number of processed files in task."""

    query = f"UPDATE {MDC_TABLES.tasks} SET files_scanned = files_scanned + {count} WHERE id = {task_id};"
    execute_commit(query)


def append_task_error(task_id: int, errors: str, connection_id: int = 0) -> None:
    """Append to `errors` text field a string with error, throw connection with `connection_id`."""

    if CONFIG["dbtype"] == "mysql":
        query = f"UPDATE {MDC_TABLES.tasks} SET errors = CONCAT(errors, %s, '\n') WHERE id = {task_id};"
        execute_commit(query, args=errors, connection_id=connection_id)
    else:
        query = f"UPDATE {MDC_TABLES.tasks} SET errors = errors || %s || '\n' WHERE id = {task_id};"
        execute_commit(query, args=(errors,), connection_id=connection_id)


def set_task_keepalive(task_id: int, connection_id: int = 1) -> None:
    """Update `updated_time` field to current time, throw connection with `connection_id`."""

    query = f"UPDATE {MDC_TABLES.tasks} SET updated_time = {get_time()} WHERE id = {task_id};"
    execute_commit(query, connection_id=connection_id)


def get_remote_filesize_limit() -> int:
    """Return `remote_filesize_limit` value from settings table."""

    query = f"SELECT value FROM {MDC_TABLES.settings} WHERE name='remote_filesize_limit';"
    result = execute_fetchall(query)
    if not result:
        return 0
    if CONFIG["dbtype"] == "mysql" and isinstance(result[0]["value"], str):
        return loads(result[0]["value"])
    return result[0]["value"]


def get_directory_data_image(dir_id: int, dir_mimetype: int, img_mimetype: int, spike_fileid: list) -> list:
    """For dir_id returns list of records with mimetype specified by dir_mimetype or img_mimetype.
    Record(dict) contains: fileid,path,storage,mimetype,size,mtime,encrypted,hash,skipped."""

    mp_query = ""
    if spike_fileid:
        mp_query = f" OR fcache.fileid IN ({','.join(str(x) for x in spike_fileid)})"
    query = (
        "SELECT fcache.fileid, fcache.path, fcache.storage, fcache.mimetype, fcache.size, fcache.mtime, "
        "fcache.encrypted, "
        "imgcache.hash, imgcache.skipped "
        f"FROM {TABLES.file_cache} AS fcache "
        f"LEFT JOIN {MDC_TABLES.photos} AS imgcache "
        "ON fcache.fileid = imgcache.fileid AND fcache.mtime = imgcache.mtime "
        f"WHERE (fcache.parent = {dir_id}{mp_query}) "
        f"AND (fcache.mimetype = {dir_mimetype}"
        f" OR fcache.mimepart = {img_mimetype}"
        " OR fcache.name IN ('.nomedia', '.noimage'));"
    )
    return execute_fetchall(query)


def get_directory_data_video(dir_id: int, dir_mimetype: int, video_mimetype: int, spike_fileid: list) -> list:
    """For dir_id returns list of records with mimetype specified by dir_mimetype or video_mimetype.
    Record(dict) contains: fileid,path,storage,mimetype,size,mtime,encrypted,duration,timestamps,hash,skipped."""

    mp_query = ""
    if spike_fileid:
        mp_query = f" OR fcache.fileid IN ({','.join(str(x) for x in spike_fileid)})"
    query = (
        "SELECT fcache.fileid, fcache.path, fcache.storage, fcache.mimetype, fcache.size, fcache.mtime, "
        "fcache.encrypted, "
        "vcache.duration, vcache.timestamps, vcache.hash, vcache.skipped "
        f"FROM {TABLES.file_cache} AS fcache "
        f"LEFT JOIN {MDC_TABLES.videos} AS vcache "
        "ON fcache.fileid = vcache.fileid AND fcache.mtime = vcache.mtime "
        f"WHERE (fcache.parent = {dir_id}{mp_query}) "
        f"AND (fcache.mimetype = {dir_mimetype}"
        f" OR fcache.mimepart = {video_mimetype}"
        " OR fcache.name IN ('.nomedia', '.noimage'));"
    )
    dirs_list = execute_fetchall(query)
    if CONFIG["dbtype"] == "mysql":
        for each_dir in dirs_list:
            if isinstance(each_dir["timestamps"], str):
                each_dir["timestamps"] = loads(each_dir["timestamps"])
    return dirs_list


def store_task_files_group(task_id: int, group_id: int, file_id: int) -> None:
    """Add to table `task_details` one record with similar files."""

    query = f"INSERT INTO {MDC_TABLES.tasks_details} (task_id,group_id,fileid) VALUES({task_id},{group_id},{file_id});"
    execute_commit(query)


def store_image_hash(fileid: int, image_hash: str, mtime: int) -> None:
    """Sets for fileid `mtime`,`hash`. `skipped` sets to zero."""
    if CONFIG["dbtype"] == "mysql":
        query = (
            f"REPLACE INTO {MDC_TABLES.photos} (fileid,hash,mtime,skipped) VALUES({fileid},0x{image_hash},{mtime},0);"
        )
    else:
        query = (
            f"INSERT INTO {MDC_TABLES.photos} (fileid,hash,mtime,skipped) "
            f"VALUES({fileid},'\\x{image_hash}',{mtime},0) "
            "ON CONFLICT (fileid) DO UPDATE "
            "SET hash = EXCLUDED.hash, "
            "mtime = EXCLUDED.mtime, "
            "skipped = EXCLUDED.skipped;"
        )
    execute_commit(query)


def store_err_image_hash(fileid: int, mtime: int, skipped_count: int) -> None:
    """Sets for fileid `mtime`,`skipped`. For `hash` set const value:`0x00`."""

    if CONFIG["dbtype"] == "mysql":
        query = (
            f"REPLACE INTO {MDC_TABLES.photos} (fileid,hash,mtime,skipped) "
            f"VALUES({fileid},0x00,{mtime},{skipped_count});"
        )
    else:
        query = (
            f"INSERT INTO {MDC_TABLES.photos} (fileid,hash,mtime,skipped) "
            f"VALUES({fileid},'\\x00',{mtime},{skipped_count}) "
            "ON CONFLICT (fileid) DO UPDATE "
            "SET hash = EXCLUDED.hash, "
            "mtime = EXCLUDED.mtime, "
            "skipped = EXCLUDED.skipped;"
        )
    execute_commit(query)


def store_video_hash(fileid: int, duration: int, timestamps: str, video_hash: str, mtime: int) -> None:
    """Sets for fileid `duration`,`timestamps`,`mtime`,`hash`. `skipped` sets to zero."""
    if CONFIG["dbtype"] == "mysql":
        query = (
            f"REPLACE INTO {MDC_TABLES.videos} (fileid,duration,timestamps,hash,mtime,skipped) "
            f"VALUES({fileid},{duration},'{timestamps}',"
            f"0x{video_hash},{mtime},0);"
        )
    else:
        query = (
            f"INSERT INTO {MDC_TABLES.videos} (fileid,duration,timestamps,hash,mtime,skipped) "
            f"VALUES({fileid},{duration},'{timestamps}',"
            f"'\\x{video_hash}',{mtime},0) "
            "ON CONFLICT (fileid) DO UPDATE "
            "SET hash = EXCLUDED.hash, "
            "duration = EXCLUDED.duration, "
            "timestamps = EXCLUDED.timestamps, "
            "mtime = EXCLUDED.mtime, "
            "skipped = EXCLUDED.skipped;"
        )
    execute_commit(query)


def store_err_video_hash(fileid: int, duration: int, mtime: int, skipped_count: int) -> None:
    """Sets for fileid `duration`,`mtime`,`skipped`. For `timestamps` and `hash` set const values:`[0],0x00`."""

    if CONFIG["dbtype"] == "mysql":
        query = (
            f"REPLACE INTO {MDC_TABLES.videos} (fileid,duration,timestamps,hash,mtime,skipped) "
            f"VALUES({fileid},{duration},'[0]',"
            f"0x00,{mtime},{skipped_count});"
        )
    else:
        query = (
            f"INSERT INTO {MDC_TABLES.videos} (fileid,duration,timestamps,hash,mtime,skipped) "
            f"VALUES({fileid},{duration},'[0]',"
            f"'\\x00',{mtime},{skipped_count}) "
            "ON CONFLICT (fileid) DO UPDATE "
            "SET hash = EXCLUDED.hash, "
            "duration = EXCLUDED.duration, "
            "timestamps = EXCLUDED.timestamps, "
            "mtime = EXCLUDED.mtime, "
            "skipped = EXCLUDED.skipped;"
        )
    execute_commit(query)
