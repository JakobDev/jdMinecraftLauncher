from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QCoreApplication
from ..MicrosoftSecrets import MicrosoftSecrets
import minecraft_launcher_lib


class LoginWindow(QDialog):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self._secrets = MicrosoftSecrets.get_secrets()

        self.setWindowTitle(QCoreApplication.translate("LoginWindow", "Login"))

        self._webView = QWebEngineView()

        loginUrl, self._state, self._codeVerifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(self._secrets.client_id, self._secrets.redirect_url)

        # Open the login url
        self._webView.load(QUrl(loginUrl))

        # Connects a function that is called when the url changed
        self._webView.urlChanged.connect(self.newUrl)

        self._accountData: dict[str, str] | None = None

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._webView)

        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)

    def newUrl(self, url: QUrl) -> None:
        # Check if the url contains the code
        if not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url.toString()):
            return

        # Get the code from the url
        authCode = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(url.toString(), self._state)
        # Do the login
        try:
            accountInformation = minecraft_launcher_lib.microsoft_account.complete_login(self._secrets.client_id, self._secrets.secret, self._secrets.redirect_url, authCode, self._codeVerifier)
        except minecraft_launcher_lib.exceptions.AccountNotOwnMinecraft:
            self.hide()

            text = QCoreApplication.translate("LoginWindow", "Your account appears to not own Minecraft.")
            text += " " + QCoreApplication.translate("LoginWindow", "You need an account that owns Minecraft to use jdMinecraftLauncher.")
            text += " " + QCoreApplication.translate("LoginWindow", "If you've purchased Minecraft and still encounter this error, try logging in with the official launcher first.")
            text += " " + QCoreApplication.translate("LoginWindow", "If the error still persists, please write a bug report.")
            QMessageBox.critical(self, QCoreApplication.translate("LoginWindow", "Account does not own Minecraft"), text)

            loginUrl, self._state, self._codeVerifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(self._secrets.client_id, self._secrets.redirect_url)

            self._webView.load(QUrl(loginUrl))

            self.show()

            return

        self._accountData = {
            "name": accountInformation["name"],
            "accessToken": accountInformation["access_token"],
            "refreshToken": accountInformation["refresh_token"],
            "uuid": accountInformation["id"]
        }

        self.close()

    def getAccountData(self) -> dict[str, str] | None:
        return self._accountData
