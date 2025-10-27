from PyQt6.QtCore import QCoreApplication, QTranslator, QLibraryInfo
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from .Functions import hasInternetConnection, getDataPath, isFlatpak
from .core.ProfileCollection import ProfileCollection
from .utils.ProfileImporter import askProfileImport
from .utils.InterProcessCommunication import getIPC
from .core.AccountManager import AccountManager
from .utils.UpdateChecker import checkUpdates
from .core.ActionManager import ActionManager
from .Settings import Settings
from PyQt6.QtGui import QIcon
import minecraft_launcher_lib
from .Globals import Globals
import traceback
import argparse
import tomllib
import sys
import os


def _ensureMinecraftDirectoryExists() -> None:
    if os.path.isdir(Globals.minecraftDir):
        return

    try:
        os.makedirs(Globals.minecraftDir)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)

        settings = Settings.getInstance()

        text = QCoreApplication.translate("jdMinecraftLauncher", "The Minecraft directory was not found and could not be created.")

        if settings.get("customMinecraftDir") is None:
            QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "Minecraft directory not found"), text)
            sys.exit(1)
        else:
            text += "<br><br>" + QCoreApplication.translate("jdMinecraftLauncher", "You have set a custom Minecraft directory. Would you like to revert it back to the default?")

            if QMessageBox.question(None, QCoreApplication.translate("jdMinecraftLauncher", "Minecraft directory not found"), text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                sys.exit(1)

            Globals.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

            settings.set("customMinecraftDir", None)
            settings.save()

            _ensureMinecraftDirectoryExists()


def _handleAccount(splashScreen: QSplashScreen) -> bool:
    accountManager = AccountManager.getInstance()

    account = accountManager.getSelectedAccount()

    if account is None:
        splashScreen.close()
        if Globals.offlineMode:
            QMessageBox.critical(
                None,
                QCoreApplication.translate("jdMinecraftLauncher", "No Internet Connection"),
                QCoreApplication.translate("jdMinecraftLauncher", "You have no Internet connection. If you start jdMinecraftLauncher for the first time, you have to login using the Internet before you can use the offline Mode.")
            )
            return False

        return accountManager.addMicrosoftAccount(None) is not None

    if Globals.offlineMode:
        return True

    if account.reload():
        return True

    return account.login(None)


def _activate(args: argparse.Namespace, icon: QIcon) -> None:
    settings = Settings.getInstance()

    if Globals.firstLaunch:
        welcomeText = QCoreApplication.translate("jdMinecraftLauncher", "It appears to be your first time using jdMinecraftLauncher.") + " "
        welcomeText += QCoreApplication.translate("jdMinecraftLauncher", "This is a custom Minecraft Launcher designed to resemble the old official launcher in appearance and feel, but with modern features like Microsoft account support.") + "<br><br>"
        welcomeText += QCoreApplication.translate("jdMinecraftLauncher", "If you encounter any issues, please report them so that they can be addressed and resolved.") + "<br><br>"
        welcomeText += QCoreApplication.translate("jdMinecraftLauncher", "This launcher is not an official product of Mojang/Microsoft.")
        QMessageBox.information(None, QCoreApplication.translate("jdMinecraftLauncher", "Welcome"), welcomeText)

    if Globals.enableUpdater and not Globals.offlineMode and settings.get("checkUpdatesStartup"):
        checkUpdates()

    _ensureMinecraftDirectoryExists()

    splashScreen = QSplashScreen()
    splashScreen.setPixmap(icon.pixmap(128, 128))
    splashScreen.show()

    # We import it here, so jdMinecraftLauncher doesn't crash if the compiled ui files and missing and is able to show the error message
    from jdMinecraftLauncher.gui.MainWindow.MainWindow import MainWindow

    if not _handleAccount(splashScreen):
        sys.exit(0)

    mainWindow = MainWindow.getInstance()

    accountManager = AccountManager.getInstance()
    accountManager.saveData()

    if args.account:
        account = accountManager.getAccountByName(args.account)
        if account is not None:
            accountManager.setSelectedAccount(account)
        else:
            print(QCoreApplication.translate("jdMinecraftLauncher", "Account {{name}} does not exist").replace("{{name}}", args.account), file=sys.stderr)

    if Globals.firstLaunch:
        askProfileImport(mainWindow)

    mainWindow.updateAccountInformation()
    mainWindow.openMainWindow()

    splashScreen.close()


def main() -> None:
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), "ui_compiled")):
        print("Could not find compiled ui files. Please run tools/CompileUI.py first.", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)

    Globals.programDir = os.path.dirname(os.path.realpath(__file__))
    icon = QIcon(os.path.join(Globals.programDir, "Icon.svg"))

    with open(os.path.join(Globals.programDir, "version.txt"), "r", encoding="utf-8") as f:
        Globals.launcherVersion = f.read().strip()

    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs="?")
    parser.add_argument("--minecraft-dir", help="Set the Minecraft Directory")
    parser.add_argument("--data-dir", help="Set the Data Directory")
    parser.add_argument("--launch-profile", help="Launch a Profile")
    parser.add_argument("--account", help="Launch with the selected Account")
    parser.add_argument("--offline-mode", help="Force offline Mode", action="store_true")
    parser.add_argument("--force-start", help="Forces the start on unsupported Platforms", action="store_true")
    parser.add_argument("--dont-save-data", help="Don't save data to the disk (only for development usage)", action="store_true")
    parser.add_argument("--debug", help="Start in Debug Mode", action="store_true")
    parser.add_argument("--no-activate", help="Don't run in foreground", action="store_true")
    args = parser.parse_known_args()[0]

    ipc = getIPC()

    if args.url is not None and ipc.isAlreadyRunning():
        ipc.openURI(args.url)
        return

    if args.data_dir:
        Globals.dataDir = args.data_dir
    else:
        Globals.dataDir = getDataPath()

    if not os.path.exists(Globals.dataDir):
        os.makedirs(Globals.dataDir)
        Globals.firstLaunch = True

    settings = Settings.getInstance()
    settings.load()

    if args.minecraft_dir:
        Globals.minecraftDir = args.minecraft_dir
    elif settings.get("customMinecraftDir") is not None:
        Globals.minecraftDir = settings.get("customMinecraftDir")
    else:
        Globals.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

    if args.minecraft_dir:
        Globals.defaultMinecraftDir = args.minecraft_dir
    else:
        Globals.defaultMinecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

    Globals.debugMode = bool(args.debug)
    Globals.dontSaveData = bool(args.dont_save_data)

    with open(os.path.join(Globals.programDir, "Distribution.toml"), "rb") as f:
        distributionConfig = tomllib.load(f)

    Globals.enableUpdater = not isFlatpak() and distributionConfig.get("EnableUpdater", True)

    if (lang := settings.get("language")) != "default":
        Globals.locale = lang

    app.setWindowIcon(icon)
    app.setOrganizationName("JakobDev")
    app.setApplicationName("jdMinecraftLauncher")
    app.setDesktopFileName("page.codeberg.JakobDev.jdMinecraftLauncher")

    qtTranslator = QTranslator()
    if qtTranslator.load(Globals.locale, "qt", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(qtTranslator)

    webengineTranslator = QTranslator()
    if webengineTranslator.load(Globals.locale, "qtwebengine", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(webengineTranslator)

    appTranslator = QTranslator()
    if appTranslator.load(Globals.locale, "jdMinecraftLauncher", "_", os.path.join(Globals.programDir, "translations")):
        app.installTranslator(appTranslator)

    if not minecraft_launcher_lib.utils.is_platform_supported() and not args.force_start:
        QMessageBox.critical(None, QCoreApplication.translate("jdMinecraftLauncher", "Unsupported Platform"), QCoreApplication.translate("jdMinecraftLauncher", "Your current Platform is not supported by jdMinecraftLauncher"))
        sys.exit(0)

    if args.offline_mode or not hasInternetConnection():
        Globals.offlineMode = True

    try:
        import setproctitle
        setproctitle.setproctitle("jdMinecraftLauncher")
    except ModuleNotFoundError:
        pass

    ipc.startup()

    if os.getenv("DBUS_SESSION_BUS_ADDRESS") is not None:
        try:
            from .utils.DBusService import DBusService
            DBusService.start()
        except ModuleNotFoundError as ex:
            print(QCoreApplication.translate("jdMinecraftLauncher",
                                             "The DBus service failed to start because the optional Python module {{name}} was not found"
                                             ).replace("{{name}}", str(ex.name)), file=sys.stderr)

    actionManager = ActionManager.getInstance()
    actionManager.activated.connect(lambda: _activate(args, icon))

    if args.launch_profile is not None:
        profileCollection = ProfileCollection.getInstance()
        profile = profileCollection.getProfileByName(args.launch_profile)
        if profile is not None:
            actionManager.launchProfile(profile)
        else:
            QMessageBox.critical(None,
                                 QCoreApplication.translate("jdMinecraftLauncher", "Profile not found"),
                                 QCoreApplication.translate("jdMinecraftLauncher", "The given Profile was not found")
                                 )
    elif args.url is not None:
        actionManager.openURI(args.url)

    if args.no_activate:
        actionManager.resetExitTimer()
    else:
        actionManager.activate()

    sys.exit(app.exec())
