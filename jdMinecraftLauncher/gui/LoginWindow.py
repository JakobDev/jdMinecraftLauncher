from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QCoreApplication
from typing import TYPE_CHECKING
import minecraft_launcher_lib


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class LoginWindow(QWebEngineView):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        self.setWindowTitle(QCoreApplication.translate("LoginWindow", "Login"))

        # Open the login url
        self.load(QUrl(minecraft_launcher_lib.microsoft_account.get_login_url(self.env.secrets.client_id, self.env.secrets.redirect_url)))

        # Connects a function that is called when the url changed
        self.urlChanged.connect(self.new_url)

    def new_url(self, url: QUrl):
        # Check if the url contains the code
        if minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url.toString()):
            # Get the code from the url
            auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(url.toString())
            # Do the login
            account_information = minecraft_launcher_lib.microsoft_account.complete_login(self.env.secrets.client_id, self.env.secrets.secret, self.env.secrets.redirect_url, auth_code)

            # Show the login information
            self.login_done(account_information)

    def login_done(self, information_dict: minecraft_launcher_lib.microsoft_types.CompleteLoginResponse):
        accountData = {
            "name": information_dict["name"],
            "accessToken": information_dict["access_token"],
            "refreshToken": information_dict["refresh_token"],
            "uuid": information_dict["id"]
        }

        self.env.account = accountData

        self.env.mainWindow.openMainWindow()
        self.env.mainWindow.setFocus()
        for count, i in enumerate(self.env.accountList):
            if i["uuid"] == accountData["uuid"]:
                self.env.accountList[count] = accountData
                self.env.selectedAccount = count
                self.env.mainWindow.updateAccountInformation()
                self.close()
                return
        self.env.accountList.append(accountData)
        self.env.selectedAccount = len(self.env.accountList) - 1
        self.env.mainWindow.updateAccountInformation()
        self.close()

