import logging.config
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets

import mogui as ui
from mogui import MOGDevice
from cem import APP_TITLE, APP_VER, DebugModes
from cem import CEM_SN
from cem.cem_main import CEMApp

if __name__ == "__main__":
    if "--mog" in sys.argv:
        from cem.logging_configs import CEM_CONFIG_INTERNAL as CEM_LOGGING_CONFIG
    else:
        from cem.logging_configs import CEM_CONFIG_PRODUCTION as CEM_LOGGING_CONFIG

    logging.config.dictConfig(CEM_LOGGING_CONFIG)
    logger = logging.getLogger("cem")
    logger.info(APP_TITLE + " - v" + APP_VER)

    msg = "Select CEM. Unique configuration file will be loaded."

    for debug_mode in DebugModes:
        try:
            sys.argv.remove(f"--{debug_mode.name}")
            CEMApp.debug_mode = debug_mode
            logger.debug(f"Starting debug mode {debug_mode.name.upper()}.")
            break
        except ValueError:
            continue

    if CEMApp.debug_mode == DebugModes.offline:
        app = QtWidgets.QApplication(sys.argv[2:] if len(sys.argv) > 2 else [])
        app.setOrganizationName("MOGLabs")
        app.setOrganizationDomain("moglabs.com")
        app.setApplicationName(CEMApp.__name__)
        wnd = CEMApp(dev=None, cem_sn=CEM_SN)
        wnd.show()
        sys.exit(app.exec() if hasattr(app, 'exec') else app.exec_())
    else:
        direct_addr = None
        remaining = [a for a in sys.argv[1:] if not a.startswith("--")]
        if remaining:
            direct_addr = remaining[0]
            logger.info("Direct connection to: %s" % direct_addr)

        if direct_addr:
            app = QtWidgets.QApplication([])
            app.setOrganizationName("MOGLabs")
            app.setOrganizationDomain("moglabs.com")
            app.setApplicationName(CEMApp.__name__)
            try:
                dev = MOGDevice(direct_addr, timeout=3)
                wnd = CEMApp(dev, cem_sn=CEM_SN)
                wnd.show()
                sys.exit(app.exec() if hasattr(app, 'exec') else app.exec_())
            except Exception as e:
                logger.error("Failed to connect to %s: %s" % (direct_addr, e))
                from mogui.mogui import msgbox_critical
                msgbox_critical("Failed to connect to %s:<br>%s" % (direct_addr, e))
                sys.exit(1)
        else:
            ui.cmdline_start(CEMApp, filter="CEM", msg=msg)
