from PyQt6.QtWidgets import QPlainTextEdit, QMessageBox
from PyQt6.QtCore import QProcess, QCoreApplication
from typing import TYPE_CHECKING
import shutil
import sys


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow
    from ...Profile import Profile


class GameOutputTab(QPlainTextEdit):
    def __init__(self, env: "Environment", mainWindow: "MainWindow") -> None:
        super().__init__()

        self._env = env
        self._mainWindow = mainWindow

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setReadOnly(True)

    def dataReady(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(bytes(self.process.readAll()).decode(encoding=sys.stdout.encoding, errors="replace"))  # type: ignore
        self.moveCursor(cursor.MoveOperation.End)

    def procStarted(self) -> None:
        if self.profile.launcherVisibility != 2:
            self._mainWindow.hide()
        self._mainWindow.playButton.setEnabled(self._env.settings.get("enableMultiLaunch"))

    def procFinish(self) -> None:
        if self.profile.launcherVisibility == 0:
            self._mainWindow.show()
            self._mainWindow.setFocus()
        elif self.profile.launcherVisibility == 1:
            self._mainWindow.close()

        self._mainWindow.playButton.setEnabled(True)

        if self.natives_path != "":
            try:
                shutil.rmtree(self.natives_path)
            except Exception:
                pass

    def executeCommand(self, profile: "Profile", command: list[str], natives_path: str) -> None:
        self.profile = profile
        self.natives_path = natives_path
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.setWorkingDirectory(profile.getGameDirectoryPath())
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.procStarted)
        self.process.finished.connect(self.procFinish)
        self.process.start(command[0], command[1:])

        if not self.process.waitForStarted():
            self.setPlainText(QCoreApplication.translate("GameOutputTab", "Failed to start Minecraft"))
            QMessageBox.critical(self, QCoreApplication.translate("GameOutputTab", "Failed to start"), QCoreApplication.translate("GameOutputTab", "Minecraft could not be started. Maybe you use a invalid Java executable."))
            self._mainWindow.playButton.setEnabled(True)
            return

        # There are some cases e.g. when failing to init a window where Minecraft uses tinyfiledialogs to output an error message
        # When DISPLAY is not set (e.g. on Wayland mode) it writes to the terminal and waits for the user to press enter
        # So we simulate a enter press here, so it does not hang, as this is not a TTY which supports a key press
        self.process.write(b"\n")
        self.process.closeWriteChannel()
