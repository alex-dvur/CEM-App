# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\__init__.py
import time
from enum import Enum, IntEnum, unique
CEM_SN = "DEV0767"
APP_TITLE = "Motorised Cateye App"
APP_TITLE_SHORT = "CEM"
APP_VER = "1.0.1"
RESONANCE_PC = [
 10, 50, 90]
CAM_MAX = 2500
FZW_COLOURS = ["#08f", "#f00"]
BACKLOG = 10
time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
DATA_FILES = {'measurement':"measurement_data.p", 
 'calibration':"calibration_data.p", 
 'calibration_raw_data':"calibration_raw_data.p", 
 'daily_calibration_data':"daily_calibration_data.p", 
 'parameters':"parameters.p", 
 'measurement_data_server':"%s_measurement_data.p" % time_str, 
 'calibration_raw_data_server':"%s_calibration_raw_data.p" % time_str, 
 'device_config':"_config.p", 
 'resonance':f"{time_str}_resonance.p", 
 'power_angle':f"{time_str}_power_angle.p"}

@unique
class SupportedWavemeters(Enum):
    fzw = 0
    hfw = 1


@unique
class Modes(IntEnum):
    uber_fast = -1
    very_fast = 0
    fast = 1
    fine = 2
    very_fine = 3
    retune = 4
    hold = 5


@unique
class DebugModes(Enum):
    none = -1
    resonance = 0
    offline = 1

# okay decompiling cem/__init__.pyc
