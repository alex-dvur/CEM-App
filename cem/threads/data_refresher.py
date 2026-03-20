# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\threads\data_refresher.py
import logging
try:
    from PySide2.QtCore import QObject, Slot, QTimer
except ImportError:
    from PySide6.QtCore import QObject, Slot, QTimer
from cem.utils.typing import *
logger = logging.getLogger(__name__)

class CEMDataRefresher(QObject):
    FRINGES_DIV = 5

    def __init__(self, worker, loop_time_ms=200, mld_div=5, override_alert=False, fzw_loop_ms=25):
        super().__init__()
        self.worker = worker
        self._fringes_counter = 0
        self.cem_query_timer = QTimer()
        self.mld_query_timer = QTimer()
        self.fzw_query_timer = QTimer()
        self.cem_query_timer.setInterval(loop_time_ms)
        self.mld_query_timer.setInterval(loop_time_ms * mld_div)
        self.fzw_query_timer.setInterval(fzw_loop_ms)
        self.cem_query_timer.timeout.connect(self.cem_queries)
        self.mld_query_timer.timeout.connect(self.mld_queries)
        self.fzw_query_timer.timeout.connect(self.fzw_queries)
        self._override_alert = override_alert

    @property
    def alert(self):
        if self._override_alert:
            return False
        return self.worker.mog

    @Slot()
    def cem_queries(self):
        if self.worker.cem:
            try:
                self.worker.get.filter_angle(alert=(self.alert))
            except Exception as E:
                try:
                    logger.exception("Exception occurred during cem_queries.")
                finally:
                    E = None
                    del E

    @Slot()
    def mld_queries(self):
        if self.worker.mld:
            try:
                self.worker.get.mld_data(alert=(self.alert))
            except Exception as E:
                try:
                    logger.exception("Exception occurred during mld_queries.")
                finally:
                    E = None
                    del E

    @Slot()
    def fzw_queries(self):
        if self.worker.fzw or self.worker.hfw:
            try:
                self.worker.get.frequency(alert=(self.alert))
                if not self._fringes_counter:
                    self.worker.get.fringes(alert=(self.alert))
                self._fringes_counter = (self._fringes_counter + 1) % self.FRINGES_DIV
            except Exception as E:
                try:
                    logger.exception("Exception occurred during fzw_queries.")
                finally:
                    E = None
                    del E

# okay decompiling cem/threads/data_refresher.pyc
