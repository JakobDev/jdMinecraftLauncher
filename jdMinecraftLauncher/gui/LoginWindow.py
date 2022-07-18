from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import minecraft_launcher_lib
import json
import os


class LoginWindow(QWebEngineView):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.setWindowTitle(env.translate("loginwindow.title"))

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

        self.env.mainWindow.openMainWindow()
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

