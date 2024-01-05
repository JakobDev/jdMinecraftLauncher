from typing import TYPE_CHECKING
import traceback
import platform
import sys


if TYPE_CHECKING:
    from jdMinecraftLauncher.gui.MainWindow import MainWindow


class WindowIconProgressBase:
    def setProgress(self, value: float) -> None:
        pass

    def hide(self) -> None:
        pass

    def isSupported(self) -> bool:
        return False


class WindowIconProgressWindows(WindowIconProgressBase):
    def __init__(self, windowID: int) -> None:
        import PyTaskbar

        self._progress = PyTaskbar.Progress(windowID)
        self._progress.init()
        self._progress.setState("normal")

    def setProgress(self, value: float) -> None:
        self._progress.setProgress(int(value * 100))

    def hide(self) -> None:
        self._progress.setProgress(0)

    def isSupported(self) -> bool:
        return True


class WindowIconProgressUnix(WindowIconProgressBase):
    def __init__(self) -> None:
        from PyQt6.QtDBus import QDBusConnection, QDBusMessage

        self._connection = QDBusConnection.sessionBus()
        self._message = QDBusMessage.createSignal("/", "com.canonical.Unity.LauncherEntry", "Update")

    def setProgress(self, value: float) -> None:
        self._message.setArguments(("application://page.codeberg.JakobDev.jdMinecraftLauncher", {"progress": value, "progress-visible": True}))
        self._connection.send(self._message)

    def hide(self) -> None:
        self._message.setArguments(("application://page.codeberg.JakobDev.jdMinecraftLauncher", {"progress-visible": False}))
        self._connection.send(self._message)

    def isSupported(self) -> bool:
        return True


def createWindowIconProgress(mainWindow: "MainWindow") -> WindowIconProgressBase:
    try:
        if platform.system() == "Windows":
            try:
                return WindowIconProgressWindows(int(mainWindow.winId()))
            except ModuleNotFoundError:
                print("Could not import PyTaskbar", file=sys.stderr)
                return WindowIconProgressBase()
        elif platform.system() == "Linux":
            return WindowIconProgressUnix()
        else:
            return WindowIconProgressBase()
    except Exception:
        print("Could not create WindowIconProgress", file=sys.stderr)
        print(traceback.format_exc(), end="", file=sys.stderr)
        return WindowIconProgressBase()
