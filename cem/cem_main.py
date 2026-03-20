"""
CEM Main Application Window
Reconstructed from decompiled bytecode - some methods are stubs.
"""
import logging
import traceback
from functools import partial
from typing import Dict, Optional

import numpy as np
import mogui as ui
from mogui import MOGDevice
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

_QAction = getattr(QtWidgets, 'QAction', None) or QtGui.QAction

try:
    import mogui.graphs as pg
    from mogui.graphs import LoggerGraph, myAxisItems
except ImportError:
    pg = None
    LoggerGraph = None
    myAxisItems = None

from cem import APP_TITLE, APP_VER, FZW_COLOURS, BACKLOG, Modes, DebugModes
from cem.core import CEMAppGUIScriptCommon
try:
    from cem.core.worker import CEMWorker
except ImportError:
    CEMWorker = None

try:
    from cem.gui import Ui_MainWindow, ServerLabel
except ImportError:
    Ui_MainWindow = None
    ServerLabel = None

from cem.style import LINE_COLOR, font_1, labelStyle_1

try:
    from cem.server import SocketServer
except ImportError:
    SocketServer = None

try:
    from cem.threads import FailSave, CEMDataRefresher, CEMDrift
except ImportError:
    FailSave = CEMDataRefresher = CEMDrift = None

try:
    from cem.windows import (CEMDriftDialog, CEMFailSafeDialog, MLDControlDialog,
                             ScanControlDialog, PhotodiodeViewerDialog,
                             CEMParametersDialog, ToggleResonance)
except ImportError:
    CEMDriftDialog = CEMFailSafeDialog = MLDControlDialog = None
    ScanControlDialog = PhotodiodeViewerDialog = CEMParametersDialog = None
    ToggleResonance = None

logger = logging.getLogger(__name__)


class CEMApp(QtWidgets.QMainWindow):
    debug_mode = DebugModes.none

    def __init__(self, dev=None, cem_sn=None, mog=False, **kwargs):
        super(CEMApp, self).__init__()
        self.dev = dev
        self.cem_sn = cem_sn
        self.mog = mog

        self.setWindowTitle(f"{APP_TITLE} v{APP_VER}")
        self.setMinimumSize(800, 600)

        if self.debug_mode == DebugModes.offline:
            self._init_offline_gui()
        else:
            self._init_gui()

    def _init_offline_gui(self):
        """Initialize GUI in offline mode (no device connected)"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        title_label = QtWidgets.QLabel(f"<h1>{APP_TITLE}</h1>")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        version_label = QtWidgets.QLabel(f"<h3>Version {APP_VER}</h3>")
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(version_label)

        mode_label = QtWidgets.QLabel("<h3><font color='orange'>OFFLINE MODE</font></h3>")
        mode_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(mode_label)

        if self.cem_sn:
            sn_label = QtWidgets.QLabel(f"<p>CEM Serial: {self.cem_sn}</p>")
            sn_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(sn_label)

        info_label = QtWidgets.QLabel(
            "<p>No device connected. Running in offline/demo mode.</p>"
            "<p>Connect a MOGLabs CEM device and restart without --offline flag.</p>"
        )
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        self._create_menu_bar()

        self.statusBar().showMessage("Offline Mode - No device connected")

    def _init_gui(self):
        """Initialize GUI with device connection"""
        if Ui_MainWindow is not None:
            try:
                self.ui = Ui_MainWindow()
                self.ui.setupUi(self)
                self._init_connections()
                return
            except Exception as e:
                logger.warning("Failed to initialize full UI: %s" % e)

        self._init_offline_gui()
        if self.dev is not None:
            self.statusBar().showMessage(f"Connected to {self.dev.connection}")

    def _init_connections(self):
        """Connect UI signals to slots"""
        pass

    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        exit_action = _QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("&Help")
        about_action = _QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_about(self):
        ui.msgbox_about(self, APP_TITLE, "Motorised Cateye Laser Controller", APP_VER,
                        self.dev if hasattr(self, 'dev') else None)

    def closeEvent(self, event):
        logger.info("Application closing")
        if hasattr(self, 'dev') and self.dev is not None:
            try:
                self.dev.close()
            except Exception:
                pass
        event.accept()


class LasingRangeLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(LasingRangeLabel, self).__init__(parent)

    def set_range(self, low, high, units=""):
        self.setText(f"{low:.1f} - {high:.1f} {units}")


class ScanNPeaks(ui.MOGDialog):
    def __init__(self, dev=None, parent=None):
        super(ScanNPeaks, self).__init__("Scan N Peaks", parent)
        self.dev = dev

    def append_frequency(self, freq):
        pass

    def clear(self):
        pass

    def start_scan_n_peaks(self):
        pass
