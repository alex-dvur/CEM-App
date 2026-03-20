# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\server\device_cmds.py
"""
    Handle communication with devices
"""

class DeviceCommand:
    __doc__ = "Handle all commands sending to connected devices"
    SUPPORTED_DEVICES = [
     "cem", "mld", "fzw"]

    def __init__(self, worker) -> None:
        self.worker = worker

    def process(self, cmd):
        """Process DEV command"""
        if cmd[0] in self.SUPPORTED_DEVICES:
            dev = getattr(self.worker, cmd[0], self.default)
            if dev:
                return dev.ask(",".join(cmd[1:]))
            return f"{cmd[0]} might not connected, please check"
        return

    def default(self):
        return

# okay decompiling cem/server/device_cmds.pyc
