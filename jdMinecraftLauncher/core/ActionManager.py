from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget
from ..Profile import Profile
from typing import Optional


class ActionManager(QObject):
    _instance: Optional["ActionManager"] = None

    profileLaunched = pyqtSignal(Profile)
    uriOpened = pyqtSignal(str)
    activated = pyqtSignal()

    @classmethod
    def getInstance(cls) -> "ActionManager":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        super().__init__()

        self._currentLaunchProfile: Profile | None = None
        self._currentParent: QWidget | None = None
        self._currentURI: str | None = None
        self._exitTimer = QTimer()
        self._isActivated = False

        self._exitTimer.setInterval(10 * 1000)

        self._exitTimer.timeout.connect(self._exitTimeout)

    def _exitTimeout(self) -> None:
        if not self._isActivated:
            QApplication.quit()

    def activate(self) -> None:
        if not self._isActivated:
            self._isActivated = True
            self.activated.emit()

    def launchProfile(self, profile: Profile) -> None:
        self._currentLaunchProfile = profile
        self.profileLaunched.emit(profile)

    def getCurrentLaunchProfile(self) -> Profile | None:
        return self._currentLaunchProfile

    def resetExitTimer(self) -> None:
        if not self._isActivated:
            self._exitTimer.start()

    def openURI(self, uri: str) -> None:
        self.uriOpened.emit(uri)
        self._currentURI = uri

    def getCurrentURI(self) -> str | None:
        return self._currentURI
