# lib/server_support/log_rotate.py
#
# Rotates stdout/stderr logging for the long-running server processes
# (instrument server, data server) and create_instruments.py, keeping only
# the most recent N runs in log/<name>/.

import os
import sys
import time

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_ROOT = os.path.join(_REPO_ROOT, 'log')
INSTRUMENT_SERVER_LOG_ENV = 'QRLAB_INSTRUMENT_SERVER_LOG'
DATA_SERVER_LOG_ENV = 'QRLAB_DATA_SERVER_LOG'


class _Tee:
    """Writes to multiple streams at once (e.g. the real console + a log file)."""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for s in self._streams:
            s.write(data)

    def flush(self):
        for s in self._streams:
            s.flush()

_ATTACHED_LOG_PATHS = set()

def _rotate(log_dir, keep):
    """Delete the oldest log files in <log_dir> until at most <keep>-1 remain."""
    existing = sorted(f for f in os.listdir(log_dir) if f.endswith('.log'))
    excess = len(existing) - (keep - 1)
    for fn in existing[:max(0, excess)]:
        os.remove(os.path.join(log_dir, fn))

def _attach_log_path(log_path):
    if not log_path or log_path in _ATTACHED_LOG_PATHS:
        return None
    log_file = open(log_path, 'a', buffering=1, encoding='utf-8')
    sys.stdout = _Tee(sys.stdout, log_file)
    sys.stderr = _Tee(sys.stderr, log_file)
    _ATTACHED_LOG_PATHS.add(log_path)
    return log_path


def open_log_file_from_env(env_var):
    """Open the log file pointed at by env_var for appending, or return None."""
    log_path = os.environ.get(env_var)
    if not log_path:
        return None
    return open(log_path, 'a', buffering=1, encoding='utf-8')


def attach_log_from_env(env_var):
    return _attach_log_path(os.environ.get(env_var))


def _current_log_path(log_dir):
    return os.path.join(log_dir, 'current.log')


def init_log_rotation(name, keep=5, child_env_var=None):
    """Tee stdout and stderr to a fresh timestamped log file in log/<name>/, keeping
    only the most recent <keep> log files (oldest deleted first).

    Call once near the top of a server entrypoint (instrument server, data
    server, create_instruments.py), before any output.

    Returns the path of the new log file.
    """
    log_dir = os.path.join(LOG_ROOT, name)
    os.makedirs(log_dir, exist_ok=True)
    _rotate(log_dir, keep)

    timestamp_log_path = os.path.join(log_dir, time.strftime('%Y%m%d_%H%M%S') + '.log')
    current_log_path = _current_log_path(log_dir)

    current_log_file = open(current_log_path, 'w', buffering=1, encoding='utf-8')
    timestamp_log_file = open(timestamp_log_path, 'a', buffering=1, encoding='utf-8')
    sys.stdout = _Tee(sys.stdout, timestamp_log_file, current_log_file)
    sys.stderr = _Tee(sys.stderr, timestamp_log_file, current_log_file)
    _ATTACHED_LOG_PATHS.add(timestamp_log_path)
    _ATTACHED_LOG_PATHS.add(current_log_path)
    if child_env_var:
        os.environ[child_env_var] = current_log_path
    return timestamp_log_path
