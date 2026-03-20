# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\threads\drift_monitor.py
import logging
try:
    from PySide2.QtCore import QObject, Signal, Slot, QTimer
except ImportError:
    from PySide6.QtCore import QObject, Signal, Slot, QTimer
from cem.utils.typing import *
logger = logging.getLogger(__name__)

class CEMDrift(QObject):
    __doc__ = "\n    Object to periodically monitor CEM drift and emit signal (drift_detected) if non zero drift detected\n    "
    drift_detected = Signal(int, int)

    def __init__(self, worker, monitor_period_seconds=60):
        super().__init__()
        self.worker = worker
        self.monitor_timer = QTimer(parent=self)
        self.monitor_timer.timeout.connect(self.check_drift)
        self.monitor_timer.setInterval(monitor_period_seconds * 1000)

    @Slot()
    def check_drift(self):
        """
        Read values and emit drift_detected on non zero values
        """
        home_error, homing_error = self.worker.cem.ask("FILT,DRIFT").split(" ")
        home_error, homing_error = int(home_error), int(homing_error)
        if home_error != 0:
            self.drift_detected.emit(home_error, homing_error)

# okay decompiling cem/threads/drift_monitor.pyc
