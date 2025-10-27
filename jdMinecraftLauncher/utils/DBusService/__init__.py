from ...core.ProfileCollection import ProfileCollection
from ...core.AccountManager import AccountManager
from ...core.ActionManager import ActionManager
from PyQt6.QtCore import QCoreApplication
from .Connection import DBusConnection
from ...Functions import getRealPath
from typing import Optional, Any
from ...Profile import Profile
from ...Globals import Globals
import traceback
import jeepney
import sys
import os


with open(os.path.join(os.path.dirname(__file__), "Introspect.xml"), "r", encoding="utf-8") as f:
    introspect = f.read()


class DBusService:
    _instance: Optional["DBusService"] = None

    def __init__(self) -> None:
        self._connection = DBusConnection()

        self._profileCollection = ProfileCollection.getInstance()
        self._accountManager = AccountManager.getInstance()
        self._actionManager = ActionManager.getInstance()

        rep = self._connection.send_and_get_reply(jeepney.bus_messages.message_bus.RequestName("page.codeberg.JakobDev.jdMinecraftLauncher"))
        if rep.body[0] == 1:
            self._connection.message_received.connect(self._listener)
        else:
            print(QCoreApplication.translate("DBusService", "Failed to acquire DBus name {{name}}").replace("{{name}}", "page.codeberg.JakobDev.jdMinecraftLauncher"), file=sys.stderr)

    def _searchProfile(self, text: str) -> list[Profile]:
        if self._accountManager.getSelectedAccount() is None:
            return []

        results: list[Profile] = []

        for profile in self._profileCollection.getProfileList():
            if text.lower() in profile.name.lower():
                results.append(profile)

        return results

    def _launchProfile(self, profile: Profile) -> None:
        self._actionManager.activate()
        self._actionManager.launchProfile(profile)

    def _setActivationToken(self, activationToken: str) -> None:
        if activationToken == "":
            return

        os.putenv("XDG_ACTIVATION_TOKEN", activationToken)

        try:
            os.reload_environ()  # type: ignore[attr-defined]
        except AttributeError:
            pass

    def _handleMain(self, msg: jeepney.Message) -> None:
        match msg.header.fields[jeepney.HeaderFields.member]:
            case "OpenURI":
                self._setActivationToken(msg.body[1])
                self._actionManager.openURI(msg.body[0])

                return jeepney.new_method_return(msg, "", ())
            case "ListProfiles":
                profileList: list[str] = []

                for currentProfile in self._profileCollection.getProfileList():
                    profileList.append(currentProfile.id)

                return jeepney.new_method_return(msg, "as", (profileList,))
            case "LaunchProfile":
                profile = self._profileCollection.getProfileByID(msg.body[0])
                if profile is not None:
                    self._setActivationToken(msg.body[1])
                    self._launchProfile(profile)
                    return jeepney.new_method_return(msg, "", ())
                else:
                    return jeepney.new_error(msg, "org.freedesktop.DBus.Error.InvalidArgs", "s", ("Invalid id",))
            case "GetProfileDetails":
                profile = self._profileCollection.getProfileByID(msg.body[0])
                if profile is None:
                    return jeepney.new_error(msg, "org.freedesktop.DBus.Error.InvalidArgs", "s", ("Invalid id",))

                return jeepney.new_method_return(msg, "a{sv}", ({
                    "id": ("s", profile.id),
                    "name": ("s", profile.name),
                    "version": ("s", profile.getVersionID()),
                    "gameDirectory": ("s", getRealPath(profile.getGameDirectoryPath())),
                },))
            case "GetLauncherVersion":
                return jeepney.new_method_return(msg, "s", (Globals.launcherVersion,))
            case _:
                return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", ("Invalid method call",))

    def _handleKrunner(self, msg: jeepney.Message) -> jeepney.Message:
        match msg.header.fields[jeepney.HeaderFields.member]:
            case "Actions":
                return jeepney.new_method_return(msg, "a(sss)", ([],))
            case "Match":
                results = []

                for currentProfile in self._searchProfile(msg.body[0]):
                    results.append((
                        currentProfile.id,
                        currentProfile.name,
                        "page.codeberg.JakobDev.jdMinecraftLauncher",
                        100,
                        1.0,
                        {"subtext": ("s", QCoreApplication.translate("DBusService", "Launch {{name}} using jdMinecraftLauncher").replace("{{name}}", currentProfile.name))}
                    ))

                return jeepney.new_method_return(msg, "a(sssida{sv})", (results,))
            case "Run":
                profile = self._profileCollection.getProfileByID(msg.body[0])
                if profile is not None:
                    self._launchProfile(profile)

                return jeepney.new_method_return(msg, "", ())
            case _:
                return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", ("Invalid method call",))

    def _handleGnomeSearchProvider(self, msg: jeepney.Message) -> jeepney.Message:
        match msg.header.fields[jeepney.HeaderFields.member]:
            case "GetInitialResultSet":
                initialResults: list[str] = []

                for term in msg.body[0]:
                    for currentProfile in self._searchProfile(term):
                        if currentProfile.id not in initialResults:
                            initialResults.append(currentProfile.id)

                return jeepney.new_method_return(msg, "as", (initialResults,))
            case "GetSubsearchResultSet":
                subsearchResults: list[str] = []

                for term in msg.body[1]:
                    for currentProfile in self._searchProfile(term):
                        if currentProfile.id not in subsearchResults:
                            subsearchResults.append(currentProfile.id)

                return jeepney.new_method_return(msg, "as", (subsearchResults,))
            case "GetResultMetas":
                metas: list[dict[str, Any]] = []
                for profileId in msg.body[0]:
                    profile = self._profileCollection.getProfileByID(profileId)
                    if profile is None:
                        continue

                    metas.append({
                        "id": ("s", profileId),
                        "name": ("s", profile.name),
                        "gicon": ("s", "page.codeberg.JakobDev.jdMinecraftLauncher"),
                        "description": ("s", QCoreApplication.translate("DBusService", "Launch {{name}} using jdMinecraftLauncher").replace("{{name}}", profile.name))
                    })

                return jeepney.new_method_return(msg, "aa{sv}", (metas,))
            case "ActivateResult":
                profile = self._profileCollection.getProfileByID(msg.body[0])
                if profile is not None:
                    self._launchProfile(profile)

                return jeepney.new_method_return(msg, "", ())
            case "LaunchSearch":
                pass
            case _:
                return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", ("Invalid method call",))

    def _getMachineId(self) -> str:
        for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
            if not os.path.exists(path):
                continue

            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()

        return ""

    def _handleMessage(self, msg: jeepney.Message) -> jeepney.Message:
        if msg.header.fields[jeepney.HeaderFields.path] != "/":
            return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", ("Invalid method call",))

        match msg.header.fields[jeepney.HeaderFields.interface]:
            case "page.codeberg.JakobDev.jdMinecraftLauncher":
                return self._handleMain(msg)
            case "org.kde.krunner1":
                return self._handleKrunner(msg)
            case "org.gnome.Shell.SearchProvider2":
                return self._handleGnomeSearchProvider(msg)
            case "org.freedesktop.DBus.Introspectable":
                if msg.header.fields[jeepney.HeaderFields.member] == "Introspect":
                    return jeepney.new_method_return(msg, "s", (introspect,))
                else:
                    return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", ("Invalid method call",))
            case "org.freedesktop.DBus.Peer":
                match msg.header.fields[jeepney.HeaderFields.member]:
                    case "Ping":
                        return jeepney.new_method_return(msg, "", ())
                    case "GetMachineId":
                        return jeepney.new_method_return(msg, "s", (self._getMachineId(),))
                    case _:
                        return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", ("Invalid method call",))
            case _:
                return jeepney.new_error(msg, "org.freedesktop.DBus.Error.UnknownInterface", "s", ("Invalid interface",))

    def _listener(self, msg: jeepney.Message) -> None:
        if msg.header.message_type != jeepney.MessageType.method_call:
            return

        self._actionManager.resetExitTimer()

        try:
            resp = self._handleMessage(msg)
            self._connection.send(resp)
        except Exception as ex:
            print(traceback.format_exc(), file=sys.stderr)
            self._connection.send(jeepney.new_error(msg, "org.freedesktop.DBus.Error.InternalError", "s", (str(ex),)))

    @classmethod
    def start(cls) -> None:
        cls._instance = cls()
