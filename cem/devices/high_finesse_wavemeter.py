# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\devices\high_finesse_wavemeter.py
"""
Interface for HighFinesse Wavemeters using their provided DLL. Note that their

Current interface only offers limited functionality to read frequency

N.B. it is possible to install callbacks and notifications to avoid polling the wavemeter execessively. However, to keep consistent
behaviour between HighFinesseWavemeters and MOG FZW, a polling approach will be utilised.
Written by Josh Cherubino
Last edited 14/02/2022 by Josh Cherubino
"""
import ctypes
try:
    from PySide2.QtCore import Slot
except ImportError:
    from PySide6.QtCore import Slot
import logging
logger = logging.getLogger(__name__)

class HighFinesseWavemeter:

    def __init__(self, server_app_path: str, hidden: bool=True):
        """
        To initialise a HFW to use, we must first start the WLM server application. Then we can set the
        HFW to measure data.
        """
        self.server_app_path_ptr = ctypes.c_char_p(server_app_path.encode(encoding="ascii"))
        self._hidden = hidden
        self.dll = ctypes.WinDLL("wlmData.dll")
        self._control_wlm = self.dll.ControlWLMEx
        self._control_wlm.restype = ctypes.c_long
        self._control_wlm.argtypes = [ctypes.c_long,
         ctypes.c_char_p,
         ctypes.c_long,
         ctypes.c_long,
         ctypes.c_long]
        self._wlm_instantiate = self.dll.Instantiate
        self._wlm_instantiate.restype = ctypes.c_long
        self._wlm_instantiate.argtypes = [ctypes.c_long,
         ctypes.c_long,
         ctypes.c_long, ctypes.c_long]
        self._operation = self.dll.Operation
        self._operation.restype = ctypes.c_long
        self._operation.argtypes = [ctypes.c_ushort]
        self._get_frequency = self.dll.GetFrequencyNum
        self._get_frequency.restype = ctypes.c_double
        self._get_frequency.argtypes = [ctypes.c_long, ctypes.c_double]
        self._get_wlm_version = self.dll.GetWLMVersion
        self._get_wlm_version.restype = ctypes.c_long
        self._get_wlm_version.argtypes = [ctypes.c_long]
        self._get_pressure = self.dll.GetPressure
        self._get_pressure.restype = ctypes.c_double
        self._get_pressure.argtypes = [ctypes.c_double]
        self._get_temperature = self.dll.GetTemperature
        self._get_temperature.restype = ctypes.c_double
        self._get_temperature.argtypes = [ctypes.c_double]
        self._set_exposure_mode = self.dll.SetExposureModeNum
        self._set_exposure_mode.restype = ctypes.c_long
        self._set_exposure_mode.argtypes = [ctypes.c_long, ctypes.c_bool]
        self.freq_error_name_table = {
         0: '"ErrNoValue"', -1: '"ErrNoSignal"', -2: '"ErrBadSignal"', -3: '"ErrLowSignal"', 
         -4: '"ErrBigSignal"', , -5: '"ErrWlmMissing"', , -6: '"ErrNotAvailable"', , -7: '"InfNothingChanged"', 
         -8: '"ErrNoPulse"', , -13: '"ErrDiv0"', , -14: '"ErrOutOfRange"', , -15: '"ErrUnitNotAvailable"'}
        self.ErrWlmMissing = -5
        self.wlm_control_constants = {
         'cCtrlWLMShow': 1, 'cCtrlWLMHide': 2, 'cCtrlWLMExit': 3, 'cCtrlWLMWait': 16}
        self.wlm_control_ret_flags_errors = {
         2: '"flErrDeviceNotFound"', 
         4: '"flErrDriverError"', 
         8: '"flErrUSBError"', 
         16: '"flErrUnknownDeviceError"', 
         32: '"flErrWrongSN"', 
         128: '"flErrTemperatureError"', 
         256: '"flErrPressureError"', 
         512: '"flErrCancelledManually"', 
         1024: '"flErrWLMBusy"', 
         4096: '"flErrUnknownError"', 
         8192: '"flNoInstalledVersionFound"', 
         16384: '"flDesiredVersionNotFound"', 
         32768: '"flErrFileNotFound"', 
         65536: '"flErrParmOutOfRange"', 
         131072: '"flErrCouldNotSet"', 
         262144: '"flErrEEPROMFailed"', 
         524288: '"flErrFileFailed"', 
         1048576: '"flDeviceDataNewer"', 
         2097152: '"flFileDataNewer"', 
         4194304: '"flErrDeviceVersionOld"', 
         8388608: '"flErrFileVersionOld"', 
         16777216: '"flDeviceStampNewer"', 
         33554432: '"flFileStampNewer"'}
        self.wlm_control_ret_flags_warnings = {64: "flErrUnknownSN"}
        self.control_flServerStarted = 1
        self.RFC_constants = {
         'cInstCheckForWLM': -1, 'cInstResetCalc': 0, 'cInstReturnMode': 0, 
         'cInstNotification': 1}
        self.base_operation_constants = {'cCtrlStopAll':0, 
         'cCtrlStartMeasurement':2}
        self.set_error_name_table = {
         0: '"ResERR_NoErr"', 
         -1: '"ResERR_WlmMissing"', 
         -2: '"ResERR_CouldNotSet"', 
         -3: '"ResERR_ParmOutOfRange"', 
         -4: '"ResERR_WlmOutOfResources"', 
         -5: '"ResERR_WlmInternalError"', 
         -6: '"ResERR_NotAvailable"', 
         -7: '"ResERR_WlmBusy"', 
         -8: '"ResERR_NotInMeasurementMode"', 
         -9: '"ResERR_OnlyInMeasurementMode"', 
         -10: '"ResERR_ChannelNotAvailable"', 
         -11: '"ResERR_ChannelTemporarilyNotAvailable"', 
         -12: '"ResERR_CalOptionNotAvailable"', 
         -13: '"ResERR_CalWavelengthOutOfRange"', 
         -14: '"ResERR_BadCalibrationSignal"', 
         -15: '"ResERR_UnitNotAvailable"'}
        self.set_ResErr_NoErr = 0
        self.get_temp_pressure_error_name_table = {-1000:"ErrTempNotMeasured", 
         -1006:"ErrTempNotAvailable", 
         -1005:"ErrTempWlmMissing"}
        self.reset()
        self.start()

    def start(self) -> None:
        """
        Start HFW connection
        """
        self._start_control_server()
        if self._wlm_instantiate(self.RFC_constants["cInstResetCalc"], 1, 0, 0) == 0:
            raise RuntimeError("Failed to Instantiate HighFinesse Wavemeter")
        if (ret := self._set_exposure_mode(1, 1)) != self.set_ResErr_NoErr:
            raise RuntimeError(f"Failed to set auto exposure due to error: {self.set_error_name_table[ret]}")
        if (ret := self._operation(self.base_operation_constants["cCtrlStartMeasurement"])) != self.set_ResErr_NoErr:
            raise RuntimeError(f"Failed to start measurements due to error: {self.set_error_name_table[ret]}")

    def _start_control_server(self) -> None:
        """
        Helper method to start WLM control server which checks return flag values

        Raises RuntimeError if failure occurs
        """
        flags = self.wlm_control_constants["cCtrlWLMWait"]
        if self._hidden:
            flags |= self.wlm_control_constants["cCtrlWLMHide"]
        else:
            flags |= self.wlm_control_constants["cCtrlWLMShow"]
        ret = self._control_wlm(flags, self.server_app_path_ptr, 0, -1, 1)
        self._check_control_ret_flags(ret)

    def _stop_control_server(self) -> None:
        """
        Helper method to stop WLM control server.
        """
        if self._control_wlm(self.wlm_control_constants["cCtrlWLMExit"] | self.wlm_control_constants["cCtrlWLMWait"], None, 0, -1, 0) == 0:
            logger.warning("Failed to stop WLM control server")

    def _check_control_ret_flags(self, ret_flags: int):
        """
        Internal helper method to check the return flags from a _control_wlm call
        Raises Value error or warning as appropriate
        """
        errors = ""
        for err_code, err_name in self.wlm_control_ret_flags_errors.items():
            if ret_flags & err_code == err_code:
                errors += f" {err_name} "
        else:
            if ret_flags & self.control_flServerStarted == self.control_flServerStarted:
                if errors:
                    self._stop_control_server()
            if errors:
                raise RuntimeError(f"ControlWLMEx call failed due to error(s) ({errors})")
            for warn_code, warn_name in self.wlm_control_ret_flags_warnings.items():
                if ret_flags & warn_code == warn_code:
                    logger.warning(f"{warn_name} flag(s) set from ControlWLMEx call")

    def reset(self) -> None:
        """
        Required reset actions on GUI shutdown/restart.
        N.B. only warn on failures in reset as they are only cleanup operations and not critical to perform
        """
        if (ret := self._operation(self.base_operation_constants["cCtrlStopAll"])) != self.set_ResErr_NoErr:
            logger.warning(f"Failed to stop measurements due to error: {self.set_error_name_table[ret]}")
        self._stop_control_server()

    def frequency(self) -> float:
        """
        Method to get frequency value from WLM (in THz)
        Raises ValueError on failure
        """
        freq = self._get_frequency(1, 0)
        if freq <= 0:
            raise ValueError(f"HighFinesse Wavemeter error ({self.freq_error_name_table[int(freq)]}) occurred while trying to read frequency")
        return freq

    def temperature(self) -> float:
        """
        Method to get temperature value from HighFinesse Wavemeter (in degrees celsius)
        Raises ValueError on failure
        """
        temperature = self._get_temperature(0)
        if temperature <= 0:
            raise ValueError(f"HighFinesse Wavemeter error ({self.get_temp_pressure_error_name_table[int(temperature)]}) occurred while trying to read temperature")
        return temperature

    def pressure(self) -> float:
        """
        Method to get pressure reading from HighFinesse wavemeter (in mbar)
        Raises ValueError on failure
        """
        pressure = self._get_pressure(0)
        if pressure <= 0:
            raise ValueError(f"HighFinesse Wavemeter error ({self.get_temp_pressure_error_name_table[int(pressure)]}) occurred while trying to read pressure")
        return pressure

    def version(self) -> str:
        """
        Get WLM version number in the form. Returns
        info string on Wavelength meter type & wavelength version number or 'Not connected'
        """
        meter_type = self._get_wlm_version(0)
        if meter_type == self.ErrWlmMissing:
            return "Not connected"
        version_num = self._get_wlm_version(1)
        return f"WS-{meter_type} {version_num}"

    @Slot(bool)
    def set_window_visibility(self, *, hidden: bool):
        """
        method to set visiblity of the WLM control server window
        """
        if self._hidden != bool(hidden):
            self._hidden = bool(hidden)
            flags = self.wlm_control_constants["cCtrlWLMWait"]
            if self._hidden:
                flags |= self.wlm_control_constants["cCtrlWLMHide"]
            else:
                flags |= self.wlm_control_constants["cCtrlWLMShow"]
            ret = self._control_wlm(flags, None, 0, -1, 0)
            try:
                self._check_control_ret_flags(ret)
            except ValueError:
                self.reset()
                self.start()

# okay decompiling cem/devices/high_finesse_wavemeter.pyc
