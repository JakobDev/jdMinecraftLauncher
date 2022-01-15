from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QUrl, QLocale
import minecraft_launcher_lib
import json
import sys
import os


class LoginWindow(QWebEngineView):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.setWindowTitle(env.translate("loginwindow.title"))

        # Set the path where the refresh token is saved
        self.refresh_token_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh_token.json")

        # Login with refresh token, if it exists
        if os.path.isfile(self.refresh_token_file):
            with open(self.refresh_token_file, "r", encoding="utf-8") as f:
                refresh_token = json.load(f)
                # Do the login with refresh token
                try:
                    account_informaton = minecraft_launcher_lib.microsoft_account.complete_refresh(self.env.secrets.client_id, self.env.secrets.secret, self.env.secrets.redirect_url, refresh_token)
                    self.show_account_information(account_informaton)
                    return
                # Show the window if the refresh token is invalid
                except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
                    pass

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
            account_informaton = minecraft_launcher_lib.microsoft_account.complete_login(self.env.secrets.client_id, self.env.secrets.secret, self.env.secrets.redirect_url, auth_code)

            # Show the login information
            self.show_account_information(account_informaton)

    def show_account_information(self, information_dict):
        information_string = f'Username: {information_dict["name"]}<br>'
        information_string += f'UUID: {information_dict["id"]}<br>'
        information_string += f'Token: {information_dict["access_token"]}<br>'

        accountData = {
            "name": information_dict["name"],
            "accessToken": information_dict["access_token"],
            "refreshToken": information_dict["refresh_token"],
            "uuid": information_dict["id"]
        }

        self.env.account = accountData

        self.env.mainWindow.show()
        self.env.mainWindow.setFocus()
        for count, i in enumerate(self.env.accountList):
            if i["uuid"] == accountData["uuid"]:
                self.env.accountList[count] = accountData
                self.env.selectedAccount = count
                self.env.mainWindow.updateAccountInformation()
                return
        self.env.accountList.append(accountData)
        self.env.selectedAccount = len(self.env.accountList) - 1
        self.env.mainWindow.updateAccountInformation()
        self.close()

