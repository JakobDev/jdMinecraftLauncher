from jdMinecraftLauncher.Functions import hasInternetConnection, showMessageBox, login_with_saved_passwords
from jdMinecraftLauncher.gui.LoginWindow import LoginWindow
from jdMinecraftLauncher.gui.MainWindow import MainWindow
from jdMinecraftLauncher.Enviroment import Enviroment
from PyQt5.QtWidgets import QApplication
import minecraft_launcher_lib
import json
import sys
import os

def main():
    app = QApplication(sys.argv)
    env = Enviroment()
    env.mainWindow = MainWindow(env)
    env.loginWindow = LoginWindow(env)

    if hasattr(env,"account"):
        if hasInternetConnection():
            response = minecraft_launcher_lib.account.validate_access_token(env.account["accessToken"])
            if response:
                env.mainWindow.updateAccountInformation()
                env.mainWindow.show()
            elif env.account.get("mail","") in env.saved_passwords:
                login_with_saved_passwords(env,env.account)
                env.mainWindow.show()
            else:
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
    #w = MainWindow()
    #w.setup(env)
    #w.show()
    #w.setFocus()
    sys.exit(app.exec_())
