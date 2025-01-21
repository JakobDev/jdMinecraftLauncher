from PyQt6.QtWidgets import QWidget, QPushButton, QMenu, QTableWidgetItem, QMessageBox
from ...Functions import clearTableWidget, stretchTableWidgetColumnsSize
from PyQt6.QtCore import Qt, QCoreApplication, QPoint
from ...ui_compiled.AccountTab import Ui_AccountTab
from typing import TYPE_CHECKING
from PyQt6.QtGui import QAction


if TYPE_CHECKING:
    from ...AccountManager import AccountBase
    from ...Environment import Environment
    from .MainWindow import MainWindow


class _TableColumns:
    NAME = 0
    TYPE = 1
    SWITCH = 2
    REMOVE = 3


class _SwitchAccountButton(QPushButton):
    def __init__(self, env: "Environment", account: "AccountBase", mainWindow: "MainWindow") -> None:
        super().__init__(QCoreApplication.translate("AccountTab", "Switch"))

        self._env = env
        self._account = account
        self._mainWindow = mainWindow

        self.clicked.connect(self._buttonClicked)

    def _buttonClicked(self) -> None:
        if not self._account.reload():
            if not self._account.login(self._mainWindow):
                return

        self._env.accountManager.setSelectedAccount(self._account)
        self._mainWindow.updateAccountInformation()


class _RemoveAccountButton(QPushButton):
    def __init__(self, env: "Environment", account: "AccountBase", mainWindow: "MainWindow") -> None:
        super().__init__(QCoreApplication.translate("AccountTab", "Remove"))

        self._env = env
        self._account = account
        self._mainWindow = mainWindow

        self.clicked.connect(self._buttonClicked)

    def _buttonClicked(self) -> None:
        if self._env.offlineMode:
            QMessageBox.critical(self, QCoreApplication.translate("AccountTab", "No Internet Connection"), QCoreApplication.translate("AccountTab", "This Feature needs a internet connection"))
            return

        self._env.accountManager.removeAccount(self._account)

        if self._env.accountManager.getSelectedAccount() is None:
            self._mainWindow.hide()
            if self._env.accountManager.addMicrosoftAccount(self) is None:
                self._mainWindow.close()
                return
            self._mainWindow.show()

        self._mainWindow.updateAccountInformation()


class AccountTab(QWidget, Ui_AccountTab):
    def __init__(self, env: "Environment", mainWindow: "MainWindow") -> None:
        super().__init__()

        self.setupUi(self)

        self._env = env
        self._mainWindow = mainWindow

        stretchTableWidgetColumnsSize(self.accountTable)
        self.accountTable.setColumnHidden(_TableColumns.TYPE, not env.debugMode)
        self.accountTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.accountTable.customContextMenuRequested.connect(self._openContextMenu)

        self.addButton.clicked.connect(self._addMicrosoftAccount)

    def _openContextMenu(self, pos: QPoint) -> None:
        menu = QMenu(self)

        addMicrosoftAccount = QAction(QCoreApplication.translate("AccountTab", "Add Account"), self)
        addMicrosoftAccount.triggered.connect(self._addMicrosoftAccount)
        menu.addAction(addMicrosoftAccount)

        if self._env.debugMode:
            addDummyAccount = QAction(QCoreApplication.translate("AccountTab", "Add Dummy Account"), self)
            addDummyAccount.triggered.connect(self._addDummyAccount)
            menu.addAction(addDummyAccount)

        menu.popup(self.accountTable.mapToGlobal(pos))

    def _addMicrosoftAccount(self) -> None:
        account = self._env.accountManager.addMicrosoftAccount(self)

        if account is None:
            return

        self._env.accountManager.setSelectedAccount(account)
        self._mainWindow.updateAccountInformation()

    def _addDummyAccount(self) -> None:
        account = self._env.accountManager.addDummyAccount(self)

        if account is None:
            return

        self._env.accountManager.setSelectedAccount(account)
        self._mainWindow.updateAccountInformation()

    def updateAccountTable(self) -> None:
        clearTableWidget(self.accountTable)

        for account in self._env.accountManager.getAllAccounts():
            row = self.accountTable.rowCount()
            self.accountTable.insertRow(row)

            nameItem = QTableWidgetItem(account.getName())
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.accountTable.setItem(row, _TableColumns.NAME, nameItem)

            typeItem = QTableWidgetItem(account.getType())
            typeItem.setFlags(typeItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.accountTable.setItem(row, _TableColumns.TYPE, typeItem)

            self.accountTable.setCellWidget(row, _TableColumns.SWITCH, _SwitchAccountButton(self._env, account, self._mainWindow))

            self.accountTable.setCellWidget(row, _TableColumns.REMOVE, _RemoveAccountButton(self._env, account, self._mainWindow))
