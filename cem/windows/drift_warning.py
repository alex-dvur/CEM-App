# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\drift_warning.py
import logging
try:
    from PySide2.QtCore import Slot
except ImportError:
    from PySide6.QtCore import Slot

try:
    from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
except ImportError:
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from mogui.mogui import MOGDialog, PushButton
logger = logging.getLogger(__name__)

class CEMDriftDialog(MOGDialog):
    __doc__ = "\n    MOGDialog subclass to handle requesting homing\n    "

    def __init__(self, cem_app=None):
        super().__init__("CEM Drift Monitor", parent=cem_app)
        self.cem_app = cem_app
        layout = QVBoxLayout(self)
        label = QLabel()
        label.setText("CEM filter drift detected. Filter homing recommended")
        layout.addWidget(label)
        if self.cem_app.worker.mog:
            self.value_label = QLabel()
            layout.addWidget(self.value_label)
        hlayout = QHBoxLayout()
        self.rehome_button = PushButton("Home filter")
        hlayout.addWidget(self.rehome_button)
        self.disable_button = PushButton("Disable monitor until next home")
        hlayout.addWidget(self.disable_button)
        layout.addLayout(hlayout)
        self.rehome_button.pressed.connect(self.rehome_filter)
        self.disable_button.pressed.connect(self.cem_app.drift.monitor_timer.stop)
        self.disable_button.pressed.connect(self.disable_pressed)

    @Slot()
    def rehome_filter(self):
        """
        Slot to rehome filter
        """
        self.cem_app.worker.move.home()
        self.accept()

    @Slot()
    def disable_pressed(self):
        """
        Close window when disable button pressed. N.B. this signal is also connected to the CEMDrift monitor_drift slot (with False argument)
        which prevents the window from appearing until it is re-enabled
        """
        self.reject()

# okay decompiling cem/windows/drift_warning.pyc
