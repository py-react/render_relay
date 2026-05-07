import logging
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).timestamp()

DEFAULT_SOCK_PATH = f"/tmp/render_relay_unix.sock"

DEFAULT_LOCKFILE = f"/tmp/my_subprocess.lock"

level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}