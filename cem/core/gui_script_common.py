# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\core\gui_script_common.py
import logging
from cem import SupportedWavemeters
from cem.utils.typing import *
from mogui import DeviceError
logger = logging.getLogger(__name__)

class CEMAppGUIScriptCommon:

    def __init__(self):
        self.worker = None

    def connect_MLD(self, *args, **kwargs):
        raise NotImplementedError

    def connect_FZW(self, *args, **kwargs):
        raise NotImplementedError

    def connect_HFW(self, *args, **kwargs):
        raise NotImplementedError

    def connect_hardware(self):
        settings = self.worker.device_config.devices
        mld_settings = settings.get("mld")
        connection = mld_settings.get("connection")
        expected_serial = mld_settings.get("serial")
        if self.connect_MLD(addr=connection, expected_serial=expected_serial):
            try:
                self.worker.init.start_mld()
            except DeviceError:
                pass
            else:
                if self.worker.default_wavemeter == SupportedWavemeters.fzw:
                    fzw_settings = settings.get("fzw")
                    connection = fzw_settings.get("connection")
                    expected_serial = fzw_settings.get("serial")
                    if self.connect_FZW(addr=connection, expected_serial=expected_serial):
                        self.worker.init.start_fzw()
                    else:
                        if self.worker.default_wavemeter == SupportedWavemeters.hfw:
                            self.connect_HFW()
                        else:
                            raise ValueError(f"Unsupported wavemeter type {self.worker.default_wavemeter.name}")
                    if self.worker.get.all_hardware_connected():
                        logger.info("Required hardware connected.")
                        self.worker.got_status.emit({"status": "Required hardware connected."})
                        try:
                            logger.debug(self.worker.cem.ask("INFO"))
                        except DeviceError:
                            pass
                        else:
                            try:
                                logger.debug(self.worker.mld.ask("INFO"))
                            except DeviceError:
                                pass
                            else:
                                if self.worker.default_wavemeter == SupportedWavemeters.fzw:
                                    try:
                                        logger.debug(self.worker.fzw.ask("INFO"))
                                    except DeviceError:
                                        pass

                elif self.worker.default_wavemeter == SupportedWavemeters.hfw:
                    logger.debug(f"HFW {self.worker.hfw.version()}")
        else:
            self.worker.got_status.emit({"error": "Required hardware not connected."})
            logger.error("Required hardware not connected.")

# okay decompiling cem/core/gui_script_common.pyc
