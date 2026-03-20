"""MOGLabs commander window"""
import os

try:
    from .compat import *
    from . import mogdevice
    from . import mogui as ui
except ImportError:
    from compat import *
    import mogdevice
    import mogui as ui

import logging
logger = logging.getLogger("MOG")


class ReplyBox(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(ReplyBox, self).__init__(parent)
        self.setReadOnly(True)

    def add(self, text, color=None):
        if color:
            text = "<font color=%s>%s</font>" % (color, text)
        self.append(text)

    def newBlock(self):
        self.append("<hr>")


class CommandBox(QtWidgets.QComboBox):
    execCmd = QtCore.Signal(str)
    status = QtCore.Signal(str, str)

    def __init__(self, parent):
        super(CommandBox, self).__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QtWidgets.QComboBox.InsertAtTop)

    def process(self):
        cmd = self.currentText().strip()
        if cmd:
            self.execCmd.emit(cmd)

    def keyPressEvent(self, e):
        if e.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.process()
        else:
            super(CommandBox, self).keyPressEvent(e)


class CommandWindow(ui.MOGDialog):
    def __init__(self, dev=None, parent=None, **kwargs):
        super(CommandWindow, self).__init__("MOGLabs Commander", parent)
        self.initUI()
        self.setDevice(dev)
        self.resize(700, 500)

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        w = QtWidgets.QWidget(self)
        box = QtWidgets.QHBoxLayout(w)
        box.setContentsMargins(2, 2, 2, 2)
        lb = QtWidgets.QLabel("Command:", self)
        box.addWidget(lb)
        self.cmdbox = CommandBox(self)
        self.cmdbox.setToolTip("Command to send to device")
        box.addWidget(self.cmdbox, stretch=1)
        btn = QtWidgets.QPushButton("Send")
        btn.setToolTip("Send command to device")
        btn.pressed.connect(self.cmdbox.process)
        btn.setAutoDefault(True)
        box.addWidget(btn)
        btn = QtWidgets.QPushButton("Run script")
        btn.setToolTip("Upload a series of commands from a text file")
        btn.pressed.connect(self.from_file)
        box.addWidget(btn)
        layout.addWidget(w)
        self.reply = ReplyBox(self)
        layout.addWidget(self.reply, stretch=1)
        w = QtWidgets.QWidget(self)
        box = QtWidgets.QHBoxLayout(w)
        box.setContentsMargins(2, 2, 2, 2)
        btn = QtWidgets.QPushButton("Reconnect")
        btn.pressed.connect(self.reconnect)
        box.addWidget(btn)
        self.lb_connection = QtWidgets.QLabel(self)
        box.addWidget(self.lb_connection)
        box.addStretch(1)
        btn = QtWidgets.QPushButton("Clear")
        btn.setToolTip("Erase the command history")
        btn.pressed.connect(self.clear)
        box.addWidget(btn)
        btn = QtWidgets.QPushButton("Save")
        btn.setToolTip("Save command history and replies to text file")
        btn.pressed.connect(self.to_file)
        box.addWidget(btn)
        layout.addWidget(w)
        self.cmdbox.execCmd.connect(self.cmd)
        self.cmdbox.status.connect(self.reply.add)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

    def setDevice(self, dev):
        self.dev = dev
        if dev is None:
            self.lb_connection.setText("")
        else:
            self.lb_connection.setText("<font color=grey>" + dev.connection)
        self.setWindowTitle("MOGLabs commander")

    def keyPressEvent(self, e):
        if not self.reply.hasFocus():
            self.cmdbox.keyPressEvent(e)
            self.cmdbox.setFocus()

    def cmd(self, cmd_str):
        self.reply.add("> " + cmd_str, "blue")
        try:
            resp = self.dev.ask(cmd_str)
            self.reply.add(resp)
            return True
        except Exception as e:
            self.reply.add(str(e), "red")
            return False

    def reconnect(self):
        try:
            self.dev.reconnect()
            self.reply.add("Reconnected", "green")
        except Exception as e:
            self.reply.add("Reconnect failed: " + str(e), "red")

    def clear(self):
        self.reply.clear()

    def from_file(self):
        filename = ui.file_dialog(self, "Open text file", "Text files (*.txt)", True)
        if filename is None:
            return
        self.reply.newBlock()
        self.reply.add("Executing " + filename, "green")
        script = list(mogdevice.load_script(filename))
        if not script:
            return
        for linenum, cmd_str in script:
            if not self.cmd(cmd_str):
                if not ui.msgbox_yesno(self, "Execution error",
                    'Error during script "%s" at line %d; continue?' % (os.path.split(filename)[1], linenum)):
                    self.reply.add("Script execution aborted", "orange")
                    break

    def to_file(self):
        filename = ui.file_dialog(self, "Save to log file", "Log files (*.log)", False)
        if filename is None:
            return
        data = self.reply.toPlainText()
        with open(filename, "w") as f:
            f.write(data)


if __name__ == "__main__":
    ui.cmdline_start(CommandWindow, debug=True, check=False, check_IAP=False)
