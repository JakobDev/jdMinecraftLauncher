from jdMinecraftLauncher.Functions import hasInternetConnection, showMessageBox, getAccountDict
from jdMinecraftLauncher.MicrosoftSecrets import MicrosoftSecrets
from jdMinecraftLauncher.gui.LoginWindow import LoginWindow
from jdMinecraftLauncher.gui.MainWindow import MainWindow
from jdMinecraftLauncher.Enviroment import Enviroment
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import minecraft_launcher_lib
import json
import copy
import sys
import os

def main():
    app = QApplication(sys.argv)
    env = Enviroment()
    app.setWindowIcon(QIcon(os.path.join(env.currentDir , "Icon.svg")))
    env.mainWindow = MainWindow(env)
    env.loginWindow = LoginWindow(env)

    try:
        import setproctitle
        setproctitle.setproctitle("jdMinecraftLauncher")
    except ModuleNotFoundError:
        pass

    if hasattr(env, "account"):
        if hasInternetConnection():
            try:
                accountData = getAccountDict(minecraft_launcher_lib.microsoft_account.complete_refresh(env.secrets.client_id, env.secrets.secret, env.secrets.redirect_url, env.account["refreshToken"]))
                env.accountList[env.selectedAccount] = copy.copy(accountData)
                env.account = copy.copy(accountData)
                env.mainWindow.updateAccountInformation()
                env.mainWindow.show()
            except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
                env.loginWindow.show()
        else:
            env.offlineMode = True
            env.loadVersions()
            env.mainWindow.updateAccountInformation()
            env.mainWindow.show()
    else:
        if hasInternetConnection():
            env.loginWindow.show()
        else:
            showMessageBox("messagebox.nointernet.title","messagebox.nointernet.text",self.env,lambda: sys.exit(0))
            env.mainWindow.profileWindow.close()
            env.mainWindow.close()
            env.loginWindow.close()
    sys.exit(app.exec())
