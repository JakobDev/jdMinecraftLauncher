from PyQt6.QtWidgets import QPlainTextEdit, QMessageBox
from PyQt6.QtCore import QProcess, QCoreApplication
from typing import TYPE_CHECKING
import sys


if TYPE_CHECKING:
    from ...Environment import Environment
    from ...Profile import Profile


class GameOutputTab(QPlainTextEdit):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setReadOnly(True)

    def dataReady(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(bytes(self.process.readAll()).decode(encoding=sys.stdout.encoding,errors="replace"))
        self.moveCursor(cursor.MoveOperation.End)

    def procStarted(self) -> None:
        if self.profile.launcherVisibility != 2:
            self.env.mainWindow.hide()
        self.env.mainWindow.playButton.setEnabled(self.env.settings.get("enableMultiLaunch"))

    def procFinish(self) -> None:
        if self.profile.launcherVisibility == 0:
            self.env.mainWindow.show()
            self.env.mainWindow.setFocus()
        elif self.profile.launcherVisibility == 1:
            self.env.mainWindow.close()

        self.env.mainWindow.playButton.setEnabled(True)

        if self.natives_path != "":
            try:
                shutil.rmtree(self.natives_path)
            except Exception:
                pass

    def executeCommand(self,profile: "Profile", command: list[str], natives_path: str) -> None:
        self.profile = profile
        self.natives_path = natives_path
        self.process = QProcess(self)
        self.process.setWorkingDirectory(profile.getGameDirectoryPath())
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.procStarted)
        self.process.finished.connect(self.procFinish)
        self.process.start(command[0], command[1:])

        if not self.process.waitForStarted():
            self.setPlainText(QCoreApplication.translate("GameOutputTab", "Failed to start Minecraft"))
            QMessageBox.critical(self, QCoreApplication.translate("GameOutputTab", "Failed to start"), QCoreApplication.translate("GameOutputTab", "Minecraft could not be started. Maybe you use a invalid Java executable."))
            self.env.mainWindow.playButton.setEnabled(True)
            return
