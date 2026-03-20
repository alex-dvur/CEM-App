# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\gui\server_status.py
"""
    Handle displaying server status on the GUI
"""
from mogui import QtWidgets

class ServerLabel(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(ServerLabel, self).__init__(parent)
        self.setText("Server Offline")
        self.setContentsMargins(10, 5, 10, 5)

    def set_ready_to_connect(self, ip_address, port):
        self.setText("Ready to connect on %s:%s" % (ip_address, port))

    def set_connection_accepted(self, ip_address, port):
        self.setText("Connected with %s:%s" % (ip_address, port))

# okay decompiling cem/gui/server_status.pyc
