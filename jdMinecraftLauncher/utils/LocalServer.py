from PyQt6.QtCore import QObject, QCoreApplication, pyqtSignal
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from ..core.ActionManager import ActionManager
from typing import Optional, Type
import traceback
import platform
import uuid
import json
import sys


class _LocalServerConnection(QObject):
    closed = pyqtSignal(str)

    def __init__(self, connectionID: str, socket: QLocalSocket) -> None:
        super().__init__()

        self._actionManager = ActionManager.getInstance()
        self._connectionID = connectionID
        self._socket = socket

        self._socket.readyRead.connect(self._readData)
        self._socket.disconnected.connect(lambda: self.closed.emit(self._connectionID))

    def _handleData(self, data: bytes) -> None:
        msg = json.loads(data.decode("utf-8"))

        match msg["action"]:
            case "OpenURI":
                if platform.system() == "Windows":
                    from jdMinecraftLauncher.gui.MainWindow.MainWindow import MainWindow

                    reply = {"action": "SetForegroundWindow", "windowID": int(MainWindow.getInstance().effectiveWinId())}
                else:
                    reply = {"action": "done"}

                self._socket.write(json.dumps(reply).encode("utf-8"))
                self._socket.waitForBytesWritten()

                self._actionManager.openURI(msg["uri"])

    def _readData(self) -> None:
        data = self._socket.readAll().data()

        try:
            self._handleData(data)
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)


class LocalServer(QObject):
    _instance: Optional["LocalServer"] = None

    def __init__(self) -> None:
        super().__init__()

        self._server = QLocalServer(self)
        self._connections: dict[str, _LocalServerConnection] = {}

        self._server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)

        if self._server.listen(self.getServerName()):
            self._server.newConnection.connect(self._newConnection)
        else:
            print(QCoreApplication.translate("LocalServer", "Unable to start local server: {{message}}").replace("{{message}}", self._server.errorString()), file=sys.stderr)

    def _newConnection(self) -> None:
        socket = self._server.nextPendingConnection()
        if socket is None:
            return

        connectionID = str(uuid.uuid4())

        connection = _LocalServerConnection(connectionID, socket)
        connection.closed.connect(self._connectionClosed)
        self._connections[connectionID] = connection

    def _connectionClosed(self, connectionID: str) -> None:
        del self._connections[connectionID]

    @classmethod
    def start(cls: Type["LocalServer"]) -> None:
        cls._instance = cls()

    @staticmethod
    def getServerName() -> str:
        return "jdMinecraftLauncher"
