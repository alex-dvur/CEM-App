# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\scan_control.py
try:
    from PySide2.QtCore import Slot
except ImportError:
    from PySide6.QtCore import Slot
import logging
logger = logging.getLogger(__name__)
import mogui as ui
from cem.utils.typing import *
from mogui import QtWidgets

class ScanControl(QtWidgets.QGroupBox):

    def __init__(self, worker):
        super().__init__("Scan control")
        self.worker = worker
        self.worker.got_angle.connect(self.got_angle)
        self.initUI()

    def initUI(self):
        vb = QtWidgets.QVBoxLayout(self)
        MIN_ANGLE = self.worker.convert.to_angle(self.worker.device_config.min_encoder)
        MAX_ANGLE = self.worker.convert.to_angle(self.worker.device_config.max_encoder)
        self.wsettings = QtWidgets.QWidget(self)
        self.wsettings.setMinimumWidth(200)
        grid = QtWidgets.QGridLayout(self.wsettings)
        grid.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.wsettings)
        grid.addWidget(QtWidgets.QLabel("Angle:"), 1, 2)
        grid.addWidget(QtWidgets.QLabel("Position:"), 1, 3)
        grid.addWidget(QtWidgets.QLabel("Current:"), 2, 1)
        self.current_angle = ui.DblSpinner(min=MIN_ANGLE, max=MAX_ANGLE, step=1, decimals=3, units="°", readonly=True)
        grid.addWidget(self.current_angle, 2, 2)
        self.current_angle_ticks = ui.IntSpinner(min=(self.worker.device_config.min_encoder), max=(self.worker.device_config.max_encoder),
          step=10,
          readonly=True)
        grid.addWidget(self.current_angle_ticks, 2, 3)
        grid.addWidget(QtWidgets.QLabel("Minimum:"), 3, 1)
        self.min_angle = ui.DblSpinner(min=MIN_ANGLE, max=MAX_ANGLE, step=1, decimals=3, default=MIN_ANGLE, units="°")
        self.min_angle.valueChanged.connect(self._got_min_angle)
        grid.addWidget(self.min_angle, 3, 2)
        self.min_angle_ticks = ui.IntSpinner(min=(self.worker.device_config.min_encoder), max=(self.worker.device_config.max_encoder),
          step=10,
          default=(self.worker.device_config.min_encoder))
        self.min_angle_ticks.valueChanged.connect(self._got_min_angle_ticks)
        grid.addWidget(self.min_angle_ticks, 3, 3)
        grid.addWidget(QtWidgets.QLabel("Maximum filter:"), 4, 1)
        self.max_angle = ui.DblSpinner(min=MIN_ANGLE, max=MAX_ANGLE, step=1, decimals=3, default=MAX_ANGLE, units="°")
        self.max_angle.valueChanged.connect(self._got_max_angle)
        grid.addWidget(self.max_angle, 4, 2)
        self.max_angle_ticks = ui.IntSpinner(min=(self.worker.device_config.min_encoder), max=(self.worker.device_config.max_encoder),
          step=10,
          default=(self.worker.device_config.max_encoder))
        self.max_angle_ticks.valueChanged.connect(self._got_max_angle_ticks)
        grid.addWidget(self.max_angle_ticks, 4, 3)
        grid.addWidget(QtWidgets.QLabel("Steps:"), 5, 1)
        self.step = ui.DblSpinner(min=0, max=10, step=0.01, decimals=3, default=0.018, units="°")
        self.step.valueChanged.connect(self._got_step)
        grid.addWidget(self.step, 5, 2)
        self.step_ticks = ui.IntSpinner(min=0, max=10000, step=100, default=10)
        self.step_ticks.valueChanged.connect(self._got_step_ticks)
        grid.addWidget(self.step_ticks, 5, 3)
        grid.addWidget(QtWidgets.QLabel("Piezo:"), 6, 1)
        self.piezo = QtWidgets.QCheckBox("Piezo scan")
        grid.addWidget(self.piezo, 6, 2)
        grid.addWidget(QtWidgets.QLabel("Replicates:"), 7, 1)
        self.replicates = ui.IntSpinner(min=1, default=1)
        grid.addWidget((self.replicates), 7, 2, columnSpan=2)
        vb.addWidget(ui.HLine(self))
        self.btn_home = ui.PushButton("Home filter")
        self.btn_home.pressed.connect(self.go_home)
        vb.addWidget(self.btn_home)
        vb.addWidget(ui.HLine(self))
        self.btn_rapid_scan = ui.PushButton("Rapid filter scan")
        self.btn_rapid_scan.pressed.connect(self.start_rapid_scan)
        vb.addWidget(self.btn_rapid_scan)
        self.btn_detailed_scan = ui.PushButton("Detailed filter scan")
        self.btn_detailed_scan.pressed.connect(self.start_detailed_scan)
        vb.addWidget(self.btn_detailed_scan)
        self.btn_export_scan_data = ui.PushButton("Export scan data")
        self.btn_export_scan_data.pressed.connect(self.save_data)
        vb.addWidget(self.btn_export_scan_data)
        vb.addWidget(ui.HLine(self))
        self.btn_calibration_scan = ui.PushButton("Run calibration scan")
        self.btn_calibration_scan.pressed.connect(self.start_calibration_scan)
        vb.addWidget(self.btn_calibration_scan)
        self.btn_load_calibration = ui.PushButton("Load calibration data")
        self.btn_load_calibration.pressed.connect(self.load_calibration)
        vb.addWidget(self.btn_load_calibration)
        self.btn_export_calibration = ui.PushButton("Export calibration data")
        self.btn_export_calibration.pressed.connect(self.save_calibration)
        vb.addWidget(self.btn_export_calibration)

    @Slot()
    def got_angle(self, filter_angle, destination=None):
        self.current_angle.setValue(filter_angle)
        self.current_angle_ticks.setValue(self.worker.convert.to_encoder_ticks(filter_angle))

    @Slot()
    def _got_min_angle(self, value):
        self.min_angle_ticks.setValue(self.worker.convert.to_encoder_ticks(value))

    @Slot()
    def _got_min_angle_ticks(self, value):
        self.min_angle.setValue(self.worker.convert.to_angle(value))

    @Slot()
    def _got_max_angle(self, value):
        self.max_angle_ticks.setValue(self.worker.convert.to_encoder_ticks(value))

    @Slot()
    def _got_max_angle_ticks(self, value):
        self.max_angle.setValue(self.worker.convert.to_angle(value))

    @Slot()
    def _got_step(self, value):
        self.step_ticks.setValue(self.worker.convert.to_encoder_ticks(value))

    @Slot()
    def _got_step_ticks(self, value):
        self.step.setValue(self.worker.convert.to_angle(value))

    def move_absolute(self):
        """
        @deprecated
        @return:
        """
        return

    @ui.wrap_except
    def go_home(self):
        self.worker.move.home()

    @ui.wrap_except
    def start_rapid_scan(self):
        self.worker.got_plot_y_range.emit(0, 0)
        self.worker.queue(self.worker.scans.rapid)

    @ui.wrap_except
    def start_detailed_scan(self, **kwargs):
        self.worker.got_plot_y_range.emit(self.min_angle.value(), self.max_angle.value())
        (self.worker.queue)(self.worker.scans.filter_position, encoder_start=self.min_angle_ticks.value(), 
         encoder_stop=self.max_angle_ticks.value(), 
         encoder_step=self.step_ticks.value(), 
         piezo_scan=self.piezo.isChecked(), 
         replicates=self.replicates.value(), **kwargs)

    @ui.wrap_except
    def save_data(self, filename=None):
        if filename is None:
            filename = ui.file_dialog(self, "Save measurement data file", "*.p", False, initial="measurement_data.p")
            if filename is None:
                return
        self.worker.data.save(filename=filename)

    @ui.wrap_except
    def start_calibration_scan(self, **kwargs):
        self.worker.got_plot_x_range.emit(self.min_angle.value(), self.max_angle.value())
        (self.worker.queue)(self.worker.scans.calibration, encoder_start=self.min_angle_ticks.value(), 
         encoder_stop=self.max_angle_ticks.value(), 
         encoder_step=self.step_ticks.value(), 
         replicates=self.replicates.value(), **kwargs)

    @ui.wrap_except
    def load_calibration(self, filename=None):
        if filename is None:
            filename = ui.file_dialog(self,
              caption="Load calibration file", filter="*.p", readonly=True, initial="calibration_data.p")
            if filename is None:
                return
        self.worker.data.load(filename=filename)

    @ui.wrap_except
    def save_calibration(self, filename=None):
        if filename is None:
            filename = ui.file_dialog(self,
              caption="Save calibration file", filter="*.p", readonly=False, initial="calibration_data.p")
            if filename is None:
                return
        self.worker.data.save(filename=filename, data=(self.worker.calibration_data))


class ScanControlDialog(ui.MOGDialog):

    def __init__(self, worker, parent=None):
        super().__init__("Scan Control", parent=parent)
        self.scan_control = ScanControl(worker=worker)
        vb = QtWidgets.QVBoxLayout(self)
        vb.addWidget(self.scan_control)
        self.setFocus()

# okay decompiling cem/windows/scan_control.pyc
