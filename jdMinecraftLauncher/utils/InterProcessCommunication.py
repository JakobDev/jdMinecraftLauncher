from PyQt6.QtDBus import QDBusConnection, QDBusMessage
from PyQt6.QtNetwork import QLocalSocket
from .LocalServer import LocalServer
from typing import Optional
import traceback
import platform
import ctypes
import json
import sys
import os


_instance: Optional["BaseIPC"] = None


class BaseIPC:
    def startup(self) -> None:
        pass

    def isAlreadyRunning(self) -> bool:
        return False

    def openURI(self, uri: str) -> None:
        pass


class WindowsIPC(BaseIPC):
    def __init__(self) -> None:
        self._socket = QLocalSocket()
        self._socket.connectToServer(LocalServer.getServerName())
        self._socket.waitForConnected()

    def startup(self) -> None:
        LocalServer.start()

    def isAlreadyRunning(self) -> bool:
        return self._socket.state() == QLocalSocket.LocalSocketState.ConnectedState

    def _handleSocketData(self, data: bytes) -> None:
        msg = json.loads(data.decode("utf-8"))

        match msg["action"]:
            case "SetForegroundWindow":
                ctypes.windll.user32.SetForegroundWindow(msg["windowID"])  # type: ignore[attr-defined]

    def openURI(self, uri: str) -> None:
        msg = {"action": "OpenURI", "uri": uri}
        data = json.dumps(msg).encode("utf-8")

        self._socket.writeData(data)
        self._socket.waitForBytesWritten()

        self._socket.waitForReadyRead()
        data = self._socket.readAll().data()

        try:
            self._handleSocketData(data)
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)


class LinuxIPC(BaseIPC):
    def isAlreadyRunning(self) -> bool:
        msg = QDBusMessage.createMethodCall("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "ListNames")
        resp = QDBusConnection.sessionBus().call(msg)

        if resp.errorName() != "":
            print(f"{resp.errorName()}: {resp.errorMessage()}", file=sys.stderr)
            return False

        return "page.codeberg.JakobDev.jdMinecraftLauncher" in resp.arguments()[0]

    def openURI(self, uri: str) -> None:
        msg = QDBusMessage.createMethodCall("page.codeberg.JakobDev.jdMinecraftLauncher", "/", "page.codeberg.JakobDev.jdMinecraftLauncher", "OpenURI")
        msg.setArguments([uri, os.getenv("XDG_ACTIVATION_TOKEN", "")])

        resp = QDBusConnection.sessionBus().call(msg)
        if resp.errorName() != "":
            print(f"{resp.errorName()}: {resp.errorMessage()}", file=sys.stderr)


def getIPC() -> BaseIPC:
    global _instance

    if _instance is not None:
        return _instance

    match platform.system():
        case "Windows":
            _instance = WindowsIPC()
        case "Linux":
            _instance = LinuxIPC()
        case _:
            _instance = BaseIPC()

    return _instance
