# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: mogui\thorlabs_new.py
import logging, pyvisa as visa
from ThorlabsPM100 import ThorlabsPM100
logger = logging.getLogger("mogui")

def connectPowerMeter():
    rm = visa.ResourceManager()
    matches = []
    sensors = []
    for m in rm.list_resources("USB?::0x1313::?*::INSTR"):
        try:
            inst = rm.open_resource(m)
            s = inst.query("SYSTEM:SENSOR:IDN?")
            matches.append(m)
            sensors.append(s.strip())
        except Exception as E:
            try:
                logger.exception(E)
            finally:
                E = None
                del E

    else:
        assert len(matches) > 0, "No PM detected. Check the USB connection; set device driver to PM100D."
        inst = rm.open_resource(matches[0])
        if len(matches) > 1:
            logger.info("Multiple PM detected. Connected to first one.")
        return ThorlabsPM100(inst=inst)

# okay decompiling mogui/thorlabs_new.pyc
