from jdMinecraftLauncher.Functions import hasInternetConnection, getAccountDict
from PyQt6.QtCore import QCoreApplication, QTranslator, QLibraryInfo, QLocale
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from jdMinecraftLauncher.gui.MainWindow.MainWindow import MainWindow
from jdMinecraftLauncher.Environment import Environment
from .ProfileImporter import askProfileImport
import minecraft_launcher_lib
import traceback
import copy
import sys
import os


def _ensureMinecraftDirectoryExists(env: Environment) -> None:
    if os.path.isdir(env.minecraftDir):
        return

    try:
        os.makedirs(env.minecraftDir)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)

        text = QCoreApplication.translate("jdMinecraftLauncher", "The Minecraft directory was not found and could not be created.")

        if env.settings.get("customMinecraftDir") is None:
            QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "Minecraft directory not found"), text)
            sys.exit(1)
        else:
            text += "<br><br>" + QCoreApplication.translate("jdMinecraftLauncher", "You have set a custom Minecraft directory. Would you like to revert it back to the default?")

            if QMessageBox.question(None, QCoreApplication.translate("jdMinecraftLauncher", "Minecraft directory not found"), text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                sys.exit(1)

            env.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

            env.settings.set("customMinecraftDir", None)
            env.settings.save(os.path.join(env.dataDir, "settings.json"))

            _ensureMinecraftDirectoryExists(env)


def _handleAccount(env: Environment, splashScreen: QSplashScreen) -> None:
    account = env.accountManager.getSelectedAccount()

    if account is None:
        splashScreen.close()
        if env.offlineMode:
            QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "No Internet Connection"), QCoreApplication.translate("jdMinecraftLauncher", "You have no Internet connection. If you start jdMinecraftLauncher for the first time, you have to login using the Internet before you can use the offline Mode."))
            return False

        return env.accountManager.addMicrosoftAccount(None) is not None

    if env.offlineMode:
        splashScreen.close()
        return True

    if account.reload():
        splashScreen.close()
        return True

    splashScreen.close()

    return account.login(None)


def main() -> None:
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

    _ensureMinecraftDirectoryExists(env)

    splashScreen = QSplashScreen()
    splashScreen.setPixmap(env.icon.pixmap(128, 128))
    splashScreen.show()

    try:
        import setproctitle
        setproctitle.setproctitle("jdMinecraftLauncher")
    except ModuleNotFoundError:
        pass

    if env.args.offline_mode or not hasInternetConnection():
        env.offlineMode = True

    env.loadVersions()

    env.mainWindow = MainWindow(env)

    if not _handleAccount(env, splashScreen):
        sys.exit(0)

    if env.firstLaunch:
        askProfileImport(env)

    env.mainWindow.updateAccountInformation()
    env.mainWindow.openMainWindow()

    sys.exit(app.exec())
