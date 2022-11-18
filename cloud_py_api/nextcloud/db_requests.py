from .config import CONFIG
from .db_api import execute_fetchall
from .db_misc import TABLES


def get_paths_by_ids(file_ids: list) -> list:
    """For each element of list in file_ids return [path, fileid, storage]. Order of file_ids is not preserved."""

    query = (
        "SELECT path, fileid, storage "
        f"FROM {TABLES.file_cache} "
        f"WHERE fileid IN ({','.join(str(x) for x in file_ids)}) "
        "ORDER BY fileid ASC;"
    )
    return execute_fetchall(query)


def get_storages_info(num_id: int = None) -> list:
    """If num_id is None, return info for all storages.
    Returns list of dicts with: numeric_id,id,available,mount_point,user_id,storage_backend fields."""

    if CONFIG["dbtype"] == "mysql":
        check_ext_mounts_query = f'SHOW TABLES LIKE "{TABLES.ext_mounts}";'
    else:
        check_ext_mounts_query = f"SELECT * FROM pg_catalog.pg_tables WHERE tablename LIKE '{TABLES.ext_mounts}';"
    if execute_fetchall(check_ext_mounts_query):
        query = (
            "SELECT storage.numeric_id, storage.id, storage.available, "
            "mounts.mount_point, mounts.user_id, mounts.root_id, ext_mounts.storage_backend "
            f"FROM {TABLES.storages} AS storage "
            f"LEFT JOIN {TABLES.mounts}  AS mounts "
            "ON storage.numeric_id = mounts.storage_id "
            f"LEFT JOIN {TABLES.ext_mounts} AS ext_mounts "
            "ON mounts.mount_id = ext_mounts.mount_id "
        )
    else:
        query = (
            "SELECT storage.numeric_id, storage.id, storage.available, "
            "mounts.mount_point, mounts.user_id, mounts.root_id "
            f"FROM {TABLES.storages} AS storage "
            f"LEFT JOIN {TABLES.mounts}  AS mounts "
            "ON storage.numeric_id = mounts.storage_id"
        )
    if num_id is None:
        query += " WHERE 1;" if CONFIG["dbtype"] == "mysql" else ";"
    else:
        query += f" WHERE storage.numeric_id = {num_id};"
    return execute_fetchall(query)


def get_mimetype_id(mimetype: str) -> int:
    """For string mimetype returns it number representation."""

    query = f"SELECT id FROM {TABLES.mimetypes} WHERE mimetype = {mimetype};"
    result = execute_fetchall(query)
    if not result:
        return 0
    return result[0]["id"]
