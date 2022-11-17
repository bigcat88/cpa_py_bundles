from datetime import datetime

from .config import CONFIG


class Table:
    @property
    def storage_table(self):
        return CONFIG["dbtprefix"] + "storages"

    @property
    def mounts_table(self):
        return CONFIG["dbtprefix"] + "mounts"

    @property
    def ext_mounts(self) -> str:
        return CONFIG["dbtprefix"] + "external_mounts"

    @property
    def fs_table(self) -> str:
        return CONFIG["dbtprefix"] + "filecache"

    @property
    def mimetypes_table(self) -> str:
        return CONFIG["dbtprefix"] + "mimetypes"

    @property
    def task(self):
        return CONFIG["dbtprefix"] + "mediadc_tasks"

    @property
    def task_details(self):
        return CONFIG["dbtprefix"] + "mediadc_tasks_details"

    @property
    def image_table(self):
        return CONFIG["dbtprefix"] + "mediadc_photos"

    @property
    def video_table(self):
        return CONFIG["dbtprefix"] + "mediadc_videos"

    @property
    def settings_table(self):
        return CONFIG["dbtprefix"] + "mediadc_settings"


def get_time() -> int:
    return int(datetime.now().timestamp())
