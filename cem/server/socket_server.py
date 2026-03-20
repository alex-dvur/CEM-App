"""Socket server for CEM remote control - stub"""
import logging
import socket
import threading

logger = logging.getLogger(__name__)


class SocketServer:
    def __init__(self, port=7803, parent=None):
        self.port = port
        self.parent = parent
        self._running = False
        self._thread = None
        self._server = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._server:
            try:
                self._server.close()
            except Exception:
                pass

    def _serve(self):
        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind(('', self.port))
            self._server.listen(1)
            self._server.settimeout(1.0)
            logger.info("CEM server listening on port %d" % self.port)
            while self._running:
                try:
                    conn, addr = self._server.accept()
                    logger.info("Connection from %s" % str(addr))
                    self._handle_client(conn)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        logger.error("Server error: %s" % e)
        except Exception as e:
            logger.error("Failed to start server: %s" % e)

    def _handle_client(self, conn):
        try:
            conn.settimeout(5.0)
            data = conn.recv(4096)
            if data:
                response = self._process_command(data.decode('utf-8', errors='replace').strip())
                conn.sendall(response.encode())
        except Exception as e:
            logger.warning("Client error: %s" % e)
        finally:
            conn.close()

    def _process_command(self, cmd):
        return "OK"
