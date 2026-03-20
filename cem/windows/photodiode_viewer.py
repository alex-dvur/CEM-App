# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\photodiode_viewer.py
import numpy as np, logging, mogui as ui
from cem.core.single_mode_finder import stable_regions
from cem.utils.typing import *
from cem.windows.mld_control import MLDControl
from mogui import QtWidgets, QtCore
from mogui.graphs import pg
logger = logging.getLogger(__name__)

class SingleModeFinderGraph(pg.GraphicsLayoutWidget):

    def __init__(self, graph_size=(1000, 1000)):
        super(SingleModeFinderGraph, self).__init__()
        self.graph_size = graph_size
        self.n_regions = 16
        self.p1 = self.addPlot(row=1, col=1)
        self.p1.enableAutoRange()
        self.p1.setLabels(left="External photodiode")
        self.scan_ext_pd = self.p1.plot(pen=(pg.mkPen("#00f")), name="External photodiode")
        self.scan_ext_pd_backward = self.p1.plot(pen=(pg.mkPen("#f00")), name="ext_pd_backward")
        self.bestzone_ext = pg.LinearRegionItem(movable=False, pen=pg.mkPen("#080", w=2), brush=(pg.mkBrush("#0802")))
        self.p1.addItem(self.bestzone_ext)
        self.bestzone_ext.hide()
        self.haltline = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen("#0008", dashing=(2,
                                                                                               2)))
        self.p1.addItem(self.haltline)
        self.p2 = self.addPlot(row=2, col=1)
        self.p2.enableAutoRange()
        self.p2.setLabels(left="Internal photodiode")
        self.scan_int_pd = self.p2.plot(pen=(pg.mkPen("#80f")), name="Internal photodiode")
        self.scan_int_pd_backward = self.p2.plot(pen=(pg.mkPen("#f80")), name="int_pd_backward")
        self.bestzone_int = pg.LinearRegionItem(movable=False, pen=pg.mkPen("#080", w=2), brush=(pg.mkBrush("#0802")))
        self.p2.addItem(self.bestzone_int)
        self.bestzone_int.hide()
        self.p2.setXLink(self.p1)
        self.p2.hide()
        self.p3 = self.addPlot(row=3, col=1)
        self.p3.enableAutoRange()
        self.p3.setLabels(left="Mode finder")
        self.p3.addLegend(offset=(10, 10))
        self.badzones = [pg.LinearRegionItem(movable=False, pen=pg.mkPen("#f00", w=2), brush=(pg.mkBrush("#f002"))) for i in range(self.n_regions)]
        for G in self.badzones:
            self.p3.addItem(G)
        else:
            self.derivative_ext_pd = self.p3.plot(pen=(pg.mkPen("#00f")), name="derivative_ext_pd")
            self.normalized_std_ext_pd = self.p3.plot(pen=(pg.mkPen("#f0f")), name="normalized_std_ext_pd")
            self.derivative_int_pd = self.p3.plot(pen=(pg.mkPen("#009")), name="derivative_int_pd")
            self.normalized_std_int_pd = self.p3.plot(pen=(pg.mkPen("#909")), name="normalized_std_int_pd")
            self.p3.setXLink(self.p2)

    def find_stable_regions_and_plot(self, ext_pd, int_pd, mode_detection):
        centres, widths, mode_finder_raw_data = stable_regions(ext_pd=ext_pd,
          int_pd=int_pd,
          mode_detection=mode_detection,
          split_scan=True)
        self.plot(ext_pd=ext_pd, int_pd=int_pd, centres=centres, widths=widths, mode_finder_raw_data=mode_finder_raw_data,
          n_derivative=(mode_detection["n_derivative"]))

    def plot(self, ext_pd, int_pd, centres, widths, mode_finder_raw_data, n_derivative):
        normalized_x_axis = np.linspace(0, 1, len(ext_pd))
        self.p1.enableAutoRange()
        self.scan_ext_pd.setData(normalized_x_axis, ext_pd)
        self.scan_ext_pd_backward.setData()
        self.scan_int_pd.setData(normalized_x_axis, int_pd)
        self.scan_int_pd_backward.setData()
        self.derivative_ext_pd.setData(normalized_x_axis, mode_finder_raw_data["derivative_ext_pd"] * 100)
        self.normalized_std_ext_pd.setData(normalized_x_axis, mode_finder_raw_data["normalized_std_ext_pd"] * 100)
        self.derivative_int_pd.setData(normalized_x_axis, mode_finder_raw_data["derivative_int_pd"] * 100)
        self.normalized_std_int_pd.setData(normalized_x_axis, mode_finder_raw_data["normalized_std_int_pd"] * 100)
        scaling_factor = 1 / len(ext_pd)
        for (i, j), R in zip(mode_finder_raw_data["bad_region_blocks"], self.badzones):
            R.setRegion(((i - n_derivative) * scaling_factor, (j + n_derivative) * scaling_factor))
            R.show()
        else:
            for R in self.badzones[len(mode_finder_raw_data["bad_region_blocks"]):]:
                R.hide()
            else:
                if len(widths):
                    i = np.argmax(widths)
                    bestzone = (
                     centres[i] - widths[i] / 2, centres[i] + widths[i] / 2)
                    self.bestzone_ext.setRegion((bestzone[0], bestzone[1]))
                    self.bestzone_int.setRegion((bestzone[0], bestzone[1]))
                    self.bestzone_ext.show()
                    self.bestzone_int.show()
                else:
                    self.bestzone_ext.hide()
                    self.bestzone_int.hide()


class PhotodiodeViewerDialog(ui.MOGDialog):

    def __init__(self, worker, parent=None):
        super(PhotodiodeViewerDialog, self).__init__("CEM photodiode viewer", parent=parent)
        self.worker = worker
        self.worker.got_mode_scan.connect(self.got_mode_scan)
        self.worker.got_angle.connect(self.got_angle)
        self.graph_size = [
         1000, 1000]
        self.init_ui()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.mode_scan)
        self.timer.start(1000)
        self.resize(200 + self.graph_size[0], self.graph_size[1])
        self.setFocus()
        self.resume_scan()
        self.mode_scan()

    def init_ui(self):
        hb = QtWidgets.QHBoxLayout(self)
        vb = QtWidgets.QVBoxLayout()
        hb.addLayout(vb, stretch=0)
        general = QtWidgets.QGroupBox("General settings")
        vb.addWidget(general)
        form = QtWidgets.QFormLayout(general)
        self.continuous_scan = QtWidgets.QCheckBox("Continuous scan")
        self.continuous_scan.setChecked(False)
        form.addRow("", self.continuous_scan)
        self.hysteresis_view = QtWidgets.QCheckBox("Hysteresis view (obsolete)")
        self.hysteresis_view.setChecked(False)
        form.addRow("", self.hysteresis_view)
        motor = QtWidgets.QGroupBox("Motor")
        vb.addWidget(motor)
        form = QtWidgets.QFormLayout(motor)
        self.filter_angle = ui.DblSpinner(min=(-10), max=30, step=0.1, decimals=3)
        self.filter_angle.valueChanged.connect(self.move_motor)
        form.addRow("Filter angle", self.filter_angle)
        btn = QtWidgets.QPushButton("Home")
        btn.pressed.connect(self.home_motor)
        btn.setAutoDefault(False)
        form.addRow("", btn)
        settings = QtWidgets.QGroupBox("Single mode finder settings")
        vb.addWidget(settings)
        form = QtWidgets.QFormLayout(settings)
        self.pd_rate = QtWidgets.QSpinBox(self)
        self.pd_rate.setValue(self.worker.cem.ask_val("PD,RATE", type=int))
        self.pd_rate.setEnabled(False)
        form.addRow("Photodiode rate", self.pd_rate)
        self.n_derivative = QtWidgets.QSpinBox(self)
        self.n_derivative.setValue(self.worker.parameters["mode_detection"]["n_derivative"])
        form.addRow("Derivative block", self.n_derivative)
        self.max_derivative = ui.DblSpinner(min=0, max=100)
        self.max_derivative.setValue(self.worker.parameters["mode_detection"]["max_derivative"])
        form.addRow("Derivative limit", self.max_derivative)
        self.n_std = QtWidgets.QSpinBox(self)
        self.n_std.setValue(self.worker.parameters["mode_detection"]["n_std"])
        form.addRow("Std block", self.n_std)
        self.max_std = ui.DblSpinner(min=0, max=100)
        self.max_std.setValue(self.worker.parameters["mode_detection"]["max_std"])
        form.addRow("Std limit", self.max_std)
        self.join_block = QtWidgets.QSpinBox(self)
        self.join_block.setValue(self.worker.parameters["mode_detection"]["n_join"])
        form.addRow("Join blocks", self.join_block)
        self.mld_settings = MLDControl(worker=(self.worker))
        vb.addWidget(self.mld_settings)
        btn = QtWidgets.QPushButton("Clear PD")
        btn.pressed.connect(self.clear_photodiode)
        btn.setAutoDefault(False)
        vb.addWidget(btn)
        btn = QtWidgets.QPushButton("Halt up")
        btn.pressed.connect(self.halt_scan)
        btn.setAutoDefault(False)
        vb.addWidget(btn)
        btn = QtWidgets.QPushButton("Halt down")
        btn.pressed.connect(self.halt_scan)
        btn.setAutoDefault(False)
        vb.addWidget(btn)
        btn = QtWidgets.QPushButton("Resume")
        btn.pressed.connect(self.resume_scan)
        btn.setAutoDefault(False)
        vb.addWidget(btn)
        vb.addStretch()
        self.mode_finder_graph = SingleModeFinderGraph()
        hb.addWidget((self.mode_finder_graph), stretch=1)

    def closeEvent(self, evt):
        self.continuous_scan.setChecked(False)
        ui.MOGDialog.closeEvent(self, evt)

    def mode_scan(self):
        if self.worker.action is None:
            if self.continuous_scan.isChecked():
                self.worker.queue((self.worker.scans.piezo_mode_scan), move=False,
                  bias_mA=(self.mld_settings.Ibias.value()),
                  scan_width=(self.mld_settings.span.value() / 100))

    @ui.wrap_except
    def clear_photodiode(self):
        self.worker.cem.cmd("PD,CLEAR")

    @ui.wrap_except
    def move_motor(self, val):
        self.worker.cem.cmd("MOTOR,DEST,%.3f" % (val * self.worker.device_config.motor_encoder_factor))

    @ui.wrap_except
    def home_motor(self):
        self.worker.cem.cmd("MOTOR,HOME")

    @ui.wrap_except
    def set_decimation(self, val):
        self.worker.cem.ask("PD,RATE,%d" % val)

    def got_angle(self, pos, dest, speed, pmin, pmax):
        self.filter_angle.setReading(pos)

    def got_mode_scan(self):
        mode_detection = {'n_derivative':(self.n_derivative.value)(), 
         'n_std':(self.n_std.value)(), 
         'n_join':(self.join_block.value()) * (self.n_derivative.value()), 
         'max_derivative':(self.max_derivative.value)(), 
         'max_std':(self.max_std.value)(), 
         'min_mode_width':self.worker.parameters["mode_detection"]["min_mode_width"]}
        if self.hysteresis_view.isChecked():
            frequency = self.mld_settings.frequency.value()
            duty_cycle = self.mld_settings.duty_cycle.value()
            rate = 164000.0 / 2 ** self.pd_rate.value()
            nscan = int(rate / frequency / 2)
            nup = int(nscan * duty_cycle)
            nup = int(pow(2, np.floor(np.log(nup) / np.log(2))))
            ndown = nscan - nup
            ndata = len(self.worker.scans.ext_pd)
            if nup > ndata:
                nup = ndata
                ndown = 0
            else:
                if nup + ndown > ndata:
                    ndown = ndata - nup
                else:
                    tup = np.arange(nup) * (1000.0 / rate)
                    tdown = np.arange(ndown) * (1000.0 / rate)
                    self.mode_finder_graph.scan_ext_pd.setData(tup, self.worker.scans.ext_pd[:nup])
                    self.mode_finder_graph.scan_ext_pd_backward.setData(tdown, self.worker.scans.ext_pd[nup:nscan][::-1])
                    self.mode_finder_graph.scan_int_pd.setData(tup, self.worker.scans.int_pd[:nup])
                    self.mode_finder_graph.scan_int_pd_backward.setData(tdown, self.worker.scans.int_pd[nup:nscan][::-1])
                    ext_pd = self.worker.scans.ext_pd[:nup]
                    int_pd = self.worker.scans.int_pd[:nup]
                    split_scan = False
                    centres, widths, mode_finder_raw_data = stable_regions(ext_pd=ext_pd,
                      int_pd=int_pd,
                      mode_detection=mode_detection,
                      split_scan=split_scan)
                    self.mode_finder_graph.derivative_ext_pd.setData(mode_finder_raw_data["derivative_ext_pd"] * 100)
                    self.mode_finder_graph.normalized_std_ext_pd.setData(mode_finder_raw_data["normalized_std_ext_pd"] * 100)
                    self.mode_finder_graph.derivative_int_pd.setData(mode_finder_raw_data["derivative_int_pd"] * 100)
                    self.mode_finder_graph.normalized_std_int_pd.setData(mode_finder_raw_data["normalized_std_int_pd"] * 100)
                    scaling_factor_best = 50.0 / nup
                    scaling_factor_bad = 1
                    for (i, j), R in zip(mode_finder_raw_data["bad_region_blocks"], self.mode_finder_graph.badzones):
                        R.setRegion(((i - mode_detection["n_derivative"]) * scaling_factor_bad,
                         (j + mode_detection["n_derivative"]) * scaling_factor_bad))
                        R.show()
                    else:
                        for R in self.mode_finder_graph.badzones[len(mode_finder_raw_data["bad_region_blocks"]):]:
                            R.hide()
                        else:
                            if len(widths):
                                i = np.argmax(widths)
                                bestzone = (
                                 centres[i] - widths[i] / 2, centres[i] + widths[i] / 2)
                                self.mode_finder_graph.bestzone_ext.setRegion((bestzone[0] * scaling_factor_best,
                                 bestzone[1] * scaling_factor_best))
                                self.mode_finder_graph.bestzone_int.setRegion((bestzone[0] * scaling_factor_best,
                                 bestzone[1] * scaling_factor_best))
                                self.mode_finder_graph.bestzone_ext.show()
                                self.mode_finder_graph.bestzone_int.show()
                            else:
                                self.mode_finder_graph.bestzone_ext.hide()
                                self.mode_finder_graph.bestzone_int.hide()

        else:
            self.mode_finder_graph.find_stable_regions_and_plot(ext_pd=(self.worker.scans.ext_pd), int_pd=(self.worker.scans.int_pd),
              mode_detection=mode_detection)

    @ui.wrap_except
    def halt_scan(self):
        pos = 0.5 * self.haltline.value() / 50
        if "down" in self.sender().text():
            pos = 1 - pos
        logger.debug(f"Pos in halt scan: {pos}")
        self.worker.mld.cmd("RAMP,HALT,%.4f" % pos)

    @ui.wrap_except
    def resume_scan(self):
        self.worker.mld.cmd("RAMP,RESUME")


if __name__ == "__main__":
    ui.cmdline_start(PhotodiodeViewerDialog, filter="CEM")

# okay decompiling cem/windows/photodiode_viewer.pyc
