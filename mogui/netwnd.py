"""Network configuration window - stub"""
try:
    from .compat import *
except ImportError:
    from compat import *

import logging
logger = logging.getLogger("MOG")


class NetworkConfigDialog(QtWidgets.QDialog):
    def __init__(self, dev=None, parent=None):
        super(NetworkConfigDialog, self).__init__(parent)
        self.dev = dev
        self.setWindowTitle("Network Configuration")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Network configuration dialog."))
        btn = QtWidgets.QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
