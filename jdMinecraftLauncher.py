#!/usr/bin/env python3
from Functions import hasInternetConnection, showMessageBox
from SharedEnviroment import SharedEnviroment
from PyQt5.QtWidgets import QApplication
from gui.LoginWindow import LoginWindow
from gui.MainWindow import MainWindow
import mojang_api
import json
import sys
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)
    env = SharedEnviroment()
    env.mainWindow = MainWindow(env)
    env.loginWindow = LoginWindow(env)

    if os.path.isfile(os.path.join(env.dataPath,"mojang_account.json")):
        with open(os.path.join(env.dataPath,"mojang_account.json")) as f:
            env.account = json.load(f)
        if hasInternetConnection():
            response = str(mojang_api.servers.authserver.validate_access_token(env.account["accessToken"],env.account["clientToken"]))
            if response.find("Invalid token") == -1:
                env.loadVersions()
                env.mainWindow.updateAccountInformation()
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
