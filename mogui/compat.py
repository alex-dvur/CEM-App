from __future__ import print_function
import os

try:
    from PySide2 import QtGui, QtWidgets, QtCore
    from PySide2.QtCore import Qt
    os.environ["QT_API"] = "pyside2"
    os.environ["PYQTGRAPH_QT_LIB"] = "PySide2"
    IS_PYSIDE2 = True
except ImportError:
    try:
        from PySide6 import QtGui, QtWidgets, QtCore
        from PySide6.QtCore import Qt
        os.environ["QT_API"] = "pyside6"
        os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"
        IS_PYSIDE2 = True
    except ImportError:
        raise ImportError("PySide2 or PySide6 is required. Install with: pip install PySide6")

try:
    from .mogdevice import *
except ImportError:
    from mogdevice import *

import traceback
plugins = os.path.join(os.path.dirname(QtCore.__file__), "plugins")
QtCore.QCoreApplication.addLibraryPath(plugins)

try:
    from configparser import RawConfigParser as ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser
