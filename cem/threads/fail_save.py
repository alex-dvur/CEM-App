"""Fail-safe thread - reconstructed stub"""
import logging
try:
    from PySide2.QtCore import QObject, Signal, Slot, QTimer
except ImportError:
    from PySide6.QtCore import QObject, Signal, Slot, QTimer

logger = logging.getLogger(__name__)


class FailSave(QObject):
    fail_save_activated = Signal()
    threshold_changed = Signal(float)

    def __init__(self, parent=None):
        super(FailSave, self).__init__(parent)
        self._threshold = 0.0
        self._enabled = False
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._check)

    def start(self):
        self._enabled = True
        self._timer.start()
        logger.info("FailSave started")

    def stop(self):
        self._enabled = False
        self._timer.stop()
        logger.info("FailSave stopped")

    def set_threshold(self, threshold):
        self._threshold = threshold
        self.threshold_changed.emit(threshold)

    @Slot()
    def _check(self):
        pass
