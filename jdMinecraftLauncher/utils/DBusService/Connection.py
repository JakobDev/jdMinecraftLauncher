from PyQt6.QtCore import QObject, QCoreApplication, pyqtSignal
from PyQt6.QtNetwork import QLocalSocket
from itertools import count
import jeepney
import time


class DBusConnection(QObject):
    message_received = pyqtSignal(jeepney.Message)

    def __init__(self, bus: str = "SESSION") -> None:
        super().__init__()

        self._socket = QLocalSocket()
        self._outgoing_serial = count(start=1)
        self._last_messages: list[jeepney.Message] = []
        self._parser = jeepney.Parser()

        self._socket.connectToServer(jeepney.bus.get_bus(bus))
        self._socket.waitForConnected()
        self._auth()

        self._socket.readyRead.connect(self._readData)

        resp = self.send_and_get_reply(jeepney.bus_messages.DBus().Hello())

        self.unique_name: str = resp.body[0]

    def _auth(self) -> None:
        authr = jeepney.auth.Authenticator(inc_null_byte=False)

        self._socket.writeData(b"\0")
        self._socket.waitForBytesWritten()

        for req_data in authr:
            self._socket.writeData(req_data)

            self._socket.waitForBytesWritten()
            self._socket.waitForReadyRead()

            authr.feed(self._socket.readData(1024))

        self._socket.writeData(jeepney.auth.BEGIN)
        self._socket.waitForBytesWritten()

    def _readData(self) -> None:
        data = self._socket.readAll().data()
        self._parser.add_data(data)

        self._last_messages.clear()
        while (msg := self._parser.get_next_message()) is not None:
            self._last_messages.append(msg)
            self.message_received.emit(msg)

    def send(self, msg: jeepney.Message, serial: int | None = None) -> None:
        if serial is None:
            serial = next(self._outgoing_serial)

        data = msg.serialise(serial=serial)
        self._socket.writeData(data)
        self._socket.waitForBytesWritten()

    def send_and_get_reply(self, msg: jeepney.Message, timeout: int = 100) -> jeepney.Message:
        serial = next(self._outgoing_serial)
        self.send(msg, serial)

        start_time = time.time()

        while True:
            QCoreApplication.processEvents()

            for msg in self._last_messages:
                if msg.header.fields.get(jeepney.HeaderFields.reply_serial, 0) == serial:
                    return msg

            if time.time() - start_time >= timeout:
                raise RuntimeError("timeout")
