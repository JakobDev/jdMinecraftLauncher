from PyQt6.QtWidgets import QWidget, QInputDialog
from .MicrosoftSecrets import MicrosoftSecrets
from PyQt6.QtCore import QCoreApplication
from .gui.LoginWindow import LoginWindow
from typing import cast, TYPE_CHECKING
import minecraft_launcher_lib
import traceback
import uuid
import json
import sys
import os


if TYPE_CHECKING:
    from .Environment import Environment


class AccountBase:
    def __init__(self) -> None:
        self.id = ""

    def getType(self) -> str:
        raise NotImplementedError()

    def getName(self) -> str:
        raise NotImplementedError()

    def getMinecraftUUID(self) -> str:
        raise NotImplementedError()

    def getAccessToken(self) -> str:
        raise NotImplementedError()

    def login(self, parent: QWidget | None) -> bool:
        raise NotImplementedError()

    def reload(self) -> bool:
        raise NotImplementedError()

    def getJsonData(self) -> dict:
        raise NotImplementedError()


class MicrosoftAccount(AccountBase):
    def __init__(self) -> None:
        super().__init__()

        self._name = ""
        self._uuid = ""
        self._accessToken = ""
        self._refreshToken = ""

    @classmethod
    def fromJsonData(cls, data: dict) -> "MicrosoftAccount":
        account = cls()

        account.id = data["id"]
        account._name = data["name"]
        account._uuid = data["uuid"]
        account._accessToken = data["accessToken"]
        account._refreshToken = data["refreshToken"]

        return account

    def getType(self) -> str:
        return "Microsoft"

    def getName(self) -> str:
        return self._name

    def getMinecraftUUID(self) -> str:
        return self._uuid

    def getAccessToken(self) -> str:
        return self._accessToken

    def login(self, parent: QWidget | None) -> bool:
        loginWindow = LoginWindow(parent)
        loginWindow.exec()
        accountData = loginWindow.getAccountData()

        if accountData is None:
            return False

        self._name = accountData["name"]
        self._uuid = accountData["uuid"]
        self._accessToken = accountData["accessToken"]
        self._refreshToken = accountData["refreshToken"]

        return True

    def reload(self) -> bool:
        secrets = MicrosoftSecrets.get_secrets()

        try:
            data = minecraft_launcher_lib.microsoft_account.complete_refresh(secrets.client_id, secrets.secret, secrets.redirect_url, self._refreshToken)

            self._name = data["name"]
            self._uuid = data["id"]
            self._accessToken = data["access_token"]
            self.refreshToken = data["refresh_token"]

            return True
        except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
            return False
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            return False

    def getJsonData(self) -> dict:
        return {
            "type": "microsoft",
            "id": self.id,
            "name": self._name,
            "uuid": self._uuid,
            "accessToken": self._accessToken,
            "refreshToken": self._refreshToken,
        }


class DummyAccount(AccountBase):
    def __init__(self) -> None:
        super().__init__()

        self._name = ""

    @classmethod
    def fromJsonData(cls, data: dict) -> "DummyAccount":
        account = cls()

        account.id = data["id"]
        account._name = data["name"]
        account._uuid = data["uuid"]

        return account

    def getType(self) -> str:
        return "Dummy"

    def getName(self) -> str:
        return self._name

    def getMinecraftUUID(self) -> str:
        return self._uuid

    def getAccessToken(self) -> str:
        return ""

    def login(self, parent: QWidget | None) -> bool:
        name, ok = QInputDialog.getText(parent, QCoreApplication.translate("AccountManager", "Enter name"), QCoreApplication.translate("AccountManager", "Please enter a name for the dummy account"))

        if not ok:
            return False

        self._name = name
        self._uuid = str(uuid.uuid4())

        return True

    def reload(self) -> bool:
        return True

    def getJsonData(self) -> dict:
        return {
            "type": "dummy",
            "id": self.id,
            "name": self._name,
            "uuid": self._uuid,
        }


class AccountManager:
    def __init__(self, env: "Environment") -> None:
        self._accountList: list[AccountBase] = []
        self._currentID = ""
        self._env = env

        self._loadData()

    def _loadData(self) -> None:
        if not os.path.isfile(os.path.join(self._env.dataDir, "accounts.json")):
            return

        try:
            with open(os.path.join(self._env.dataDir, "accounts.json"), "r", encoding="utf-8") as f:
                data = json.load(f)

            self._currentID = data["selectedAccount"]
            self._accountList.clear()

            for accountData in data["accounts"]:
                match accountData["type"]:
                    case "microsoft":
                        self._accountList.append(MicrosoftAccount.fromJsonData(accountData))
                    case "dummy":
                        self._accountList.append(DummyAccount.fromJsonData(accountData))

        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

    def saveData(self) -> None:
        if self._env.args.dont_save_data:
            return

        try:
            data = {"selectedAccount": self._currentID, "accounts": []}

            for account in self._accountList:
                cast(list[dict], data["accounts"]).append(account.getJsonData())

            try:
                os.makedirs(self._env.dataDir)
            except FileExistsError:
                pass

            with open(os.path.join(self._env.dataDir, "accounts.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

    def _generateID(self) -> str:
        while True:
            currentUUID = str(uuid.uuid4())
            if self.getAccountByID(currentUUID) is None:
                return currentUUID

    def getAccountByID(self, uuid: str) -> AccountBase | None:
        for currentAccount in self._accountList:
            if currentAccount.id == uuid:
                return currentAccount
        return None

    def getAccountByName(self, name: str) -> AccountBase | None:
        for currentAccount in self._accountList:
            if currentAccount.getName().lower() == name.lower():
                return currentAccount
        return None

    def getSelectedAccount(self) -> AccountBase | None:
        return self.getAccountByID(self._currentID)

    def getAllAccounts(self) -> list[AccountBase]:
        return self._accountList

    def setSelectedAccount(self, account: AccountBase) -> None:
        self._currentID = account.id
        self.saveData()

    def removeAccount(self, account: AccountBase) -> None:
        for count, currentAccount in enumerate(self._accountList):
            if account == currentAccount:
                del self._accountList[count]
                break

        if self._currentID == account.id:
            if len(self._accountList) == 0:
                self._currentID = ""
            else:
                self._currentID = self._accountList[0].id

        self.saveData()

    def _addAccount(self, account: AccountBase, parent: QWidget | None) -> AccountBase | None:
        if account.login(parent) is False:
            return None

        account.id = self._generateID()

        self._accountList.append(account)

        if self.getSelectedAccount() is None:
            self._currentID = account.id

        self.saveData()

        return account

    def addMicrosoftAccount(self, parent: QWidget | None) -> AccountBase | None:
        account = MicrosoftAccount()
        return self._addAccount(account, parent)

    def addDummyAccount(self, parent: QWidget | None) -> AccountBase | None:
        account = DummyAccount()
        return self._addAccount(account, parent)
