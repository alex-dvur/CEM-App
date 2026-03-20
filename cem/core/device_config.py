import collections
import logging
import os
import pickle
from functools import wraps
from typing import Optional, Dict

import numpy as np
from cem import SupportedWavemeters, DATA_FILES
from cem.core.parameters import initial_parameters
from mogui import MOGDevice

logger = logging.getLogger(__name__)
NDict = Optional[Dict]


def save(func):
    """Decorator to save CEMConfig obj to file after func call."""
    @wraps(func)
    def inner(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self._save()
        return ret
    return inner


class CEMConfig:

    @save
    def __init__(self, cem_serial_number: str, mog: bool = False):
        self._mog = mog
        self._cem_serial_number = cem_serial_number
        self.motor_encoder_factor = 728.1777777777778
        self.min_encoder = None
        self.max_encoder = None
        self._factory_parameters = None
        self._custom_parameters = None
        self._factory_calibration_data = None
        self._custom_calibration_data = None
        self._daily_calibration_data = None
        self.devices = CEMConfig._devices_dict()
        self.default_wavemeter = SupportedWavemeters.fzw
        self.ticks_two_degrees = None
        self._load()
        if mog:
            if not self.parameters:
                self.default_parameters()

    def __str__(self):
        s = ""
        for key, value in self.__dict__.items():
            s += f"'{key}': {value},\n"
        return s

    def dump(self, filename=None):
        text = []
        if not filename:
            filename = f"{self._cem_serial_number}_config.cfg"
        text.append("[info]")
        text.append(f"serial_number={self._cem_serial_number}")
        text.append(f"motor_encoder_factor={self.motor_encoder_factor}")
        text.append(f"ticks_two_degrees={self.ticks_two_degrees}")
        text.append("\n[devices]")
        text.append(f"default_wavemeter={self.default_wavemeter}")
        for dev, metadata in self.devices.items():
            for k, v in metadata.items():
                text.append(f"{dev},{k}={v}")
        text.append("\n[parameters]")
        if self._factory_parameters:
            for sub_menu, sub_dict in self._factory_parameters.items():
                if isinstance(sub_dict, dict):
                    for k, v in sub_dict.items():
                        text.append(f"{sub_menu},{k}={v}")
        text.append("\n[calibration_data]")
        if self._factory_calibration_data:
            for sub_menu, sub_dict in self._factory_calibration_data.items():
                if isinstance(sub_dict, dict):
                    for k1, v1 in sub_dict.items():
                        if isinstance(v1, dict):
                            for k2, v2 in v1.items():
                                if isinstance(v2, np.ndarray):
                                    v2 = np.array2string(v2, threshold=int(10000000.0), max_line_width=int(10000000000.0))
                                text.append(f"{sub_menu},{k1},{k2}={v2}")
                        elif isinstance(v1, np.ndarray):
                            v1 = np.array2string(v1, threshold=int(10000000.0), max_line_width=int(10000000000.0))
                            text.append(f"{sub_menu},{k1}={v1}")
                        else:
                            text.append(f"{sub_menu},{k1}={v1}")
                else:
                    text.append(f"{sub_menu}={sub_dict}")
        with open(filename, "w") as fp:
            fp.writelines(f"{line}\n" for line in text)

    @property
    def parameters(self):
        if self._mog:
            return self._custom_parameters or self._factory_parameters
        return self._custom_parameters

    @parameters.setter
    @save
    def parameters(self, vals):
        if self._mog:
            self._factory_parameters = vals
        else:
            self._custom_parameters = vals

    @parameters.deleter
    def parameters(self):
        self.parameters = None

    @property
    def calibration_data(self):
        if self._mog:
            return self._custom_calibration_data or self._factory_calibration_data
        return self._custom_calibration_data

    @calibration_data.setter
    @save
    def calibration_data(self, vals):
        if self._mog:
            self._factory_calibration_data = vals
        else:
            self._custom_calibration_data = vals

    @calibration_data.deleter
    def calibration_data(self):
        self.calibration_data = None

    @property
    def daily_calibration_data(self):
        return self._daily_calibration_data

    @daily_calibration_data.setter
    @save
    def daily_calibration_data(self, vals):
        self._daily_calibration_data = vals

    @daily_calibration_data.deleter
    def daily_calibration_data(self):
        self.daily_calibration_data = None

    def reset_parameters(self):
        del self.parameters

    def reset_calibration_data(self):
        del self.calibration_data

    def reset_daily_calibration(self):
        del self.daily_calibration_data

    def _load(self):
        """Load saved configuration from pickle file if it exists."""
        fn = self._cem_serial_number + DATA_FILES["device_config"]
        if not os.path.exists(fn):
            logger.info("No saved config found for %s" % self._cem_serial_number)
            return
        try:
            with open(fn, "rb") as fp:
                saved = pickle.load(fp)
            for key, value in saved.__dict__.items():
                if not key.startswith('__'):
                    setattr(self, key, value)
            logger.info("Loaded config for %s" % self._cem_serial_number)
        except Exception as e:
            logger.warning("Failed to load config: %s" % e)

    def _save(self):
        fn = self._cem_serial_number + DATA_FILES["device_config"]
        try:
            with open(fn, "wb") as fp:
                pickle.dump(self, fp)
        except Exception as e:
            logger.warning("Failed to save config: %s" % e)

    @save
    def update_device_param(self, dev: str, key: str, val: str):
        self.devices.setdefault(dev, {})[key] = val

    @save
    def update_device(self, dev: MOGDevice):
        if not dev:
            return
        info_dict = dev.info_dict()
        device = info_dict["type"].lower()
        sn = info_dict["serial"]
        self.devices.setdefault(device, {})["connection"] = dev.connection
        self.devices[device]["serial"] = sn

    @staticmethod
    def _devices_dict() -> Dict[str, Dict]:
        """Creates default dictionary for four standard devices."""
        return {'cem': {}, 'mld': {}, 'fzw': {}, 'hfw': {}}

    @save
    def update_default_wavemeter(self, val: SupportedWavemeters):
        self.default_wavemeter = val

    @save
    def set_motor_encoder_factor(self, val):
        self.motor_encoder_factor = val

    @save
    def set_ticks_two_degrees(self, val):
        self.ticks_two_degrees = val

    def get_tick_translate(self):
        if not self.ticks_two_degrees:
            return 0
        return 2 * self.motor_encoder_factor - self.ticks_two_degrees

    def store_encoder_limits(self, vals):
        self.min_encoder, self.max_encoder = vals

    def default_parameters(self):
        if self._mog:
            self.parameters = initial_parameters()
        else:
            self.parameters = self._factory_parameters
