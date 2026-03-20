# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\mld_control.py
import logging
try:
    from PySide2.QtCore import Slot
except ImportError:
    from PySide6.QtCore import Slot
import mogui as ui
from cem.utils.typing import *
from mogui import QtWidgets, QtGui, QtCore
logger = logging.getLogger(__name__)

class MLDControl(QtWidgets.QGroupBox):

    def __init__(self, worker):
        super(MLDControl, self).__init__("MLD control")
        self.worker = worker
        self.worker.got_mld_data.connect(self.got_mld_data)
        self.worker.got_destination_ticks.connect(self.got_destination_ticks)
        self.initUI()
        if self.worker.mld is None:
            logger.info("Reconnect on start up")
            self.reconnect()

    def initUI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.wsettings = QtWidgets.QWidget(self)
        self.wsettings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.wsettings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.wsettings)
        self.Iset = ui.DblSpinner(min=0, max=500, step=0.01, decimals=2, units="mA")
        self.Iset.valueChanged.connect(self.setCurrent)
        form.addRow("Current:", self.Iset)
        self.Ibias = ui.DblSpinner(min=0, max=500, step=0.1, decimals=1, units="mA")
        self.Ibias.valueChanged.connect(self.setBias)
        form.addRow("Bias:", self.Ibias)
        self.span = ui.DblSpinner(min=0, max=100, step=1, decimals=1)
        self.span.valueChanged.connect(self.setSpan)
        form.addRow("Span (%):", self.span)
        self.offset = ui.DblSpinner(min=(-100), max=100, step=0.1, decimals=1)
        self.offset.valueChanged.connect(self.setOffset)
        form.addRow("Offset (%):", self.offset)
        self.frequency = ui.DblSpinner(min=0, max=100, step=0.1, decimals=2, units="Hz")
        self.frequency.valueChanged.connect(self.setFreq)
        self.frequency.setEnabled(True)
        form.addRow("Frequency:", self.frequency)
        self.duty_cycle = ui.DblSpinner(min=0, max=1, step=0.1, decimals=2)
        self.duty_cycle.setEnabled(False)
        form.addRow("Duty cycle:", self.duty_cycle)
        self.pzt = QtWidgets.QCheckBox("Piezo")
        self.pzt.toggled.connect(self.setPzt)
        form.addRow("Piezo:", self.pzt)
        self.bias = QtWidgets.QComboBox(self)
        self.bias.addItems(["Off", "+Ramp", "-Ramp"])
        self.bias.currentIndexChanged[str].connect(self.setBiasMode)
        form.addRow("Bias:", self.bias)
        form.addRow(ui.HLine(self))
        self.Tset = ui.DblSpinner(min=0, max=30, decimals=2, units="C")
        self.Tset.valueChanged.connect(self.setTset)
        form.addRow("Setpoint:", self.Tset)
        self.Tactual = ui.DblSpinner(min=0, max=30, decimals=2, units="C")
        self.Tactual.setReadOnly(True)
        form.addRow("Actual:", self.Tactual)
        self.Tcurrent = ui.DblSpinner(min=(-3), max=3, decimals=2, units="A")
        self.Tcurrent.setReadOnly(True)
        form.addRow("TEC:", self.Tcurrent)
        filter_min = self.worker.device_config.min_encoder
        filter_max = self.worker.device_config.max_encoder
        self.filter_setpoint = ui.IntSpinner(min=filter_min, max=filter_max, units="ticks")
        self.filter_setpoint.valueChanged.connect(self.setFilterSetpoint)
        form.addRow("Filter SP:", self.filter_setpoint)
        form.addRow(ui.HLine(self))
        hb = QtWidgets.QHBoxLayout()
        hb.setContentsMargins(0, 0, 0, 0)
        self.btn_tec = ui.PushButton("Temperature")
        self.btn_tec.pressed.connect(self.toggle_tec)
        hb.addWidget(self.btn_tec)
        self.btn_cur = ui.PushButton("Current")
        self.btn_cur.pressed.connect(self.toggle_current)
        hb.addWidget(self.btn_cur)
        form.addRow(hb)
        form.addRow(ui.HLine(self))
        hb = QtWidgets.QHBoxLayout()
        hb.setContentsMargins(0, 0, 0, 0)
        btn_key_toggle = ui.PushButton("Toggle key switch")
        btn_key_toggle.pressed.connect(self.key_toggle)
        btn_key_toggle.setAutoDefault(False)
        hb.addWidget(btn_key_toggle)
        btn_reconnect = ui.PushButton("Reconnect")
        btn_reconnect.pressed.connect(self.reconnect)
        btn_reconnect.setAutoDefault(False)
        hb.addWidget(btn_reconnect)
        form.addRow(hb)

    def setEnabled(self, val):
        self.wsettings.setEnabled(val)

    def got_mld_data(self, i_set_mA, bias_mA, span, offset, frequency_Hz, duty, t_set_c, temperature_c, i_tec_A, modulation, piezo_status, tec_status, current_status):
        self.Iset.setReading(i_set_mA)
        self.Ibias.setReading(bias_mA)
        self.span.setReading(span * 100)
        self.offset.setReading(offset * 100)
        self.frequency.setReading(frequency_Hz)
        self.duty_cycle.setReading(duty)
        self.Tset.setReading(t_set_c)
        self.Tactual.setReading(temperature_c)
        self.Tcurrent.setReading(i_tec_A)
        p = self.Tactual.palette()
        p.setColor(QtGui.QPalette.Base, ui.COLOR_GOOD if abs(self.Tset.value() - self.Tactual.value()) < 0.02 else ui.COLOR_BAD)
        self.Tactual.setPalette(p)
        with ui.blocked(self.pzt):
            self.pzt.setChecked(piezo_status)
        with ui.blocked(self.bias):
            i = self.bias.findText(modulation[0], QtCore.Qt.MatchStartsWith)
            if i < 0:
                i = 0
            self.bias.setCurrentIndex(i)
        if tec_status:
            self.btn_tec.setStyleSheet("background-color: %s" % ui.COLOR_GOOD)
        else:
            self.btn_tec.setStyleSheet("background-color: %s" % ui.COLOR_BAD)
        if current_status:
            self.btn_cur.setStyleSheet("background-color: %s" % ui.COLOR_GOOD)
        else:
            self.btn_cur.setStyleSheet("background-color: %s" % ui.COLOR_BAD)

    @Slot(int)
    def got_destination_ticks(self, destination):
        self.filter_setpoint.setReading(destination)

    def setDevice(self, dev):
        return

    def closeEvent(self, evt):
        self.worker.got_mld_data.disconnect(self.got_mld_data)
        evt.accept()

    @ui.wrap_except
    def toggle_tec(self):
        if self.worker.mld.ask("TEC,ONOFF") == "ON":
            self.worker.mld.cmd("TEC,OFF")
            self.btn_tec.setStyleSheet("background-color: %s" % ui.COLOR_BAD)
        else:
            self.worker.mld.cmd("TEC,ON")
            self.btn_tec.setStyleSheet("background-color: %s" % ui.COLOR_GOOD)

    @ui.wrap_except
    def toggle_current(self):
        if self.worker.mld.ask("CURRENT,ONOFF") == "ON":
            self.worker.mld.cmd("CURRENT,OFF")
            self.btn_cur.setStyleSheet("background-color: %s" % ui.COLOR_BAD)
        else:
            self.worker.mld.cmd("CURRENT,ON")
            self.btn_cur.setStyleSheet("background-color: %s" % ui.COLOR_GOOD)

    @ui.wrap_except
    def key_toggle(self):
        self.worker.mld.cmd("TOGOVER")

    @ui.wrap_except
    def reconnect(self):
        if self.worker.mld is None:
            self.worker.mld = ui.discoverer.discover(filter="MLD")
            self.setDevice(None)
        else:
            self.worker.mld.reconnect()
            self.setDevice(None)

    @ui.wrap_except
    def setCurrent(self, val):
        self.worker.mld.cmd("CURRENT,ISET,%.2f mA" % val)

    @ui.wrap_except
    def setBias(self, val):
        self.worker.mld.cmd("CURRENT,BIAS,%.2f mA" % val)

    @ui.wrap_except
    def setSpan(self, val):
        self.worker.mld.cmd("RAMP,SPAN,%.3f" % (val / 100))

    @ui.wrap_except
    def setOffset(self, val):
        self.worker.mld.cmd("RAMP,OFFSET,%.3f" % (val / 100))

    @ui.wrap_except
    def setFreq(self, val):
        self.worker.mld.cmd("RAMP,FREQ,%.2f" % val)

    @ui.wrap_except
    def setDuty(self, val):
        self.worker.mld.cmd("RAMP,DUTY,%.2f" % val)

    @ui.wrap_except
    def setPzt(self, val):
        self.worker.mld.cmd("HV,ONOFF,%d" % val)

    @ui.wrap_except
    def setBiasMode(self, val):
        self.worker.mld.cmd("CURRENT,MOD,%s" % val[0])

    @ui.wrap_except
    def setTset(self, val):
        self.worker.mld.cmd("TSET,%.2f" % val)

    @ui.wrap_except
    def setFilterSetpoint(self, val):
        self.worker.cem.cmd(f"FILT,DEST,{val}")


class MLDScans(QtWidgets.QGroupBox):

    def __init__(self, worker, mld_settings):
        super(MLDScans, self).__init__("MLD scans")
        self.worker = worker
        self.mld_settings = mld_settings
        self.initUI()

    def initUI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.wsettings = QtWidgets.QWidget(self)
        self.wsettings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.wsettings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.wsettings)
        self.wsettings.setEnabled(self.worker.mld is not None)
        hb = QtWidgets.QHBoxLayout()
        hb.setContentsMargins(0, 0, 0, 0)
        btn_mode_scan = QtWidgets.QPushButton("Mode scan")
        btn_mode_scan.pressed.connect(self.mode_scan)
        btn_mode_scan.setAutoDefault(False)
        hb.addWidget(btn_mode_scan)
        btn_clear_pd = QtWidgets.QPushButton("Clear PD")
        btn_clear_pd.pressed.connect(self.clear_photodiode)
        btn_clear_pd.setAutoDefault(False)
        hb.addWidget(btn_clear_pd)
        form.addRow(hb)

    @ui.wrap_except
    def mode_scan(self):
        self.worker.queue((self.worker.scans.piezo_mode_scan), move=False,
          bias_mA=(self.mld_settings.Ibias.value()),
          scan_width=(self.mld_settings.span.value()))

    @ui.wrap_except
    def clear_photodiode(self):
        self.worker.cem.cmd("PD,CLEAR")


class MLDControlDialog(ui.MOGDialog):

    def __init__(self, worker, parent=None):
        super(MLDControlDialog, self).__init__("MLD control", parent=parent)
        self.mld_settings = MLDControl(worker=worker)
        self.mld_scans = MLDScans(worker=worker, mld_settings=(self.mld_settings))
        vb = QtWidgets.QVBoxLayout(self)
        vb.addWidget(self.mld_settings)
        vb.addWidget(self.mld_scans)
        self.setFocus()

# okay decompiling cem/windows/mld_control.pyc
