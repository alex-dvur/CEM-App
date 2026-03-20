"""Device discovery UI dialog"""
try:
    from .compat import *
    from . import mogdiscover
    from . import mogdevice
except ImportError:
    from compat import *
    import mogdiscover
    import mogdevice

import logging
import threading

logger = logging.getLogger("MOG")


class DiscoverDialog(QtWidgets.QDialog):
    deviceFound = QtCore.Signal(str, str)

    def __init__(self, filter=None, msg=None, timeout=1, parent=None, **kwargs):
        super(DiscoverDialog, self).__init__(parent)
        self.setWindowTitle("MOGLabs Device Discovery")
        self.filter = filter
        self.timeout = timeout
        self.kwargs = kwargs
        self._abort = False
        self._device = None

        layout = QtWidgets.QVBoxLayout(self)
        if msg:
            layout.addWidget(QtWidgets.QLabel(msg))

        self.status = QtWidgets.QLabel("Searching for devices...")
        layout.addWidget(self.status)

        self.device_list = QtWidgets.QListWidget()
        self.device_list.itemDoubleClicked.connect(self._select_item)
        layout.addWidget(self.device_list)

        addr_layout = QtWidgets.QHBoxLayout()
        addr_layout.addWidget(QtWidgets.QLabel("Manual address:"))
        self.addr_edit = QtWidgets.QLineEdit()
        self.addr_edit.setPlaceholderText("IP:port or COM port")
        addr_layout.addWidget(self.addr_edit)
        layout.addLayout(addr_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.connect_btn.clicked.connect(self._connect)
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setMinimumSize(400, 300)
        self.deviceFound.connect(self._add_device)
        self._refresh()

    def _refresh(self):
        self._abort = True
        self.device_list.clear()
        self._abort = False
        self.status.setText("Searching for devices...")
        thread = threading.Thread(target=self._search, daemon=True)
        thread.start()

    def _search(self):
        count = 0
        try:
            for addr, info in mogdiscover.find_usb(self.filter, abort=lambda: self._abort):
                self.deviceFound.emit(addr, info)
                count += 1
            for addr, info in mogdiscover.find_eth(self.filter, abort=lambda: self._abort):
                self.deviceFound.emit(addr, info)
                count += 1
        except Exception as e:
            logger.warning("Discovery error: %s" % e)
        if count == 0:
            self.status.setText("No devices found. Try entering COM port (e.g. COM6) or IP manually.")
        else:
            self.status.setText("Found %d device(s). Double-click or select and Connect." % count)

    def _add_device(self, addr, info):
        self.device_list.addItem("%s - %s" % (addr, info))

    def _select_item(self, item):
        addr = item.text().split(" - ")[0]
        self.addr_edit.setText(addr)
        self._connect()

    def _connect(self):
        addr = self.addr_edit.text().strip()
        if not addr:
            sel = self.device_list.currentItem()
            if sel:
                addr = sel.text().split(" - ")[0]
        if not addr:
            return
        try:
            self._device = mogdevice.MOGDevice(addr, timeout=self.timeout, **self.kwargs)
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Connection Failed", str(e))

    def get_device(self):
        return self._device

    def closeEvent(self, event):
        self._abort = True
        event.accept()


def discover(filter=None, msg=None, timeout=1, **kwargs):
    dlg = DiscoverDialog(filter=filter, msg=msg, timeout=timeout, **kwargs)
    if dlg.exec_() == QtWidgets.QDialog.Accepted:
        return dlg.get_device()
    return None
