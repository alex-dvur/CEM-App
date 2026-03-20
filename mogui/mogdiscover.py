try:
    from .mogdevice import MOGDevice
except ImportError:
    from mogdevice import MOGDevice

import logging
import platform
import socket
import select
import time

try:
    import psutil
except ImportError:
    psutil = None

try:
    from serial.tools import list_ports
except ImportError:
    list_ports = None


def check_filter(info, filter):
    if filter is None:
        return True
    parts = info.split(" ", 1)
    return any(x in parts[0] for x in filter)


def check_connection(addr, filter=None, name=None, timeout=1):
    try:
        dev = MOGDevice(addr, timeout=timeout, check=True)
        info = dev.ask("INFO")
        if not check_filter(info, filter):
            dev.close()
            return None
        if name is not None and name not in info:
            dev.close()
            return None
        return (addr, info)
    except Exception:
        return None


def find_usb(filter=None, name=None, abort=None):
    if list_ports is None:
        return
    for portinfo in list_ports.comports():
        if abort is not None and abort():
            return
        port = portinfo.device
        logging.info("Testing USB port %s" % port)
        res = check_connection(port, filter, name)
        if res is not None:
            yield res


def find_eth(filter=None, name=None, abort=None, port=7802):
    if psutil is None:
        logging.warning("psutil not available, skipping ethernet discovery")
        return
    myips = [x.address for i, s in psutil.net_if_addrs().items()
             for x in iter(s) if x.family == socket.AF_INET if x.address != "127.0.0.1"]
    logging.info("Broadcasting for devices from " + str(myips))
    bcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    bcast.settimeout(0.1)
    try:
        bcast.bind(("", port))
    except OSError:
        logging.warning("Could not bind to port %d for discovery" % port)
        return
    for ip in myips:
        bcast.sendto(ip.encode(), ('255.255.255.255', port))
    found = []
    timeout_time = time.time() + 2
    while time.time() < timeout_time:
        if abort is not None and abort():
            return
        readers, writers, errors = select.select([bcast], [], [], 0.1)
        if not len(readers):
            continue
        msg, origin = bcast.recvfrom(32)
        addr, remote_port = origin
        if addr in myips:
            continue
        if addr in found:
            continue
        found.append(addr)
        res = check_connection(addr, filter, name)
        if res is not None:
            yield res


def find_device(filter=None, name=None, timeout=30):
    timeout_time = time.time() + timeout
    while time.time() < timeout_time:
        for addr, info in find_usb(filter, name):
            return MOGDevice(addr)
        for addr, info in find_eth(filter, name):
            return MOGDevice(addr)
    raise RuntimeError("Device not found")
