"""
moglabs device class
Simplifies communication with moglabs devices

Compatible with both python2 and python3

(c) MOGLabs 2016--2020
http://www.moglabs.com/
"""
import time
import socket
import serial
import select
from struct import unpack
from collections import OrderedDict
import logging
import threading

logger = logging.getLogger("MOG")
CRLF = b'\r\n'


class DeviceError(RuntimeError):
    def __init__(self, resp, query=None, dev=None):
        self.resp = resp.strip() if isinstance(resp, str) else resp
        self.query = None if query is None else (query.strip() if isinstance(query, str) else query)
        self.dev = dev

    def __str__(self):
        return self.resp if isinstance(self.resp, str) else self.resp.decode('utf-8', errors='replace')

    def __repr__(self):
        s = 'DeviceError("%s"' % str(self).strip()
        if self.query is not None:
            s += ', tried "%s"' % self.query
        if self.dev is not None:
            s += ", <%s>" % self.dev.connection
        return s + ")"


class USBError(RuntimeError):
    def __init__(self, serialException):
        if "went wrong" in repr(serialException):
            s = "Error configuring USB port; unplug USB then try again"
        elif hasattr(serialException, 'args') and serialException.args and "ClearCommError" in str(serialException.args[0]):
            s = "Device disconnected"
        else:
            s = str(serialException.args[0]).split(":", 1)[0] if serialException.args else str(serialException)
        super(USBError, self).__init__(s)


def check_version(required_ver, test_ver):
    for a, b in zip(required_ver.split("."), test_ver.split(".")):
        a, b = int(a, 10), int(b, 10)
        if b > a:
            return True
        if b < a:
            return False
    return True


def convert_measurement(val, units_out, default_units="", type=float):
    units_in = default_units
    if isinstance(val, str):
        parts = val.split(",", 1)[0].split(" ")
        val = type(parts[0])
        if len(parts) > 1:
            units_in = parts[1]
    if units_out is None:
        return val
    if units_in == units_out:
        return val
    pows = {'T': 12, 'G': 9, 'M': 6, 'k': 3, 'm': -3, 'u': -6, 'n': -9, 'p': -12, 'f': -15}
    pow_in = pows.get(units_in[0], 0) if len(units_in) > 1 else 0
    if pow_in:
        units_in = units_in[1:]
    pow_out = pows.get(units_out[0], 0) if len(units_out) > 1 else 0
    if pow_out:
        units_out = units_out[1:]
    assert units_in == units_out, "Units mismatch"
    return val * 10 ** (pow_in - pow_out)


class MOGDevice(object):
    _info = None

    def __init__(self, addr, port=None, timeout=1, minver=None, check=True):
        assert len(addr), "No address specified"
        self.dev = None
        self._attempts = 0
        if addr.startswith("COM") or addr.startswith("/dev/") or addr == "USB":
            if port is not None:
                addr = "COM%d" % port
            addr = addr.split(" ", 1)[0]
            self.connection = addr
            self.is_usb = True
        else:
            if ":" not in addr:
                if port is None:
                    port = 7802
                addr = "%s:%d" % (addr, port)
            self.connection = addr
            self.is_usb = False
        self.lock = threading.Lock()
        self.reconnect(timeout, check)
        if minver is not None:
            ver = self.versions()["UC"]
            assert check_version(minver, ver), "Unsupported firmware version; Please update to v%s or newer" % minver

    def __repr__(self):
        return 'MOGDevice("%s")' % self.connection

    def close(self):
        if self.connected():
            self.dev.close()
            self.dev = None

    def reconnect(self, timeout=1, check=True):
        """Reestablish connection with unit"""
        self.close()
        if self._attempts < 0:
            self._attempts = 0
        self._attempts += 1
        with self.lock:
            if self.is_usb:
                try:
                    self.dev = serial.Serial(
                        self.connection, baudrate=115200, bytesize=8,
                        parity="N", stopbits=1, timeout=timeout, writeTimeout=0)
                except serial.SerialException as E:
                    raise USBError(E)
            else:
                self.dev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dev.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.dev.settimeout(timeout)
                addr, port = self.connection.split(":")
                self.dev.connect((addr, int(port)))
        if check:
            try:
                self.info(True)
            except Exception as E:
                logger.error(str(E))
                raise DeviceError("Device did not respond to query", "info", self)
        self._attempts = -self._attempts

    def connected(self):
        return self.dev is not None

    def _check(self):
        assert self.connected(), "Not connected"

    def info(self, query=False):
        """Return the INFO array, in Unicode"""
        if query or self._info is None:
            self._info = self.ask("info").split(" ", 3)
            if len(self._info) < 4:
                self._info.append("")
            self._info[3] = self._info[3].strip()
        return self._info

    def info_dict(self, query=False):
        """Parse the INFO statement, and return as a python dict"""
        import re
        parts = self.info(query)
        code, remainder = parts[1].split("-", 1)
        if "-" in remainder:
            remainder, revstr = remainder.rsplit("-", 1)
        else:
            revstr = remainder
            remainder = None
        is_iap = "IAP" in parts[2]
        match = re.search("(\\d+)$", revstr)
        if match is None:
            rev = 0
        else:
            rev = int(match.group(0))
        if " " in parts[3]:
            name, serial_num = parts[3].rsplit(" ", 1)
        else:
            name = serial_num = parts[3]
        return {
            'type': parts[0], 'serial': serial_num, 'name': name,
            'ver': parts[2], 'code': code, 'model': remainder,
            'rev': rev, 'iap': is_iap
        }

    def versions(self):
        """Query the dictionary of version numbers, in Unicode"""
        verstr = self.ask("version")
        if verstr == "Command not defined":
            raise DeviceError("Incompatible firmware", "ver", self)
        vers = {}
        if ":" in verstr:
            tk = "," if "," in verstr else "\n"
            for l in verstr.split(tk):
                if l.startswith("OK"):
                    continue
                n, v = l.split(":", 2)
                v = v.strip()
                if " " in v:
                    v = v.rsplit(" ", 2)[1].strip()
                vers[n.strip()] = v
        else:
            vers["UC"] = verstr.strip()
        return vers

    def cmd(self, cmd):
        """Send the specified command, and check the response is OK. Returns response in Unicode"""
        resp = self.ask(cmd)
        assert isinstance(resp, str), f"Invalid response to {cmd} command"
        if resp.startswith("OK"):
            return resp
        raise DeviceError(resp, cmd, self)

    def ask(self, cmd):
        """Send followed by receive, returning response in Unicode"""
        with self.lock:
            self._flush()
            self._send(cmd)
            resp = self._recv().strip()
        if isinstance(resp, bytes):
            resp = resp.decode('utf-8', errors='replace')
        if resp.startswith("ERR:"):
            raise DeviceError(resp[4:], cmd, self)
        return resp

    def ask_dict(self, cmd):
        """Send a request which returns a dictionary response"""
        resp = self.ask(cmd)
        assert isinstance(resp, str), f"Invalid response to {cmd} query"
        if resp.startswith("OK"):
            resp = resp[3:].strip()
        if ":" not in resp:
            raise DeviceError("Not a dictionary", cmd, self)
        splitchar = "," if "," in resp else "\n"
        vals = OrderedDict()
        parts = resp.split(":")
        key = parts[0]
        for part in parts[1:-1]:
            val, next_key = part.rsplit(splitchar, 1)
            vals[key.strip()] = val.strip()
            key = next_key
        vals[key.strip()] = parts[-1].rsplit(splitchar, 1)[0].strip()
        return vals

    def ask_bin(self, cmd):
        """Send a request which returns a binary response package, returned in Bytes"""
        with self.lock:
            self._send(cmd)
            head = self._recv_raw(4)
            if head == b'ERR:':
                raise DeviceError(self._recv().strip(), cmd, self)
            datalen = unpack("<L", head)[0]
            data = self._recv_raw(datalen)
        if len(data) != datalen:
            raise DeviceError("Incorrect length", cmd, self)
        return data

    def ask_val(self, query, units=None, type=float):
        """Requests a value then converts the first part of the response"""
        return convert_measurement(self.ask(query), units, type=type)

    def _send(self, cmd):
        """Send command, appending newline if not present"""
        if hasattr(cmd, "encode"):
            cmd = cmd.encode()
        if not cmd.endswith(CRLF):
            cmd += CRLF
        self._send_raw(cmd)

    def send(self, cmd):
        """Public send wrapper"""
        self._check()
        self._send(cmd)

    def has_data(self, timeout=0):
        """Check if there is data waiting"""
        self._check()
        if self.is_usb:
            if timeout == 0:
                return self.dev.in_waiting > 0
            return len(select.select([self.dev], [], [], timeout)[0]) > 0
        return len(select.select([self.dev], [], [], timeout)[0]) > 0

    def _flush(self, timeout=0, buffer=256):
        """Reads whatever data is sitting on the line"""
        dat = b""
        while self.has_data(timeout):
            chunk = self._recv(buffer)
            if isinstance(chunk, str):
                chunk = chunk.encode()
            dat += chunk
        if len(dat):
            logger.debug("Flushed" + repr(dat))
        return dat

    def flush(self, timeout=0, buffer=256):
        """Public flush wrapper"""
        return self._flush(timeout, buffer)

    def _recv(self, buffer=4096):
        """Receive data from device"""
        self._check()
        if self.is_usb:
            try:
                data = self.dev.read_until(CRLF, buffer)
            except serial.SerialException as E:
                raise USBError(E)
        else:
            data = self.dev.recv(buffer)
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='replace')
        return data

    def recv(self, buffer=4096):
        """Public receive wrapper"""
        return self._recv(buffer)

    def _send_raw(self, data):
        """Send raw bytes to device"""
        self._check()
        if self.is_usb:
            try:
                self.dev.write(data)
            except serial.SerialException as E:
                raise USBError(E)
        else:
            self.dev.sendall(data)

    def send_raw(self, data):
        """Public raw send wrapper"""
        self._send_raw(data)

    def _recv_raw(self, size):
        self._check()
        parts = []
        tout = time.time() + self.get_timeout()
        while size > 0:
            if self.is_usb:
                try:
                    chunk = self.dev.read(min(size, 8192))
                except serial.SerialException as E:
                    raise USBError(E)
            else:
                chunk = self.dev.recv(min(size, 8192))
            if time.time() > tout:
                raise DeviceError("timed out")
            parts.append(chunk)
            size -= len(chunk)
        buf = b''.join(parts)
        logger.debug("<< RECV_RAW got %d" % len(buf))
        logger.debug(repr(buf))
        return buf

    def recv_raw(self, size):
        """Public raw receive wrapper"""
        return self._recv_raw(size)

    def get_timeout(self):
        """Get the current device timeout"""
        if self.is_usb:
            return self.dev.timeout
        return self.dev.gettimeout()

    def set_timeout(self, timeout):
        """Set the device timeout"""
        if self.is_usb:
            self.dev.timeout = timeout
        else:
            self.dev.settimeout(timeout)


def load_script(filename):
    with open(filename, "r") as f:
        for linenum, line in enumerate(f):
            line = line.split("#", 1)[0]
            line = line.strip()
            if len(line) == 0:
                continue
            yield (linenum + 1, line)


def reconnectException(func):
    """Decorator to automatically reconnect on device errors"""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (DeviceError, USBError, OSError) as E:
            logger.warning("Connection error, attempting reconnect: %s" % E)
            try:
                self.dev.reconnect()
                return func(self, *args, **kwargs)
            except Exception:
                raise E
    return wrapper
