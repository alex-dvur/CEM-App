# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\utils\data_structures.py
from dataclasses import dataclass, field
from typing import List
import numpy as np

@dataclass
class ResonanceResponse:
    percent: int
    time = field(metadata={"units": "s"})
    time: float


@dataclass
class ResonanceDataPoint:
    time = field(metadata={"units": "s"})
    time: float
    frequency = field(metadata={"units": "THz"})
    frequency: float


@dataclass
class ResonanceScan:
    on_wavelength = field(default=(-1), metadata={"units": "nm [vac]"})
    on_wavelength: float
    off_wavelength = field(default=(-1), metadata={"units": "nm [vac]"})
    off_wavelength: float
    wait_t = field(default=(-1), metadata={"units": "s"})
    wait_t: float
    off_settle_t = field(default=(-1), metadata={"units": "s"})
    off_settle_t: float
    off_single_mode_t = field(default=(-1, -1), metadata={"units": "s"})
    off_single_mode_t: (float, float)
    response_times = field(default_factory=(lambda: []))
    response_times: List[ResonanceResponse]
    data = field(default_factory=(lambda: []))
    data: List[ResonanceDataPoint]

    @property
    def time_series(self):
        return [resonance_data.time for resonance_data in self.data]

    @property
    def frequency_series(self):
        return [resonance_data.frequency for resonance_data in self.data]

    @property
    def time_and_frequency(self):
        return (self.time_series, self.frequency_series)


@dataclass
class PowerAnglePoint:
    encoder_position = field(default=(np.nan), metadata={"units": "ticks"})
    encoder_position: int
    measured_power = field(default=(-1), metadata={"units": "mW"})
    measured_power: float


@dataclass
class PowerAngleCurrent:
    current = field(default=(-1), metadata={"units": "mA"})
    current: float
    data = field(default_factory=list)
    data: List[PowerAnglePoint]

    @property
    def encoder_series(self):
        return np.asarray([measurement.encoder_position for measurement in self.data])

    @property
    def power_series(self):
        return np.asarray([measurement.measured_power for measurement in self.data])

    @property
    def encoder_and_power(self):
        return (self.encoder_series, self.power_series)


@dataclass
class PowerAngleScan:
    currents = field(default_factory=list)
    currents: List[PowerAngleCurrent]


@dataclass
class MeasurementData:
    resonance = ResonanceScan()
    resonance: ResonanceScan
    power_angle = PowerAngleScan()
    power_angle: PowerAngleScan


def units(cls, attribute_name):
    return cls.__dataclass_fields__[attribute_name.lower()].metadata.get("units", None)

# okay decompiling cem/utils/data_structures.pyc
