# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\server\cmd_handler.py
"""
    Handler all commands that server received
        - Consider as an abstract command handler
"""
from .device_cmds import DeviceCommand
from .general_cmds import GeneralCommand
from cem.utils.typing import *

class CommandHandler:
    __doc__ = "Abstract class to handle command"

    def __init__(self, server=None, worker=None, gui=None, cem_app=None):
        """Init all commander handler"""
        self._dev_cmd = DeviceCommand(worker)
        self._gen_cmd = GeneralCommand(server, gui, cem_app)
        self._cmd = [self._dev_cmd, self._gen_cmd]

    def process(self, received_cmd):
        """Process received command"""
        for c in self._cmd:
            resp = c.process(received_cmd)
            if resp:
                return resp
            return

# okay decompiling cem/server/cmd_handler.pyc
