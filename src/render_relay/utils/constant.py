import logging

DEFAULT_SOCK_PATH = "/tmp/gingerjs_unix.sock"

DEFAULT_LOCKFILE = "/tmp/my_subprocess.lock"

level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}