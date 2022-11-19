import signal
import sys

from . import log


def signal_handler(signum=None, _frame=None):
    """Handler for unexpected shutdowns."""

    log.info("Got signal: %u", signum)
    sys.exit(0)


for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP]:
    signal.signal(sig, signal_handler)
