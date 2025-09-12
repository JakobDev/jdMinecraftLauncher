from PyQt6.QtWidgets import QPlainTextEdit, QMessageBox
from PyQt6.QtCore import QProcess, QCoreApplication
from ...RunMinecraft import getMinecraftCommand
from ...Constants import LauncherVisibility
from PyQt6.QtGui import QTextCursor
from ...Settings import Settings
from typing import TYPE_CHECKING
import tempfile
import shutil
import sys


if TYPE_CHECKING:
    from .MainWindow import MainWindow
    from ...Profile import Profile


class GameOutputTab(QPlainTextEdit):
    def __init__(self, mainWindow: "MainWindow", profile: "Profile") -> None:
        super().__init__()

        self._mainWindow = mainWindow
        self._profile = profile

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setReadOnly(True)

        self._nativesPath: str | None = None
        if Settings.getInstance().get("extractNatives"):
            self._nativesPath = tempfile.mktemp(prefix="minecraft_natives_")

        command = getMinecraftCommand(profile, self._nativesPath)
        self._command = command["command"]

        self._process = QProcess(self)
        self._process.setProcessEnvironment(command["env"])
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.setWorkingDirectory(profile.getGameDirectoryPath())
        self._process.readyRead.connect(self._dataReady)
        self._process.started.connect(self._procStarted)
        self._process.finished.connect(self._procFinish)

    def _dataReady(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(bytes(self._process.readAll()).decode(encoding=sys.stdout.encoding, errors="replace"))  # type: ignore
        self.moveCursor(QTextCursor.MoveOperation.End)

    def _procStarted(self) -> None:
        if self._profile.launcherVisibility != LauncherVisibility.KEEP_OPEN:
            self._mainWindow.hide()

        self._mainWindow.playButton.setEnabled(Settings.getInstance().get("enableMultiLaunch"))

    def _procFinish(self) -> None:
        match self._profile.launcherVisibility:
            case LauncherVisibility.HIDE:
                self._mainWindow.show()
                self._mainWindow.setFocus()
            case LauncherVisibility.CLOSE:
                self._mainWindow.close()

        self._mainWindow.playButton.setEnabled(True)

        if self._nativesPath is not None:
            try:
                shutil.rmtree(self._nativesPath)
            except Exception:
                pass

    def start(self):
        self._process.start(self._command[0], self._command[1:])

        if not self._process.waitForStarted():
            self.setPlainText(QCoreApplication.translate("GameOutputTab", "Failed to start Minecraft"))
            QMessageBox.critical(self, QCoreApplication.translate("GameOutputTab", "Failed to start"), QCoreApplication.translate("GameOutputTab", "Minecraft could not be started. Maybe you're using an invalid Java executable."))
            self._mainWindow.playButton.setEnabled(True)
            return

        # There are some cases e.g. when failing to init a window where Minecraft uses tinyfiledialogs to output an error message
        # When DISPLAY is not set (e.g. on Wayland mode) it writes to the terminal and waits for the user to press enter
        # So we simulate a enter press here, so it does not hang, as this is not a TTY which supports a key press
        self._process.write(b"\n")
        self._process.closeWriteChannel()
