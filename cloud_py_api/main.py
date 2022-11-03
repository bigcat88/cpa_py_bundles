import argparse
import signal
import sys

from cloud_py_api.media_dc import process_task
from cloud_py_api.misc import print_versions


def signal_handler(signum=None, _frame=None):
    """Handler for unexpected shutdowns."""
    print("Got signal:", signum)
    sys.exit(0)


if __name__ == "__main__":
    for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP]:
        signal.signal(sig, signal_handler)
    parser = argparse.ArgumentParser(description="Module for performing objects operations.", add_help=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t",
        dest="mdc_task_id",
        type=int,
        action="append",
        help="Process MediaDC task with specified ID. Can be specified multiply times.",
    )
    group.add_argument("--version", dest="version", action="store_true", help="Print versions info.")
    args = parser.parse_args()
    if args.version:
        print_versions()
    elif args.mdc_task_id:
        process_task(args.mdc_task_id, True)
    else:
        parser.print_help()
    sys.exit(0)
