"""Small Qt5 window for starting/stopping the dataserver.

Compatible with Python 3.10 and PyQt5.
"""

import sys

from PyQt5 import QtCore, QtWidgets

try:
    # Package import, e.g. python -m package.dataserver_window
    from .dataserver_helpers import DATA_DIRECTORY, dataserver_client, run_dataserver
except ImportError:  # pragma: no cover - useful when run as a plain script
    # Script import, e.g. python dataserver_window.py from this directory
    from .dataserver_helpers import DATA_DIRECTORY, dataserver_client, run_dataserver


ALIVE_TIME_MS = 500
SERVER_START_DELAY_MS = 1000


class DataserverWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.client = None
        self.alive_poll = QtCore.QTimer(self)
        self.alive_poll.timeout.connect(self.check_alive)

        self.status_label = QtWidgets.QLabel("Not Running")
        self.start_button = QtWidgets.QPushButton("Start")
        self.exit_button = QtWidgets.QPushButton("Quit")
        self.exit_button.setEnabled(False)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.exit_button)

        contents = QtWidgets.QWidget()
        contents.setLayout(layout)
        self.setCentralWidget(contents)

        self.start_button.clicked.connect(self.start)
        self.exit_button.clicked.connect(self.stop)
        QtWidgets.QApplication.instance().aboutToQuit.connect(self.stop)

    def start(self):
        self.start_button.setEnabled(False)
        self.status_label.setText("Starting...")
        run_dataserver(qt=True)
        QtCore.QTimer.singleShot(SERVER_START_DELAY_MS, self._connect_client)

    def _connect_client(self):
        try:
            self.client = dataserver_client()
            self.alive_poll.start(ALIVE_TIME_MS)
            self.exit_button.setEnabled(True)
            self.check_alive()
        except Exception as exc:
            self.client = None
            self.alive_poll.stop()
            self.status_label.setText(f"Not Running: {exc}")
            self.start_button.setEnabled(True)
            self.exit_button.setEnabled(False)

    # This is somewhat useless now. Keep for multiprocessing.
    def check_alive(self):
        if self.client is None:
            self.status_label.setText("Not Running")
            self.alive_poll.stop()
            self.start_button.setEnabled(True)
            self.exit_button.setEnabled(False)
            return

        try:
            is_alive = self.client.hello() == "hello"
        except Exception:
            is_alive = False

        if is_alive:
            self.status_label.setText("Server running at " + DATA_DIRECTORY)
        else:
            self.status_label.setText("Not Running")
            self.client = None
            self.alive_poll.stop()
            self.start_button.setEnabled(True)
            self.exit_button.setEnabled(False)

    def stop(self):
        self.alive_poll.stop()
        if self.client is not None:
            try:
                self.client.quit()
            except Exception:
                pass
            finally:
                self.client = None

        self.status_label.setText("Not Running")
        self.start_button.setEnabled(True)
        self.exit_button.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = DataserverWindow()
    win.show()
    sys.exit(app.exec_())
