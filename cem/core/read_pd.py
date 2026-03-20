"""Photodiode reading module - reconstructed stub"""
import logging
logger = logging.getLogger(__name__)


def read_photodiode(dev, channel=1):
    """Read photodiode value from device"""
    if dev is None:
        return 0.0
    try:
        return dev.ask_val("PD,%d" % channel)
    except Exception as e:
        logger.warning("Failed to read photodiode: %s" % e)
        return 0.0
