"""Eagle Eye device interface - stub for cross-platform compatibility"""
import logging
logger = logging.getLogger(__name__)


class EagleEye:
    def __init__(self, dev=None):
        self.dev = dev
        self.connected = dev is not None

    def read(self):
        if not self.connected:
            return None
        try:
            return self.dev.ask("EE,READ")
        except Exception as e:
            logger.warning("EagleEye read failed: %s" % e)
            return None
