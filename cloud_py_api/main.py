import argparse
import signal
import sys

from cloud_py_api import log
from cloud_py_api.media_dc import get_tasks, process_task
from cloud_py_api.misc import print_versions
from cloud_py_api.nextcloud import CONFIG


def signal_handler(signum=None, _frame=None):
    """Handler for unexpected shutdowns."""

    log.info("Got signal: %u", signum)
    sys.exit(0)


if __name__ == "__main__":
    for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP]:
        signal.signal(sig, signal_handler)
    parser = argparse.ArgumentParser(description="Module for performing objects operations.", add_help=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        dest="mdc_tasks_id",
        type=int,
        action="append",
        help="Process MediaDC task with specified ID. Can be specified multiply times.",
    )
    group.add_argument("--version", dest="version", action="store_true", help="Print versions info.")
    args = parser.parse_args()
    if args.version:
        print_versions()
    elif args.mdc_tasks_id:
        if not CONFIG["valid"]:
            log.error("Unable to parse config or connect to database. Does `occ` works?")
            sys.exit(1)
        tasks_to_process = get_tasks()
        tasks_to_process = list(filter(lambda row: row["id"] in args.mdc_tasks_id, tasks_to_process))
        missing_tasks = list(filter(lambda r: not any(row["id"] == r for row in tasks_to_process), args.mdc_tasks_id))
        for x in missing_tasks:
            log.warning("Cant find task with id=%u", x)
        for i in tasks_to_process:
            process_task(i)
    else:
        parser.print_help()
    sys.exit(0)
