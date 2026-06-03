from dataserver.dataserver_helpers import run_dataserver, dataserver_client, DATA_DIRECTORY
import time
from PyQt5 import QtCore, QtWidgets
import sys

app = QtWidgets.QApplication([])
win = QtWidgets.QMainWindow()
contents = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
contents.setLayout(layout)
status_label = QtWidgets.QLabel("Not Running")
start_button = QtWidgets.QPushButton("Start")
exit_button = QtWidgets.QPushButton("Quit")
exit_button.setEnabled(False)
layout.addWidget(status_label)
layout.addWidget(start_button)
layout.addWidget(exit_button)
win.setCentralWidget(contents)
client = None
alive_poll = None
alive_time = 500


def start():
    run_dataserver(qt=True)
    time.sleep(1)
    global client, alive_poll, start_button, exit_button
    client = dataserver_client()
    alive_poll = QtCore.QTimer()
    alive_poll.timeout.connect(check_alive)
    alive_poll.start(alive_time)
    start_button.setEnabled(False)
    exit_button.setEnabled(True)


# This is somewhat useless now. Keep for multiprocessing
def check_alive():
    global client, alive_poll
    if client.hello() != "hello":
        status_label.setText("Not Running")
        client = None
        alive_poll.stop()
    else:
        status_label.setText("Server running at " + DATA_DIRECTORY)


def stop():
    global client
    if client is not None:
        client.quit()
    start_button.setEnabled(True)
    exit_button.setEnabled(False)


start_button.clicked.connect(start)
exit_button.clicked.connect(stop)
app.lastWindowClosed.connect(stop)
win.show()
sys.exit(app.exec_())
