import sys
import platform

try:
    from .compat import *
    from . import mogdevice
except ImportError:
    from compat import *
    import mogdevice

import logging
import traceback
from os import path
import time
from functools import wraps
from contextlib import contextmanager

QtCore.Qt.AlignMidRight = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
COLOR_GOOD = "#00ff00"
COLOR_BAD = "#ff1000"
logger = mogdevice.logger


def wrap_except(arg):
    msg = 'Failed to execute function "__FUNC__"'
    if not callable(arg):
        msg = arg

    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as E:
                logger.exception(msg.replace("__FUNC__", func.__name__))
        return wrapped

    if callable(arg):
        return wrapper(arg)
    return wrapper


@contextmanager
def blocked(*args):
    s = [w.blockSignals(True) for w in args]
    try:
        yield
    finally:
        for w, v in zip(args, s):
            w.blockSignals(v)


def MOGIcon():
    return QtGui.QIcon(resource_path("moglabs_ico.png", True))


class MOGDialog(QtWidgets.QDialog):
    def __init__(self, title, parent=None, modal=False):
        super(MOGDialog, self).__init__(None)
        self.setWindowTitle(title)
        self.setWindowIcon(MOGIcon())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setModal(modal)

    def setWindowTitle(self, title):
        if getattr(self, "dev", None) is not None:
            info = self.dev.info
            title += " - %s %s" % (info[0], info[-1])
        super(MOGDialog, self).setWindowTitle(title)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            e.ignore()
        else:
            super(MOGDialog, self).keyPressEvent(e)


class HLine(QtWidgets.QFrame):
    def __init__(self, parent):
        super(HLine, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setMaximumHeight(2)
        self.setMinimumHeight(2)


class EditBox(QtWidgets.QLineEdit):
    def __init__(self, text, parent, align=QtCore.Qt.AlignCenter, fontsize=None, readOnly=False):
        super(EditBox, self).__init__(text, parent)
        self.setAlignment(align)
        self.setTextMargins(4, 4, 4, 4)
        if fontsize is not None:
            font = self.font()
            font.setPointSize(fontsize)
            self.setFont(font)
        if readOnly:
            self.setReadOnly(True)

    def setReadOnly(self, val=True, dark=False):
        super(EditBox, self).setReadOnly(val)
        if dark:
            self.setBackground("#d0d0d0")

    def setBackground(self, col):
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Base, QtGui.QColor(col))
        self.setPalette(pal)

    def mouseDoubleClickEvent(self, e):
        self.selectAll()
        e.accept()

    def keyPressEvent(self, e):
        if e.matches(QtGui.QKeySequence.Copy):
            self.copy()
            self.deselect()
        else:
            super(EditBox, self).keyPressEvent(e)


class SpacerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


class LabelledWidget(QtWidgets.QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(LabelledWidget, self).__init__(parent)
        box = QtWidgets.QHBoxLayout(self)
        padding = kwargs.get("padding", 10)
        box.setContentsMargins(padding, 0, padding, 0)
        spacing = kwargs.get("spacing", 5)
        box.setSpacing(spacing)
        for w in args:
            if isinstance(w, QtWidgets.QWidget):
                box.addWidget(w, stretch=1)
            else:
                box.addWidget(QtWidgets.QLabel(w, self), stretch=0)
        if "maxWidth" in kwargs:
            self.setMaximumWidth(kwargs["maxWidth"])


class PushButton(QtWidgets.QPushButton):
    def __init__(self, str, parent=None):
        QtWidgets.QPushButton.__init__(self, str, parent)
        self.setAutoDefault(False)


_QAction = getattr(QtWidgets, 'QAction', None) or QtGui.QAction


class CheckedAction(_QAction):
    def __init__(self, parent, name, slot, tooltip=None):
        _QAction.__init__(self, name, parent)
        self.setCheckable(True)
        self.setStatusTip(tooltip)
        self.toggled.connect(slot)
        parent.addAction(self)

    def setCheckedSilent(self, b):
        self.blockSignals(True)
        self.setChecked(b)
        self.blockSignals(False)


class LEDIndicator(QtWidgets.QAbstractButton):
    def __init__(self, parent, col='G', enabled=True):
        super(LEDIndicator, self).__init__(parent)
        self.setCheckable(True)
        self.setMinimumSize(32, 32)
        self.setBase(col)
        self.setEnabled(enabled)

    def setBase(self, set):
        if set == "G":
            self.setColors("#00ff00", "#00c000", "#001c00", "#00c000")
        elif set == "R":
            self.setColors("#ff0000", "#d00002", "#1c0000", "#9c0002")
        elif set == "Y":
            self.setColors("#ffff00", "#d0d000", "#808000", "#aaaa00")
        elif set == "B":
            self.setColors("#2080ff", "#0000f0", "#00001c", "#00009c")
        elif set == "K":
            self.setColors("#808080", "#101010", "#606060", "#101010")
        else:
            raise ValueError("Unknown color")

    def setColors(self, on1, on2, off1, off2):
        self.onColor1 = QtGui.QColor(on1)
        self.onColor2 = QtGui.QColor(on2)
        self.offColor1 = QtGui.QColor(off1)
        self.offColor2 = QtGui.QColor(off2)
        self.update()

    def resizeEvent(self, evt):
        self.update()

    def paintEvent(self, evt):
        real_size = min(self.width(), self.height())
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(real_size / 1000.0, real_size / 1000.0)

        def do_gradient(x, y, r, c1, c2):
            gradient = QtGui.QRadialGradient(x, y, 1500, x, y)
            gradient.setColorAt(0, c1)
            gradient.setColorAt(1, c2)
            painter.setPen(pen)
            painter.setBrush(gradient)
            painter.drawEllipse(QtCore.QPointF(0, 0), r, r)

        g1 = QtGui.QColor(224, 224, 224)
        g2 = QtGui.QColor(28, 28, 28)
        do_gradient(-500, -500, 500, g1, g2)
        do_gradient(500, 500, 450, g1, g2)
        if self.isChecked():
            do_gradient(-500, -500, 400, self.onColor1, self.onColor2)
        else:
            do_gradient(500, 500, 400, self.offColor1, self.offColor2)


class HexSpinner(QtWidgets.QSpinBox):
    """A custom integer spinbox implementation that validates hexadecimal"""

    def __init__(self, max=None, format=None, parent=None):
        self.validator = QtGui.QRegExpValidator(QtCore.QRegExp("^(0x)?[0-9A-F]+$", QtCore.Qt.CaseInsensitive))
        self.format = "%X" if format is None else format
        super(HexSpinner, self).__init__(parent)
        self.setPrefix("0x")
        self.setKeyboardTracking(False)
        self.lineEdit().setValidator(self.validator)
        self.lineEdit().setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        if max is not None:
            self.setRange(0, max)

    def textFromValue(self, val):
        return self.format % val

    def valueFromText(self, text):
        return int(text, 0)

    def validate(self, input, pos):
        return self.validator.validate(input, pos)

    def stepBy(self, steps):
        """Custom step function that allows specific digits within the number to be changed"""
        sel0 = self.lineEdit().selectionStart()
        sel1 = len(self.lineEdit().selectedText())
        sel_x = len(self.lineEdit().text()) - sel1 - sel0
        if sel0 < 0 or sel_x > len(self.cleanText()):
            sel0, sel1, sel_x = sel_x - 2, 1, 0
        steps *= 1 << 4 * sel_x
        self.setValue(self.value() + steps)
        self.lineEdit().setSelection(sel0, sel1)


class DblSpinner(QtWidgets.QDoubleSpinBox):
    def __init__(self, max=None, min=None, decimals=None, step=None, units=None, default=None, readonly=False, parent=None):
        super(DblSpinner, self).__init__(parent)
        if min is not None:
            self.setMinimum(min)
        if max is not None:
            self.setMaximum(max)
        if decimals is not None:
            self.setDecimals(decimals)
        if step is not None:
            self.setSingleStep(step)
        if units is not None:
            self.setSuffix(" " + units)
        if default is not None:
            self.setValue(default)
        if readonly:
            self.setReadOnly(True)
        self.setKeyboardTracking(False)
        self._limiter = QtCore.QTimer(self)
        self._limiter.setSingleShot(True)
        self._limiter.setInterval(250)
        self._limiter.timeout.connect(self.activateSteps)
        self._nsteps = 0

    def stepBy(self, steps):
        """Custom step function to rate-limit events being raised"""
        if self._limiter.isActive():
            self._nsteps += steps
        else:
            self._limiter.start()
            super(DblSpinner, self).stepBy(steps)

    def activateSteps(self):
        """Execute any accumulated step instructions after some timeout"""
        super(DblSpinner, self).stepBy(self._nsteps)
        self._nsteps = 0

    def setReading(self, val):
        """Set the displayed value from a floating point or string value (with units)"""
        if self.hasFocus():
            return
        if isinstance(val, str):
            val = mogdevice.convert_measurement(val, self.suffix().strip())
        with blocked(self):
            self.setValue(val)


class IntSpinner(QtWidgets.QSpinBox):
    def __init__(self, max=None, min=None, step=None, units=None, default=None, readonly=False, parent=None):
        super(IntSpinner, self).__init__(parent)
        if min is not None:
            self.setMinimum(min)
        if max is not None:
            self.setMaximum(max)
        if step is not None:
            self.setSingleStep(step)
        if units is not None:
            self.setSuffix(" " + units)
        if default is not None:
            self.setValue(default)
        if readonly:
            self.setReadOnly(True)
        self.setKeyboardTracking(False)
        self._limiter = QtCore.QTimer(self)
        self._limiter.setSingleShot(True)
        self._limiter.setInterval(250)
        self._limiter.timeout.connect(self.activateSteps)
        self._nsteps = 0

    def stepBy(self, steps):
        """Custom step function to rate-limit events being raised"""
        if self._limiter.isActive():
            self._nsteps += steps
        else:
            self._limiter.start()
            super(IntSpinner, self).stepBy(steps)

    def activateSteps(self):
        """Execute any accumulated step instructions after some timeout"""
        super(IntSpinner, self).stepBy(self._nsteps)
        self._nsteps = 0

    def setReading(self, val):
        """Set the displayed value from a floating point or string value (with units)"""
        if self.hasFocus():
            return
        if isinstance(val, str):
            val = mogdevice.convert_measurement(val, self.suffix().strip())
        with blocked(self):
            self.setValue(int(val))


class DeviceConnectionLabel(QtWidgets.QLabel):
    def __init__(self, type='', dev=None, parent=None):
        super(DeviceConnectionLabel, self).__init__(parent)
        self.type = type
        self.setDevice(dev)
        self.setContentsMargins(10, 5, 10, 5)

    def setDevice(self, dev):
        msg = self.type
        if len(msg):
            msg += ": "
        msg += "%s (%s)" % (dev.info[-1], dev.connection) if dev is not None else "Not connected"
        self.setText(msg)


def mouse_busy(busy):
    if busy:
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    else:
        QtWidgets.QApplication.restoreOverrideCursor()


def do_events():
    QtWidgets.QApplication.processEvents()


def file_dialog(parent, caption, filter, readonly, return_filter=False, dir=None, initial=None):
    settings = QtCore.QSettings()
    if dir is None:
        dir = settings.value("lastdir", "")
    if initial is None:
        initial = dir
    elif dir != "":
        if not path.isabs(initial):
            initial = path.join(dir, initial)
    if readonly:
        name, filter = QtWidgets.QFileDialog.getOpenFileName(parent, caption, initial, filter)
    else:
        name, filter = QtWidgets.QFileDialog.getSaveFileName(parent, caption, initial, filter)
    if name == "":
        if return_filter:
            return (None, None)
        return None
    settings.setValue("lastdir", path.dirname(name))
    settings.sync()
    if return_filter:
        return (name, filter)
    return name


def prog_bar(text, max, parent=None, btext='Abort', title='mogtools'):
    prog = QtWidgets.QProgressDialog(text, btext, 0, max, parent)
    prog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    prog.setWindowTitle(title)
    prog.setWindowIcon(QtGui.QIcon(resource_path("moglabs.ico", True)))
    prog.setAutoReset(False)
    prog.setMinimumDuration(0)
    prog.setWindowModality(QtCore.Qt.ApplicationModal)
    prog.setModal(True)
    prog.setMinimumSize(400, 50)
    prog.show()
    return prog


def ui_sleep(interval):
    tend = time.time() + interval
    while time.time() < tend:
        do_events()


def msgbox_critical(ex, parent=None, title='Error'):
    msg = "<font color=red><b>ERROR:</b></font> " + str(ex)
    return QtWidgets.QMessageBox.critical(parent, title, msg)


def msgbox_deverr(text, exc, parent=None, title='Error'):
    if isinstance(exc, mogdevice.DeviceError):
        text += "<p>Query: " + exc.query
    return msgbox_critical(text + "<p><font color=red>" + str(exc), parent, title)


def msgbox_yesno(parent, title, text):
    return QtWidgets.QMessageBox.question(parent, title, text,
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes


def msgbox_info(parent, title, text):
    QtWidgets.QMessageBox.information(parent, title, text)


def msgbox_NIY(parent):
    msgbox_critical("Not implemented yet.<p>Please consult the product manual or MOGLabs support for alternatives.", parent)


def msgbox_about(parent, app, app_desc, app_ver, *devs, **kwargs):
    msg = "<b>{APP} v{VER}</b><br>{DESC}<br>&copy; {YEAR} MOGLabs Inc".format(
        APP=app, DESC=app_desc, VER=app_ver, YEAR=time.strftime("%Y"))
    devinfo = ""
    for dev in devs:
        if dev is not None:
            if len(devinfo):
                devinfo += "<br>"
            info = dev.ask("INFO").split(" ")
            devinfo += "Model: %s %s<br>Serial: %s<br>" % (info[0], info[1], info[-1])
            vers = dev.ask_dict("VER")
            for item in vers.items():
                devinfo += "%s: v%s<br>" % item
    if len(devinfo):
        msg += "<p><u>Device information:</u><br>" + devinfo
    msg += kwargs.get("append", "")
    QtWidgets.QMessageBox.information(parent, "About", msg)


def resource_path(filename, ui=False):
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        if ui:
            base = path.dirname(path.abspath(__file__))
        else:
            base = path.abspath(".")
    p = path.join(base, filename)
    logger.debug("Loading " + p)
    return p


def isotime():
    return time.strftime("%y%m%dT%H%M%S")


def export_image(ui_elem, filename=None):
    if hasattr(ui_elem, "grab"):
        pix_map = ui_elem.grab()
    else:
        pix_map = QtGui.QPixmap.grabWidget(ui_elem)
    if filename is None:
        filename = file_dialog(ui_elem, "Select output file", "Rastered image (*.png *.bmp)", False,
            initial=time.strftime("%y%m%dT%H%M%S.png"))
        if filename is None:
            return
    pix_map.save(filename)
    return filename


def save_ui_elems(filename, elems, section=None):
    if filename is None:
        filename = file_dialog(None, "Save settings as", "*.ini", readonly=False)
        if filename is None:
            return
    if len(filename):
        settings = QtCore.QSettings(filename, QtCore.QSettings.IniFormat)
    else:
        settings = QtCore.QSettings()
    if section is not None:
        settings.beginGroup(section)
    for name, ctrl in elems.items():
        if isinstance(ctrl, QtWidgets.QCheckBox) or isinstance(ctrl, QtWidgets.QAction):
            settings.setValue(name, str(ctrl.isChecked()))
        elif isinstance(ctrl, QtWidgets.QLineEdit):
            settings.setValue(name, ctrl.text())
        elif isinstance(ctrl, QtWidgets.QComboBox):
            settings.setValue(name, ctrl.currentText())
        elif hasattr(ctrl, "value"):
            settings.setValue(name, str(ctrl.value()))
        elif hasattr(ctrl, "getRegion"):
            settings.setValue(name, list(map(str, ctrl.getRegion())))
        elif hasattr(ctrl, "toPlainText"):
            settings.setValue(name, ctrl.toPlainText())
        else:
            print("Unknown object", repr(ctrl))
    settings.sync()
    return filename


def load_ui_elems(filename, elems, section=None):
    if filename is None:
        filename = file_dialog(None, "Open settings", "*.ini", readonly=True)
        if filename is None:
            return
    if len(filename):
        settings = QtCore.QSettings(filename, QtCore.QSettings.IniFormat)
    else:
        settings = QtCore.QSettings()
    if section is not None:
        settings.beginGroup(section)
    for name, ctrl in elems.items():
        if not settings.contains(name):
            continue
        val = settings.value(name)
        if isinstance(ctrl, QtWidgets.QCheckBox) or isinstance(ctrl, QtWidgets.QAction):
            val = val.lower() in ('true', '1')
            ctrl.setChecked(val)
        elif isinstance(ctrl, QtWidgets.QLineEdit):
            ctrl.setText(val)
            ctrl.editingFinished.emit()
        elif isinstance(ctrl, QtWidgets.QComboBox):
            i = ctrl.findText(val)
            if i >= 0:
                ctrl.setCurrentIndex(i)
            else:
                ctrl.setEditText(val)
        elif hasattr(ctrl, "setValue"):
            ctrl.setValue(float(val))
        elif hasattr(ctrl, "setRegion"):
            ctrl.setRegion(list(map(float, val)))
        elif hasattr(ctrl, "setPlainText"):
            ctrl.setPlainText(val)
    return filename


def save_geometry(settings, wnd, name):
    if settings is None:
        settings = QtCore.QSettings()
    settings.beginGroup(name)
    settings.setValue("geom", wnd.geometry())
    settings.setValue("max", wnd.isMaximized())
    settings.endGroup()
    settings.sync()


def load_geometry(settings, wnd, name, default_sz=None):
    if settings is None:
        settings = QtCore.QSettings()
    settings.beginGroup(name)
    if settings.contains("geom"):
        wnd.setGeometry(settings.value("geom"))
    elif default_sz is not None:
        wnd.resize(*default_sz)
    if settings.value("max", 0) == "true":
        wnd.showMaximized()
    settings.endGroup()


def show_window(wnd):
    wnd.show()
    wnd.setWindowState(wnd.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
    wnd.activateWindow()
    wnd.raise_()


def exit_app():
    QtCore.QCoreApplication.exit()


def offer_IAP_FWUPD(dev, parent=None):
    info = dev.ask("INFO")
    if "IAP" not in info or "MWM" in info:
        return False
    if msgbox_yesno(parent, "Firmware update?",
                    "Device is in <b>firmware update mode</b>.<p>Launch firmware update tool?"):
        from .firmwareui import FirmwareUI
        wnd = FirmwareUI(dev, parent=parent, modal=True)
        wnd.exec_()
    return "IAP" in dev.ask("INFO")


def cmdline_start(cls, filter=None, attempt=None, debug=False, timeout=1, check_IAP=True, params=None, msg=None, title=None, **kwargs):
    if params is None:
        params = {}
    logging.basicConfig()
    if debug:
        logger.setLevel(logging.DEBUG)
        try:
            logerr = logging.FileHandler("mogdebug.log", "w")
            logerr.setLevel(logging.DEBUG)
            logerr.setFormatter(logging.Formatter("[MOG:%(levelname)s] %(message)s"))
            logger.addHandler(logerr)
        except Exception as E:
            logger.warning("Cannot access log file: %s" % E)

    # Platform-specific DPI awareness (Windows only)
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(0)
        except Exception:
            logger.info("Failed to set DPI awareness")

    if cls is not None:
        import inspect
        if sys.version_info < (3, 6, 0):
            argspec = inspect.getargspec(cls.__init__)
        else:
            argspec = inspect.getfullargspec(cls.__init__)
        if "mog" in argspec[0]:
            params["mog"] = "--mog" in sys.argv
            if params["mog"]:
                sys.argv.remove("--mog")

    app = QtWidgets.QApplication(sys.argv[2:])
    app.setOrganizationName("MOGLabs")
    app.setOrganizationDomain("moglabs.com")
    if cls is not None:
        app.setApplicationName(cls.__name__)

    # Platform-specific taskbar icon (Windows only)
    if platform.system() == "Windows":
        try:
            import ctypes
            myappid = "MOGLabs.%s" % cls.__name__
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    dev = None
    if len(sys.argv) > 1:
        addr = sys.argv[1]
        try:
            if addr == "-":
                attempt = addr
            else:
                dev = mogdevice.MOGDevice(addr, timeout=timeout, **kwargs)
        except Exception as E:
            if attempt != "-":
                msgbox_critical("Failed to connect to %s:<br>%s" % (addr, E))
                sys.exit(1)

    if attempt != "-":
        if attempt is not None:
            try:
                dev = mogdevice.MOGDevice(attempt, timeout=timeout, **kwargs)
            except Exception as E:
                logging.debug('Connection to "%s" failed' % attempt)

        if dev is None:
            try:
                from . import discoverui
            except ImportError:
                import discoverui
            dev = discoverui.discover(filter=filter, msg=msg, timeout=timeout, **kwargs)
            if dev is None:
                sys.exit(1)

    if cls is None:
        return (app, dev)

    if check_IAP and dev is not None:
        if offer_IAP_FWUPD(dev, None):
            msgbox_critical("Device must be rebooted out of firmware update mode to access application functionality")
            sys.exit(1)

    try:
        wnd = cls(dev, **params)
        wnd.show()
    except Exception as E:
        msgbox_critical("Failed to initialise application:<br>" + str(E))
        raise

    sys.exit(app.exec_())
