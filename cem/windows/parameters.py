# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\parameters.py
import os, logging
logger = logging.getLogger(__name__)
import mogui
from cem import SupportedWavemeters
from cem.utils.typing import *
from mogui import QtWidgets, QtCore

class CEMParameterGroup:
    __doc__ = "\n    Abstract base class for a parameter group\n    N.B. this class is essentially an Abstract Base Class. However, it is designed to use\n    with a class which will subclass QtWidgets.<X> that implements its own ABC somewhere. Because of this, we can either\n    make this class an ABC and use virtual subclassing through MyABC.register, or just make this class pretend to be ABC without\n    actually being one. The second option is more useful for sharing of common methods i.e. __init__ so will go with this.\n    "

    def __init__(self, title, worker):
        super().__init__(title)
        self.worker = worker
        self.init_UI()

    def init_UI(self):
        """
        Initialise the GUI layout of the class
        Abt
        """
        raise NotImplementedError("init_UI method must be overridden in subclass")

    def refresh_group(self):
        """
        Refresh the content contained in the group
        """
        raise NotImplementedError("refresh_group method must be overridden in subclass")

    def save_group(self):
        """
        Save the content contained in the group
        """
        raise NotImplementedError("save_group method must be overridden in subclass")


class CEMDelayParameters(CEMParameterGroup, QtWidgets.QGroupBox):

    def init_UI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.w_delay_settings = QtWidgets.QWidget(self)
        self.w_delay_settings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.w_delay_settings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.w_delay_settings)
        self.loop = mogui.DblSpinner(min=0, max=99, step=0.01, decimals=1, units="s")
        form.addRow("Loop:", self.loop)
        self.hold_loop = mogui.DblSpinner(min=0, max=99, step=0.01, decimals=1, units="s")
        form.addRow("Hold loop:", self.hold_loop)
        form.addRow(mogui.HLine(self))
        self.pre_replicate = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Pre replicate:", self.pre_replicate)
        self.post_move_filter = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post move filter:", self.post_move_filter)
        self.post_move_piezo = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post move piezo:", self.post_move_piezo)
        self.post_current_change = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post current change:", self.post_current_change)
        self.post_small_current_change = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post small cur. change:", self.post_small_current_change)
        self.post_start_piezo_scan = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post start piezo scan:", self.post_start_piezo_scan)
        form.addRow(mogui.HLine(self))
        self.post_fzw_error = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post FZW error:", self.post_fzw_error)
        self.post_cem_error = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Post CEM error:", self.post_cem_error)
        self.unstable_modes = mogui.DblSpinner(min=0, max=99, step=0.1, decimals=1, units="s")
        form.addRow("Unstable modes:", self.unstable_modes)
        form.addRow(mogui.HLine(self))
        self.post_TEC_turn_on = mogui.IntSpinner(min=0, max=99, step=1, units="s")
        form.addRow("Post TEC turn on:", self.post_TEC_turn_on)

    def refresh_group(self):
        """
        Refresh the content contained in the group
        """
        self.loop.setValue(self.worker.parameters["delays"]["loop"])
        self.hold_loop.setValue(self.worker.parameters["delays"]["hold_loop"])
        self.pre_replicate.setValue(self.worker.parameters["delays"]["pre_replicate"])
        self.post_move_filter.setValue(self.worker.parameters["delays"]["post_move_filter"])
        self.post_move_piezo.setValue(self.worker.parameters["delays"]["post_move_piezo"])
        self.post_current_change.setValue(self.worker.parameters["delays"]["post_current_change"])
        self.post_small_current_change.setValue(self.worker.parameters["delays"]["post_small_current_change"])
        self.post_start_piezo_scan.setValue(self.worker.parameters["delays"]["post_start_piezo_scan"])
        self.post_fzw_error.setValue(self.worker.parameters["delays"]["post_fzw_error"])
        self.post_cem_error.setValue(self.worker.parameters["delays"]["post_cem_error"])
        self.unstable_modes.setValue(self.worker.parameters["delays"]["unstable_modes"])
        self.post_TEC_turn_on.setValue(self.worker.parameters["delays"]["post_TEC_turn_on"])

    def save_group(self):
        """
        Save the content contained in the group
        """
        delays = {'loop':(self.loop.value)(), 
         'hold_loop':(self.hold_loop.value)(), 
         'post_move_filter':(self.post_move_filter.value)(), 
         'post_move_piezo':(self.post_move_piezo.value)(), 
         'pre_replicate':(self.pre_replicate.value)(), 
         'post_current_change':(self.post_current_change.value)(), 
         'post_small_current_change':(self.post_small_current_change.value)(), 
         'post_start_piezo_scan':(self.post_start_piezo_scan.value)(), 
         'post_fzw_error':(self.post_fzw_error.value)(), 
         'post_cem_error':(self.post_cem_error.value)(), 
         'unstable_modes':(self.unstable_modes.value)(), 
         'post_TEC_turn_on':(self.post_TEC_turn_on.value)()}
        self.worker.parameters["delays"].update(delays)


class CEMModeDetectionParameters(CEMParameterGroup, QtWidgets.QGroupBox):

    def init_UI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.w_mode_detection_settings = QtWidgets.QWidget(self)
        self.w_mode_detection_settings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.w_mode_detection_settings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.w_mode_detection_settings)
        self.n_derivative = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_derivative:", self.n_derivative)
        self.n_std = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_std:", self.n_std)
        self.n_join = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_join:", self.n_join)
        self.max_derivative = mogui.DblSpinner(min=0, max=99, step=0.01, decimals=3, units="")
        form.addRow("max_derivative:", self.max_derivative)
        self.max_std = mogui.DblSpinner(min=0, max=99, step=0.01, decimals=3, units="")
        form.addRow("max_std:", self.max_std)
        self.min_mode_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("min_mode_width:", self.min_mode_width)
        self.max_diff_area = mogui.DblSpinner(min=0, max=999, step=0.1, decimals=1, units="")
        form.addRow("max_diff_area:", self.max_diff_area)
        form.addRow(mogui.HLine(self))
        self.diode_mode_width_GHz = mogui.DblSpinner(min=0, max=99, step=1, decimals=2, units="GHz")
        form.addRow("Diode mode width:", self.diode_mode_width_GHz)

    def refresh_group(self):
        """
        Update all fields in the group
        """
        self.n_derivative.setValue(self.worker.parameters["mode_detection"]["n_derivative"])
        self.n_std.setValue(self.worker.parameters["mode_detection"]["n_std"])
        self.n_join.setValue(self.worker.parameters["mode_detection"]["n_join"])
        self.max_derivative.setValue(self.worker.parameters["mode_detection"]["max_derivative"])
        self.max_std.setValue(self.worker.parameters["mode_detection"]["max_std"])
        self.min_mode_width.setValue(self.worker.parameters["mode_detection"]["min_mode_width"])
        self.max_diff_area.setValue(self.worker.parameters["mode_detection"]["max_diff_area"])
        self.diode_mode_width_GHz.setValue(self.worker.parameters["mode_detection"]["diode_mode_width_GHz"])

    def save_group(self):
        """
        Save all fields in the group
        """
        mode_detection = {'n_derivative':(self.n_derivative.value)(), 
         'n_std':(self.n_std.value)(), 
         'n_join':(self.n_join.value)(), 
         'max_derivative':(self.max_derivative.value)(), 
         'max_std':(self.max_std.value)(), 
         'min_mode_width':(self.min_mode_width.value)(), 
         'max_diff_area':(self.max_diff_area.value)(), 
         'diode_mode_width_GHz':(self.diode_mode_width_GHz.value)()}
        self.worker.parameters["mode_detection"].update(mode_detection)


class CEMCalibrationParameters(CEMParameterGroup, QtWidgets.QGroupBox):

    def init_UI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.w_calibration_settings = QtWidgets.QWidget(self)
        self.w_calibration_settings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.w_calibration_settings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.w_calibration_settings)
        self.default_current_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]),
          step=1,
          decimals=1,
          units="mA")
        form.addRow("Default current:", self.default_current_mA)
        self.current_step_mA = mogui.DblSpinner(min=0, max=100, step=1, decimals=1, units="mA")
        form.addRow("Current step:", self.current_step_mA)
        self.n_steps = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_steps:", self.n_steps)
        self.encoder_step = mogui.IntSpinner(min=0, max=9999, step=1, units="")
        form.addRow("Encoder step:", self.encoder_step)
        self.n_replicates = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_replicates:", self.n_replicates)
        form.addRow(mogui.HLine(self))
        self.scan_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=2, units="")
        form.addRow("Scan width:", self.scan_width)
        self.bias_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]), step=1,
          decimals=1,
          units="mA")
        form.addRow("Bias:", self.bias_mA)
        self.offset = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=2, units="")
        form.addRow("Offset:", self.offset)
        self.modulation = QtWidgets.QComboBox(self)
        self.modulation.addItems(["Off", "+Ramp", "-Ramp"])
        self.modulation.setCurrentText(self.worker.parameters["calibration"]["modulation"])
        form.addRow("Modulation:", self.modulation)
        self.min_mode_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Min mode width:", self.min_mode_width)
        form.addRow(mogui.HLine(self))
        self.frequency_threshold_GHz = mogui.DblSpinner(min=0, max=100000, step=1, decimals=2, units="GHz")
        form.addRow("Frequency threshold:", self.frequency_threshold_GHz)
        form.addRow(mogui.HLine(self))
        self.max_bare_diode_current_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]),
          step=1,
          decimals=1,
          units="mA")
        form.addRow("Max bare diode current:", self.max_bare_diode_current_mA)
        self.max_laser_current_mA = mogui.DblSpinner(min=0, max=250, step=1, decimals=1, units="mA")
        form.addRow("Max laser current:", self.max_laser_current_mA)

    def refresh_group(self):
        """
        Refresh content of group fields
        """
        self.default_current_mA.setValue(self.worker.parameters["calibration"]["default_current_mA"])
        self.current_step_mA.setValue(self.worker.parameters["calibration"]["current_step_mA"])
        self.n_steps.setValue(self.worker.parameters["calibration"]["n_steps"])
        self.encoder_step.setValue(self.worker.parameters["calibration"]["encoder_step"])
        self.n_replicates.setValue(self.worker.parameters["calibration"]["n_replicates"])
        self.scan_width.setValue(self.worker.parameters["calibration"]["scan_width"])
        self.bias_mA.setValue(self.worker.parameters["calibration"]["bias_mA"])
        self.offset.setValue(self.worker.parameters["calibration"]["offset"])
        self.min_mode_width.setValue(self.worker.parameters["calibration"]["min_mode_width"])
        self.frequency_threshold_GHz.setValue(self.worker.parameters["calibration"]["frequency_threshold_GHz"])
        self.max_bare_diode_current_mA.setValue(self.worker.parameters["calibration"]["max_bare_diode_current_mA"])
        self.max_laser_current_mA.setValue(self.worker.parameters["calibration"]["max_laser_current_mA"])

    def save_group(self):
        """
        Save content of group fields
        """
        calibration = {'default_current_mA':(self.default_current_mA.value)(), 
         'current_step_mA':(self.current_step_mA.value)(), 
         'n_steps':(self.n_steps.value)(), 
         'encoder_step':(self.encoder_step.value)(), 
         'n_replicates':(self.n_replicates.value)(), 
         'scan_width':(self.scan_width.value)(), 
         'bias_mA':(self.bias_mA.value)(), 
         'offset':(self.offset.value)(), 
         'modulation':(self.modulation.currentText)(), 
         'min_mode_width':(self.min_mode_width.value)(), 
         'frequency_threshold_GHz':(self.frequency_threshold_GHz.value)(), 
         'max_bare_diode_current_mA':(self.max_bare_diode_current_mA.value)(), 
         'max_laser_current_mA':(self.max_laser_current_mA.value)()}
        self.worker.parameters["calibration"].update(calibration)


class CEMLaserTuningParameters(CEMParameterGroup, QtWidgets.QGroupBox):

    def init_UI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.w_laser_tuning_settings = QtWidgets.QWidget(self)
        self.w_laser_tuning_settings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.w_laser_tuning_settings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.w_laser_tuning_settings)
        self.frequency_threshold_MHz = mogui.DblSpinner(min=0, max=100000, step=1, decimals=2, units="MHz")
        form.addRow("Frequency threshold:", self.frequency_threshold_MHz)
        self.default_current_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]),
          step=1,
          decimals=1,
          units="mA")
        form.addRow("Default current:", self.default_current_mA)
        self.min_current_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]), step=1,
          decimals=1,
          units="mA")
        form.addRow("Min current:", self.min_current_mA)
        self.max_current_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]), step=1,
          decimals=1,
          units="mA")
        form.addRow("Max current:", self.max_current_mA)
        self.current_step_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]),
          step=1,
          decimals=1,
          units="mA")
        form.addRow("Current step:", self.current_step_mA)
        self.current_step_fine_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]),
          step=0.1,
          decimals=2,
          units="mA")
        form.addRow("Current step fine:", self.current_step_fine_mA)
        self.n_steps = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_steps:", self.n_steps)
        self.n_steps_fine = mogui.IntSpinner(min=0, max=99, step=1, units="")
        form.addRow("n_steps fine:", self.n_steps_fine)
        form.addRow(mogui.HLine(self))
        self.bias_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]), step=1,
          decimals=1,
          units="mA")
        form.addRow("Bias:", self.bias_mA)
        self.slow_bias_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]), step=1,
          decimals=1,
          units="mA")
        form.addRow("Slow bias:", self.slow_bias_mA)
        self.offset = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=2, units="")
        form.addRow("Offset:", self.offset)
        self.scan_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Scan width:", self.scan_width)
        self.slow_scan_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Slow scan width:", self.slow_scan_width)
        self.scan_width_max = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Scan width max:", self.scan_width_max)
        self.tuning_range_ticks = mogui.IntSpinner(min=0, max=(self.worker.device_config.max_encoder - self.worker.device_config.min_encoder),
          step=1,
          units="")
        form.addRow("Tuning range ticks:", self.tuning_range_ticks)
        self.step_size = mogui.IntSpinner(min=0, max=1000, step=1, units="")
        form.addRow("Step size:", self.step_size)
        self.step_size_fine = mogui.IntSpinner(min=0, max=100, step=1, units="")
        form.addRow("Step size fine:", self.step_size_fine)
        form.addRow(mogui.HLine(self))
        self.default_wavemeter = QtWidgets.QComboBox(self)
        self.default_wavemeter.addItems([name.upper() for name in SupportedWavemeters.__members__.keys()])
        form.addRow("Default wavemeter:", self.default_wavemeter)
        self.hfw_server_app_path_selector = mogui.PushButton("Select exe")
        self.hfw_server_app_path_selector.clicked.connect(self.get_server_app_path)
        form.addRow("HFW Server app path:", self.hfw_server_app_path_selector)

    def refresh_group(self):
        """
        Refresh the content of the group fields
        """
        self.frequency_threshold_MHz.setValue(self.worker.parameters["laser_tuning"]["frequency_threshold_MHz"])
        self.default_current_mA.setValue(self.worker.parameters["laser_tuning"]["default_current_mA"])
        self.min_current_mA.setValue(self.worker.parameters["laser_tuning"]["min_current_mA"])
        self.max_current_mA.setValue(self.worker.parameters["laser_tuning"]["max_current_mA"])
        self.current_step_mA.setValue(self.worker.parameters["laser_tuning"]["current_step_mA"])
        self.current_step_fine_mA.setValue(self.worker.parameters["laser_tuning"]["current_step_fine_mA"])
        self.n_steps.setValue(self.worker.parameters["laser_tuning"]["n_steps"])
        self.n_steps_fine.setValue(self.worker.parameters["laser_tuning"]["n_steps_fine"])
        self.bias_mA.setValue(self.worker.parameters["laser_tuning"]["bias_mA"])
        self.slow_bias_mA.setValue(self.worker.parameters["laser_tuning"]["slow_bias_mA"])
        self.offset.setValue(self.worker.parameters["laser_tuning"]["offset"])
        self.scan_width.setValue(self.worker.parameters["laser_tuning"]["scan_width"])
        self.slow_scan_width.setValue(self.worker.parameters["laser_tuning"]["slow_scan_width"])
        self.scan_width_max.setValue(self.worker.parameters["laser_tuning"]["scan_width_max"])
        self.tuning_range_ticks.setValue(self.worker.parameters["laser_tuning"]["tuning_range_ticks"])
        self.step_size.setValue(self.worker.parameters["laser_tuning"]["step_size"])
        self.step_size_fine.setValue(self.worker.parameters["laser_tuning"]["step_size_fine"])
        if (cur_default_wavemeter := self.worker.device_config.default_wavemeter) is None:
            self.default_wavemeter.setCurrentIndex(SupportedWavemeters["fzw"].value)
        else:
            self.default_wavemeter.setCurrentIndex(cur_default_wavemeter.value)
        self.hfw_server_app_path = self.worker.device_config.devices["hfw"].get("server_app_path", None)

    def save_group(self):
        """
        Save contents of the groups fields
        """
        laser_tuning = {'frequency_threshold_MHz':(self.frequency_threshold_MHz.value)(), 
         'default_current_mA':(self.default_current_mA.value)(), 
         'min_current_mA':(self.min_current_mA.value)(), 
         'max_current_mA':(self.max_current_mA.value)(), 
         'current_step_mA':(self.current_step_mA.value)(), 
         'current_step_fine_mA':(self.current_step_fine_mA.value)(), 
         'n_steps':(self.n_steps.value)(), 
         'n_steps_fine':(self.n_steps_fine.value)(), 
         'bias_mA':(self.bias_mA.value)(), 
         'slow_bias_mA':(self.slow_bias_mA.value)(), 
         'scan_width':(self.scan_width.value)(), 
         'slow_scan_width':(self.slow_scan_width.value)(), 
         'offset':(self.offset.value)(), 
         'scan_width_max':(self.scan_width_max.value)(), 
         'tuning_range_ticks':(self.tuning_range_ticks.value)(), 
         'step_size':(self.step_size.value)(), 
         'step_size_fine':(self.step_size_fine.value)()}
        self.worker.parameters["laser_tuning"].update(laser_tuning)
        self.worker.device_config.update_default_wavemeter(SupportedWavemeters(self.default_wavemeter.currentIndex()))
        self.worker.device_config.update_device_param("hfw", "server_app_path", self.hfw_server_app_path)

    def get_server_app_path(self):
        if not self.hfw_server_app_path:
            open_dir = "C:\\\\"
        else:
            open_dir = os.path.dirname(self.hfw_server_app_path)
        ret, _ = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="HFW Server app path", dir=open_dir,
          filter="Executable files (*.exe)")
        if ret:
            self.hfw_server_app_path = ret


class CEMSpectroscopyParameters(CEMParameterGroup, QtWidgets.QGroupBox):

    def init_UI(self):
        vb = QtWidgets.QVBoxLayout(self)
        self.w_spectroscopy_settings = QtWidgets.QWidget(self)
        self.w_spectroscopy_settings.setMinimumWidth(200)
        form = QtWidgets.QFormLayout(self.w_spectroscopy_settings)
        form.setContentsMargins(0, 0, 0, 0)
        vb.addWidget(self.w_spectroscopy_settings)
        self.direction = QtWidgets.QComboBox(self)
        self.direction.addItems(["up", "down"])
        form.addRow("Direction:", self.direction)
        self.scan_frequency_Hz_fast = mogui.DblSpinner(min=0, max=5, step=1, decimals=3, units="Hz")
        form.addRow("Scan freq. fast:", self.scan_frequency_Hz_fast)
        self.scan_frequency_Hz_medium = mogui.DblSpinner(min=0, max=5, step=0.1, decimals=3, units="Hz")
        form.addRow("Scan freq. medium:", self.scan_frequency_Hz_medium)
        self.scan_frequency_Hz_slow = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="Hz")
        form.addRow("Scan freq. slow:", self.scan_frequency_Hz_slow)
        self.scan_frequency_offset_THz = mogui.DblSpinner(min=(-1), max=1, step=0.01, decimals=4, units="THz")
        form.addRow("Scan freq. offset:", self.scan_frequency_offset_THz)
        form.addRow(mogui.HLine(self))
        self.n_periods = mogui.DblSpinner(min=0, max=99, step=0.5, decimals=1, units="")
        form.addRow("n_periods:", self.n_periods)
        self.filter_position_step_size = mogui.IntSpinner(min=0, max=1000, step=1, units="")
        form.addRow("Filter step size:", self.filter_position_step_size)
        self.min_mode_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Min mode width:", self.min_mode_width)
        self.tuning_scan_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Tuning scan width:", self.tuning_scan_width)
        self.scan_width = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=3, units="")
        form.addRow("Scan width:", self.scan_width)
        self.offset = mogui.DblSpinner(min=0, max=1, step=0.01, decimals=2, units="")
        form.addRow("Offset:", self.offset)
        form.addRow(mogui.HLine(self))
        self.filter_position_shift_on_error = mogui.IntSpinner(min=0, max=1000, step=1, units="")
        form.addRow("Error filter shift:", self.filter_position_shift_on_error)
        self.set_frequency_GHz_shift_on_error = mogui.IntSpinner(min=0, max=1000, step=1, units="")
        form.addRow("Error freq. shift:", self.set_frequency_GHz_shift_on_error)
        self.bias_mA = mogui.DblSpinner(min=0, max=(self.worker.parameters["calibration"]["max_laser_current_mA"]), step=1,
          decimals=1,
          units="mA")
        form.addRow("Bias:", self.bias_mA)

    def refresh_group(self):
        """
        Refresh the content of the group fields
        """
        i = self.direction.findText(self.worker.parameters["spectroscopy"]["direction"], QtCore.Qt.MatchStartsWith)
        if i < 0:
            i = 0
        self.direction.setCurrentIndex(i)
        self.scan_frequency_Hz_fast.setValue(self.worker.parameters["spectroscopy"]["scan_frequency_Hz_fast"])
        self.scan_frequency_Hz_medium.setValue(self.worker.parameters["spectroscopy"]["scan_frequency_Hz_medium"])
        self.scan_frequency_Hz_slow.setValue(self.worker.parameters["spectroscopy"]["scan_frequency_Hz_slow"])
        self.scan_frequency_offset_THz.setValue(self.worker.parameters["spectroscopy"]["scan_frequency_offset_THz"])
        self.n_periods.setValue(self.worker.parameters["spectroscopy"]["n_periods"])
        self.filter_position_step_size.setValue(self.worker.parameters["spectroscopy"]["filter_position_step_size"])
        self.min_mode_width.setValue(self.worker.parameters["spectroscopy"]["min_mode_width"])
        self.tuning_scan_width.setValue(self.worker.parameters["spectroscopy"]["tuning_scan_width"])
        self.scan_width.setValue(self.worker.parameters["spectroscopy"]["scan_width"])
        self.offset.setValue(self.worker.parameters["spectroscopy"]["offset"])
        self.filter_position_shift_on_error.setValue(self.worker.parameters["spectroscopy"]["filter_position_shift_on_error"])
        self.set_frequency_GHz_shift_on_error.setValue(self.worker.parameters["spectroscopy"]["set_frequency_GHz_shift_on_error"])
        self.bias_mA.setValue(self.worker.parameters["spectroscopy"]["bias_mA"])

    def save_group(self):
        """
        Save content of the group fields
        """
        spectroscopy = {'direction':(self.direction.currentText)(), 
         'scan_frequency_Hz_fast':(self.scan_frequency_Hz_fast.value)(), 
         'scan_frequency_Hz_medium':(self.scan_frequency_Hz_medium.value)(), 
         'scan_frequency_Hz_slow':(self.scan_frequency_Hz_slow.value)(), 
         'scan_frequency_offset_THz':(self.scan_frequency_offset_THz.value)(), 
         'n_periods':(self.n_periods.value)(), 
         'filter_position_step_size':(self.filter_position_step_size.value)(), 
         'min_mode_width':(self.min_mode_width.value)(), 
         'tuning_scan_width':(self.tuning_scan_width.value)(), 
         'scan_width':(self.scan_width.value)(), 
         'offset':(self.offset.value)(), 
         'filter_position_shift_on_error':(self.filter_position_shift_on_error.value)(), 
         'set_frequency_GHz_shift_on_error':(self.set_frequency_GHz_shift_on_error.value)(), 
         'bias_mA':(self.bias_mA.value)()}
        self.worker.parameters["spectroscopy"].update(spectroscopy)


class CEMParametersDialog(mogui.MOGDialog):

    def __init__(self, worker, parent=None):
        super(CEMParametersDialog, self).__init__("Adjust parameters", parent=parent)
        self.worker = worker
        hb = QtWidgets.QHBoxLayout(self)
        self.cem_delay_parameters = CEMDelayParameters(title="Delay parameters", worker=worker)
        hb.addWidget(self.cem_delay_parameters)
        self.cem_mode_detection_parameters = CEMModeDetectionParameters(title="Mode detection parameters", worker=worker)
        hb.addWidget(self.cem_mode_detection_parameters)
        self.cem_calibration_parameters = CEMCalibrationParameters(title="Calibration parameters", worker=worker)
        hb.addWidget(self.cem_calibration_parameters)
        self.cem_laser_tuning_parameters = CEMLaserTuningParameters(title="Laser tuning parameters", worker=worker)
        hb.addWidget(self.cem_laser_tuning_parameters)
        self.cem_spectroscopy_parameters = CEMSpectroscopyParameters(title="Spectroscopy parameters", worker=worker)
        hb.addWidget(self.cem_spectroscopy_parameters)
        vb = QtWidgets.QVBoxLayout(self)
        self.btn_reset = mogui.PushButton("Default")
        self.btn_reset.pressed.connect(self.reset)
        vb.addWidget(self.btn_reset)
        self.btn_save = mogui.PushButton("Save")
        self.btn_save.pressed.connect(self.save)
        vb.addWidget(self.btn_save)
        save_parameters = QtWidgets.QGroupBox(title="Save parameters")
        save_parameters.setLayout(vb)
        save_parameters.setFixedWidth(100)
        hb.addWidget(save_parameters)
        self.setFocus()

    @mogui.wrap_except
    def reset(self):
        self.worker.device_config.default_parameters()
        self.refresh()
        logger.info("Parameters reset")

    @mogui.wrap_except
    def save(self):
        self.cem_delay_parameters.save_group()
        self.cem_mode_detection_parameters.save_group()
        self.cem_calibration_parameters.save_group()
        self.cem_laser_tuning_parameters.save_group()
        self.cem_spectroscopy_parameters.save_group()
        logger.info("Parameters updated")

    @mogui.wrap_except
    def refresh(self):
        """
        Refresh parameter groups
        """
        self.cem_delay_parameters.refresh_group()
        self.cem_mode_detection_parameters.refresh_group()
        self.cem_calibration_parameters.refresh_group()
        self.cem_laser_tuning_parameters.refresh_group()
        self.cem_spectroscopy_parameters.refresh_group()

# okay decompiling cem/windows/parameters.pyc
