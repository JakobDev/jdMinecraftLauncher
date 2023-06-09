from jdMinecraftLauncher.Functions import hasInternetConnection, getAccountDict
from PyQt6.QtCore import QCoreApplication, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from jdMinecraftLauncher.gui.LoginWindow import LoginWindow
from jdMinecraftLauncher.gui.MainWindow import MainWindow
from jdMinecraftLauncher.Environment import Environment
from .ProfileImporter import askProfileImport
import minecraft_launcher_lib
import copy
import sys
import os


def main():
    app = QApplication(sys.argv)
    env = Environment(app)

    app.setWindowIcon(env.icon)
    app.setApplicationName("jdMinecraftLauncher")
    app.setDesktopFileName("page.codeberg.JakobDev.jdMinecraftLauncher")

    app_translator = QTranslator()
    qt_translator = QTranslator()
    app_trans_dir = os.path.join(env.currentDir, "translations")
    qt_trans_dir = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    language = env.settings.get("language")
    if language == "default":
        system_language = QLocale.system().name()
        app_translator.load(os.path.join(app_trans_dir, "jdMinecraftLauncher_" + system_language.split("_")[0] + ".qm"))
        app_translator.load(os.path.join(app_trans_dir, "jdMinecraftLauncher_" + system_language + ".qm"))
        qt_translator.load(os.path.join(qt_trans_dir, "qt_" + system_language.split("_")[0] + ".qm"))
        qt_translator.load(os.path.join(qt_trans_dir, "qt_" + system_language + ".qm"))
    else:
        app_translator.load(os.path.join(app_trans_dir, "jdMinecraftLauncher_" + language + ".qm"))
        qt_translator.load(os.path.join(qt_trans_dir, "qt_" + language.split("_")[0] + ".qm"))
        qt_translator.load(os.path.join(qt_trans_dir, "qt_" + language + ".qm"))
    app.installTranslator(app_translator)
    app.installTranslator(qt_translator)

    if not minecraft_launcher_lib.utils.is_platform_supported() and not env.args.force_start:
        QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "Unsupported Platform"), QCoreApplication.translate("jdMinecraftLauncher", "Your current Platform is not supported by jdMinecraftLauncher"))
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

    if env.firstLaunch:
        splash_screen.close()
        askProfileImport(env)

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
            splash_screen.close()
            QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "No Internet Connection"), QCoreApplication.translate("jdMinecraftLauncher", "You have no Internet connection. If you start jdMinecraftLauncher for the first time, you have to login using the Internet before you can use the offline Mode."))
            sys.exit(0)

    sys.exit(app.exec())
