from jdMinecraftLauncher.Functions import hasInternetConnection, showMessageBox, getAccountDict
from jdMinecraftLauncher.gui.LoginWindow import LoginWindow
from jdMinecraftLauncher.gui.MainWindow import MainWindow
from jdMinecraftLauncher.Environment import Environment
from PyQt6.QtWidgets import QApplication, QSplashScreen
import minecraft_launcher_lib
import copy
import sys


def main():
    app = QApplication(sys.argv)
    env = Environment(app)

    app.setApplicationName("jdMinecraftLauncher")
    app.setDesktopFileName("com.gitlab.JakobDev.jdMinecraftLauncher")
    app.setWindowIcon(env.icon)

    if not minecraft_launcher_lib.utils.is_platform_supported() and not env.args.force_start:
        showMessageBox("messagebox.unsupportedPlatform.title", "messagebox.unsupportedPlatform.text", env)
        sys.exit(0)

    splash_screen = QSplashScreen()
    splash_screen.setPixmap(env.icon.pixmap(128, 128))
    splash_screen.show()

    env.mainWindow = MainWindow(env)
    env.loginWindow = LoginWindow(env)

    try:
        import setproctitle
        setproctitle.setproctitle("jdMinecraftLauncher")
    except ModuleNotFoundError:
        pass

    if hasattr(env, "account"):
        if not env.args.offline_mode and hasInternetConnection():
            try:
                accountData = getAccountDict(minecraft_launcher_lib.microsoft_account.complete_refresh(env.secrets.client_id, env.secrets.secret, env.secrets.redirect_url, env.account["refreshToken"]))
                env.accountList[env.selectedAccount] = copy.copy(accountData)
                env.account = copy.copy(accountData)
                splash_screen.close()
                env.mainWindow.updateAccountInformation()
                env.mainWindow.openMainWindow()
            except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
                splash_screen.close()
                env.loginWindow.show()
        else:
            env.offlineMode = True
            env.loadVersions()
            splash_screen.close()
            env.mainWindow.updateAccountInformation()
            env.mainWindow.openMainWindow()
    else:
        if not env.args.offline_mode and hasInternetConnection():
            splash_screen.close()
            env.loginWindow.show()
        else:
            showMessageBox("messagebox.nointernet.title","messagebox.nointernet.text", env, lambda: sys.exit(0))
            env.mainWindow.profileWindow.close()
            env.mainWindow.close()
            env.loginWindow.close()

    sys.exit(app.exec())
