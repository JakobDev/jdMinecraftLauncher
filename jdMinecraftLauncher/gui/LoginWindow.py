from PyQt5.QtWidgets import QWidget, QLineEdit, QCheckBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout
from jdMinecraftLauncher.Functions import showMessageBox
import minecraft_launcher_lib
import json
import os

class LoginWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.usernameInput = QLineEdit()
        self.passwordInput = QLineEdit()
        self.saveLogin = QCheckBox(env.translate("loginwindow.checkbox.saveLogin"))
        self.loginButton = QPushButton(env.translate("loginwindow.button.login"))

        self.passwordInput.setEchoMode(QLineEdit.Password)
        self.saveLogin.setChecked(True)

        self.loginButton.clicked.connect(self.loginButtonClicked)

        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(QLabel(env.translate("loginwindow.label.username")),0,0)
        self.gridLayout.addWidget(self.usernameInput,0,1)
        self.gridLayout.addWidget(QLabel(env.translate("loginwindow.label.password")),1,0)
        self.gridLayout.addWidget(self.passwordInput,1,1)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.loginButton)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(QLabel(env.translate("loginwindow.label.message")))
        self.mainLayout.addLayout(self.gridLayout)
        self.mainLayout.addWidget(self.saveLogin)
        self.mainLayout.addLayout(self.buttonLayout)

        self.setWindowTitle(env.translate("loginwindow.title"))
        self.setLayout(self.mainLayout)
        self.mainLayout.setSizeConstraint(QLayout.SetFixedSize)

    def loginButtonClicked(self):
        loginInformation = minecraft_launcher_lib.account.login_user(self.usernameInput.text(),self.passwordInput.text())
        
        if "errorMessage" in loginInformation:
            if loginInformation["errorMessage"] == "Invalid credentials. Invalid username or password.":
                showMessageBox("loginwindow.loginfailed.title","loginwindow.loginfailed.text",self.env)
                return
            else:
                showMessageBox(loginInformation["error"],loginInformation["errorMessage"],self.env)
                return
        
        self.env.accountData = loginInformation
        self.env.accountString = str(loginInformation)
        self.env.account = {}
        self.env.account["name"] = loginInformation["selectedProfile"]["name"]
        self.env.account["accessToken"] = loginInformation["accessToken"]
        self.env.account["clientToken"] = loginInformation["clientToken"]
        self.env.account["uuid"] = loginInformation["selectedProfile"]["id"]
        if self.saveLogin.checkState():
            with open(os.path.join(self.env.dataPath,"mojang_account.json"), 'w', encoding='utf-8') as f:
                json.dump(self.env.account, f, ensure_ascii=False, indent=4)
        self.close()
        self.usernameInput.setText("")
        self.passwordInput.setText("")
        self.env.mainWindow.updateAccountInformation()
        self.env.mainWindow.show()
        self.env.mainWindow.setFocus()
