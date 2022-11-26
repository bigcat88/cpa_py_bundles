import argparse
import sys

from nc_py_api import CONFIG

from python.bundle_info import bundle_info
from python.db_requests import get_tasks
from python.log import logger as log
from python.task import process_task

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Module for performing objects operations.", add_help=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        dest="mdc_tasks_id",
        type=int,
        action="append",
        help="Process MediaDC task with specified ID. Can be specified multiply times.",
    )
    group.add_argument(
        "--info", dest="bundle_info", action="store_true", help="Print information about bundled packages."
    )
    args = parser.parse_args()
    if args.bundle_info:
        bundle_info()
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
