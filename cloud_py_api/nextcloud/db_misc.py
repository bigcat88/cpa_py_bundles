from datetime import datetime

from .config import CONFIG


class Tables:
    @property
    def storages(self):
        return CONFIG["dbtprefix"] + "storages"

    @property
    def mounts(self):
        return CONFIG["dbtprefix"] + "mounts"

    @property
    def ext_mounts(self) -> str:
        return CONFIG["dbtprefix"] + "external_mounts"

    @property
    def file_cache(self) -> str:
        return CONFIG["dbtprefix"] + "filecache"

    @property
    def mimetypes(self) -> str:
        return CONFIG["dbtprefix"] + "mimetypes"


TABLES = Tables()


def get_time() -> int:
    return int(datetime.now().timestamp())
