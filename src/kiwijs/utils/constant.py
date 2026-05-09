import logging
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).timestamp()

def get_sock_path(app_name: str = "kiwijs") -> str:
    """Returns a per-app Unix socket path so multiple apps don't clash."""
    safe_name = app_name.lower().replace(" ", "_")
    return f"/tmp/{safe_name}_unix.sock"

def get_lockfile(app_name: str = "kiwijs") -> str:
    """Returns a per-app lockfile path."""
    safe_name = app_name.lower().replace(" ", "_")
    return f"/tmp/{safe_name}.lock"

# Legacy fallbacks (app-name-agnostic)
DEFAULT_SOCK_PATH = get_sock_path()
DEFAULT_LOCKFILE = get_lockfile()

level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}