# lib/server_support/lifeline.py
#
# Lifecycle helpers for the QRLab instrument server and data server.
#
# The two servers are launched as minimised console windows by start.bat:
#   start /min "Instrument Server" start_instrumentserver.bat
#   start /min "Data Server"       start_dataserver.bat
#
# We detect them by window title using `tasklist`, which is the same
# mechanism clear.bat uses for TASKKILL — so title matching is consistent.
#
# Typical usage in create_instruments.py:
#   from lib.server_support.lifeline import clear_servers, start_servers
#   clear_servers()   # kill old sessions, wait until gone
#   start_servers()   # launch fresh, wait until windows appear + init buffer

import logging
import subprocess
import time

logger = logging.getLogger(__name__)

# Root directory of the QRLab installation; bat files live here.
QRLAB_ROOT = r'C:\qrlab-3'

# Console window titles assigned by start.bat (/min "Title").
# Must match the titles used in clear.bat's TASKKILL /FI "WINDOWTITLE eq ..." lines.
SERVER_TITLES = ['Instrument Server', 'Data Server']


def _window_alive(title):
    """Return True if a console window with the given title is currently running.

    Uses `tasklist /FI "WINDOWTITLE eq <title>"`. When no match exists,
    tasklist prints a line containing "No tasks" — any other non-empty
    output means the window is alive.
    """
    r = subprocess.run(
        ['tasklist', '/FI', 'WINDOWTITLE eq ' + title, '/NH'],
        capture_output=True, text=True
    )
    return 'No tasks' not in r.stdout and r.stdout.strip() != ''


def servers_alive():
    """Return True if at least one server window is still running."""
    return any(_window_alive(t) for t in SERVER_TITLES)


def wait_servers_dead(timeout=10, interval=0.25):
    """Poll until all server windows have closed, or until timeout.

    Called after clear.bat so we don't start fresh servers before the old
    ZMQ sockets have fully released. Returns True on clean exit, False on
    timeout (prints a warning and continues either way).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not servers_alive():
            return True
        time.sleep(interval)
    logger.warning('server processes still alive after %.0fs — proceeding anyway' % timeout)
    return False


def wait_servers_alive(timeout=10, interval=0.25):
    """Poll until all server windows have appeared, or until timeout.

    Called after start.bat so we know the processes have at least launched
    before we attempt to connect. Returns True on clean detection, False on
    timeout (prints a warning and continues either way).

    Note: window appearance confirms the bat file started, NOT that the
    Python server has finished initialising its ZMQ sockets. start_servers()
    adds a short fixed buffer after this for that reason.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if servers_alive():
            return True
        time.sleep(interval)
    logger.warning('server processes not detected after %.0fs — proceeding anyway' % timeout)
    return False


def clear_servers():
    """Kill all running instrument/data servers and wait until they are gone."""
    logger.debug('Clearing servers...')
    subprocess.run([r'%s\clear.bat' % QRLAB_ROOT], shell=True)
    wait_servers_dead()


def start_servers():
    """Launch fresh instrument/data servers and wait until they are ready.

    Runs start.bat (which opens minimised console windows for each server),
    waits for the windows to appear, then sleeps a short buffer to allow
    the Python process inside each window to finish importing and binding
    its ZMQ sockets before create_instruments.py connects.
    """
    logger.debug('Starting servers...')
    subprocess.run([r'%s\start.bat' % QRLAB_ROOT], shell=True)
    wait_servers_alive()
    time.sleep(2)   # ZMQ socket init happens after the window appears
