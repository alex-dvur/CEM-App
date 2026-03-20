# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\utils\conversions.py
import numpy as np
from cem.utils.typing import *

class Conversions:
    __doc__ = "\n    Subclass to handle conversions.\n    "

    def __init__(self, worker: "CEMWorker"=None):
        self.speed_of_light = 299792458
        self._worker = worker

    @property
    def motor_encoder_factor(self):
        return self.worker.device_config.motor_encoder_factor

    @property
    def worker(self):
        assert self._worker, "Need to connect worker to use this function."
        return self._worker

    @staticmethod
    def n_eff_air(wavelength_nm):
        return 0.05792105 / (238.0185 - (1000.0 / wavelength_nm) ** 2) + 0.00167917 / (57.362 - (1000.0 / wavelength_nm) ** 2) + 1

    def to_wavelength(self, value, unit_in='THz', unit_out='nm'):
        """
        Convert input value (wavelength or frequency) to wavelength. Allows to set both input and output units.

        Arguments:
            value: Input value, wither wavelength or frequency, float, list or ndarray
            unit_in (str): m, nm, THz, Hz
            unit_out (str): m, nm

        Returns:
            wavelength (float): wavelength in specified unit
        """
        if "Hz" in unit_in:
            if unit_in == "THz":
                frequency_Hz = np.multiply(value, 1000000000000.0)
            else:
                if unit_in == "Hz":
                    frequency_Hz = value
                else:
                    raise AttributeError("Unsupported unit")
            wavelength_m = np.divide(self.speed_of_light, frequency_Hz)
        else:
            if "m" in unit_in:
                if unit_in == "m":
                    wavelength_m = value
                else:
                    if unit_in == "nm":
                        wavelength_m = np.multiply(value, 1e-09)
                    else:
                        raise AttributeError("Unsupported unit")
            else:
                raise AttributeError("Unsupported unit")
        if unit_out == "m":
            return wavelength_m
        if unit_out == "nm":
            return np.multiply(wavelength_m, 1000000000.0)
        raise AttributeError("Unsupported unit")

    def to_frequency(self, value, unit_in='nm', unit_out='THz'):
        """
        Convert input value (wavelength or frequency) to frequency. Allows to set both input and output units.

        Arguments:
            value (float): Input value, wither wavelength or frequency
            unit_in (str): m, nm, THz, Hz
            unit_out (str): THz, Hz

        Returns:
            frequency (float): frequency in specified unit
        """
        if "m" in unit_in:
            if unit_in == "m":
                wavelength_m = value
            else:
                if unit_in == "nm":
                    wavelength_m = np.multiply(value, 1e-09)
                else:
                    raise AttributeError("Unsupported unit")
            frequency_Hz = np.divide(self.speed_of_light, wavelength_m)
        else:
            if "Hz" in unit_in:
                if unit_in == "THz":
                    frequency_Hz = np.multiply(value, 1000000000000.0)
                else:
                    if unit_in == "Hz":
                        frequency_Hz = value
                    else:
                        raise AttributeError("Unsupported unit")
            else:
                raise AttributeError("Unsupported unit")
        if unit_out == "THz":
            return np.multiply(frequency_Hz, 1e-12)
        if unit_out == "Hz":
            return frequency_Hz
        raise AttributeError("Unsupported unit")

    def fzw_units(self, value, unit_in, unit_out):
        """
        Adapted from Martijn's code

        """
        if unit_in == unit_out:
            return value
            if unit_in == "nm":
                wavelength_nm_vac = value
        elif unit_in == "nm (vac)":
            wavelength_nm_vac = value
        else:
            if unit_in == "pcm":
                wavelength_nm_vac = 10000000.0 / value
            else:
                if unit_in == "THz":
                    wavelength_nm_vac = self.speed_of_light / value / 1000.0
                else:
                    if unit_in == "nm (air)":
                        wavelength_nm_vac = value * self.n_eff_air(value)
                    else:
                        raise AttributeError("Input unit not supported!")
        if unit_out == "nm":
            return wavelength_nm_vac
        if unit_out == "nm (vac)":
            return wavelength_nm_vac
        if unit_out == "nm (air)":
            return wavelength_nm_vac / self.n_eff_air(wavelength_nm_vac)
        if unit_out == "THz":
            return self.speed_of_light / wavelength_nm_vac / 1000.0
        if unit_out == "pcm":
            return 10000000.0 / wavelength_nm_vac
        raise AttributeError("Output unit not supported!")

    def to_angle(self, encoder_ticks, decimals=6):
        d = self.worker.device_config.get_tick_translate()
        if type(encoder_ticks) is np.ndarray or type(encoder_ticks) is list:
            return [float(np.round(((temp + d) / self.motor_encoder_factor), decimals=decimals)) for temp in encoder_ticks]
        return float(np.round(((encoder_ticks + d) / self.motor_encoder_factor), decimals=decimals))

    def to_encoder_ticks(self, angle):
        return int(np.round((angle * self.motor_encoder_factor), decimals=0))

    def encoder_to_frequency(self, encoder_ticks):
        return

# okay decompiling cem/utils/conversions.pyc
