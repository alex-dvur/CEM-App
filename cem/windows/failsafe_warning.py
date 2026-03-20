# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\failsafe_warning.py
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
from cem.utils.typing import *
logger = logging.getLogger(__name__)

class CEMFailSafeDialog(MOGDialog):
    __doc__ = "\n    MOGDialog subclass to handle failsafe overrides\n    "

    def __init__(self, cem_app=None):
        super().__init__("CEM Failsafe", parent=cem_app)
        self.cem_app = cem_app
        layout = QVBoxLayout(self)
        label = QLabel()
        label.setText("CEM failsafe override activated. Laser not lasing. Current reduced.")
        layout.addWidget(label)
        hlayout = QHBoxLayout()
        self.override = PushButton("Disable failsafe thread until next boot.")
        hlayout.addWidget(self.override)
        layout.addLayout(hlayout)
        self.override.pressed.connect(self.disable_failsafe)

    @Slot()
    def disable_failsafe(self):
        """
        Slot to override failsafe thread
        """
        self.cem_app.fail_save.override()

# okay decompiling cem/windows/failsafe_warning.pyc
