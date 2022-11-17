from cloud_py_api import log


def process_task(task_info, forced: bool) -> None:
    """Top Level function. Checks if we can work on task, and if so - start to process it. Called from `main`."""
    log.debug("Processing task: id={%d}, forced={%d}", task_info, forced)
