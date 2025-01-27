from PyQt6.QtCore import QCoreApplication, QTranslator, QLibraryInfo
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from jdMinecraftLauncher.Functions import hasInternetConnection
from jdMinecraftLauncher.Environment import Environment
from .MicrosoftSecrets import MicrosoftSecrets
from .utils.UpdateChecker import checkUpdates
from .ProfileImporter import askProfileImport
import minecraft_launcher_lib
import traceback
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


def _handleAccount(env: Environment, splashScreen: QSplashScreen) -> bool:
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
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), "ui_compiled")):
        print("Could not find compiled ui files. Please run tools/CompileUI.py first.", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    env = Environment(app)

    app.setWindowIcon(env.icon)
    app.setOrganizationName("JakobDev")
    app.setApplicationName("jdMinecraftLauncher")
    app.setDesktopFileName("page.codeberg.JakobDev.jdMinecraftLauncher")

    MicrosoftSecrets.setup(env)

    qtTranslator = QTranslator()
    if qtTranslator.load(env.locale, "qt", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(qtTranslator)

    webengineTranslator = QTranslator()
    if webengineTranslator.load(env.locale, "qtwebengine", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(webengineTranslator)

    appTranslator = QTranslator()
    if appTranslator.load(env.locale, "jdMinecraftLauncher", "_", os.path.join(env.currentDir, "translations")):
        app.installTranslator(appTranslator)

    if not minecraft_launcher_lib.utils.is_platform_supported() and not env.args.force_start:
        QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "Unsupported Platform"), QCoreApplication.translate("jdMinecraftLauncher", "Your current Platform is not supported by jdMinecraftLauncher"))
        sys.exit(0)

    if env.args.offline_mode or not hasInternetConnection():
        env.offlineMode = True

    if env.firstLaunch:
        welcomeText = QCoreApplication.translate("jdMinecraftLauncher", "It appears to be your first time using jdMinecraftLauncher.") + " "
        welcomeText += QCoreApplication.translate("jdMinecraftLauncher", "This is a custom Minecraft Launcher designed to resemble the old official launcher in appearance and feel, but with modern features like Microsoft account support.") + "<br><br>"
        welcomeText += QCoreApplication.translate("jdMinecraftLauncher", "If you encounter any issues, please report them so that they can be addressed and resolved.") + "<br><br>"
        welcomeText += QCoreApplication.translate("jdMinecraftLauncher", "This launcher is not an official product of Mojang/Microsoft.")
        QMessageBox.information(None, QCoreApplication.translate("jdMinecraftLauncher", "Welcome"), welcomeText)

    if env.enableUpdater and not env.offlineMode and env.settings.get("checkUpdatesStartup"):
        checkUpdates(env)

    _ensureMinecraftDirectoryExists(env)

    splashScreen = QSplashScreen()
    splashScreen.setPixmap(env.icon.pixmap(128, 128))
    splashScreen.show()

    try:
        import setproctitle
        setproctitle.setproctitle("jdMinecraftLauncher")
    except ModuleNotFoundError:
        pass

    env.loadVersions()

    # We import it here, so jdMinecraftLauncher doen't crash if the compiled ui files and missing and is able to show the error message
    from jdMinecraftLauncher.gui.MainWindow.MainWindow import MainWindow

    mainWindow = MainWindow(env)

    if not _handleAccount(env, splashScreen):
        sys.exit(0)

    env.accountManager.saveData()

    if env.args.account:
        account = env.accountManager.getAccountByName(env.args.account)
        if account is not None:
            env.accountManager.setSelectedAccount(account)
        else:
            print(QCoreApplication.translate("jdMinecraftLauncher", "Account {{name}} does not exist").replace("{{name}}", env.args.account), file=sys.stderr)

    if env.firstLaunch:
        askProfileImport(env, mainWindow)

    mainWindow.updateAccountInformation()
    mainWindow.openMainWindow()

    sys.exit(app.exec())
