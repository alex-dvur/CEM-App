"""Firmware update UI - stub for cross-platform compatibility"""
try:
    from .compat import *
except ImportError:
    from compat import *


class FirmwareUI(QtWidgets.QDialog):
    def __init__(self, dev, parent=None, modal=True):
        super(FirmwareUI, self).__init__(parent)
        self.dev = dev
        self.setModal(modal)
        self.setWindowTitle("Firmware Update")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Firmware update not available in this build."))
        btn = QtWidgets.QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
