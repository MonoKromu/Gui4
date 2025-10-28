import hashlib
import sqlite3
import sys

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeyEvent, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QMenu

from uis.ui_6 import Ui_MainWindow
from uis.ui_6_lib import Ui_LibWindow


class AuthorizationForm(QMainWindow, Ui_MainWindow):
    mode: str
    connection: sqlite3.Connection
    def __init__(self):
        super().__init__()
        self.setup()
        self.buttonMode.clicked.connect(self.changeMode)
        self.buttonEnter.clicked.connect(lambda: self.login() if self.mode == "signIn" else self.register())
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.labelMessage.clear)

    def setup(self):
        self.setupUi(self)
        self.labelConfirm.setVisible(False)
        self.editConfirm.setVisible(False)
        self.editPassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.editConfirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.setTabOrder(self.editLogin, self.editPassword)
        self.setTabOrder(self.editPassword, self.editConfirm)
        self.setTabOrder(self.editConfirm, self.buttonEnter)
        self.mode = "signIn"
        self.connection = sqlite3.connect("files/6.sqlite")
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS users("
                                         "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                                         "username TEXT UNIQUE NOT NULL, "
                                         "password TEXT NOT NULL)")
        self.connection.commit()

    def changeMode(self):
        if self.mode == "signIn":
            self.mode = "signUp"
            self.editConfirm.setVisible(True)
            self.labelConfirm.setVisible(True)
            self.labelQuestion.setText("Already have an account?")
            self.buttonMode.setText("Sign in")
            self.buttonEnter.setText("Create user")
        else:
            self.mode = "signIn"
            self.editConfirm.setVisible(False)
            self.labelConfirm.setVisible(False)
            self.labelQuestion.setText("Don't have an account?")
            self.buttonMode.setText("Sign up")
            self.buttonEnter.setText("Login")
        for label in [self.editLogin, self.editPassword, self.editConfirm, self.labelMessage]:
            label.clear()

    def login(self):
        if len(self.editLogin.text()) != 0 and len(self.editPassword.text()) != 0:
            user = self.connection.cursor().execute("SELECT username, password FROM users WHERE username = ?",
                                                    (self.editLogin.text(),)).fetchall()
            if len(user) == 0:
                self.showMessage("Wrong login or password")
            else:
                hashed = hashlib.md5(self.editPassword.text().encode("utf-8")).hexdigest()
                if hashed != user[0][1]:
                    self.showMessage("Wrong login or password")
                else:
                    self.openLibrary()

    def register(self):
        if len(self.editLogin.text()) != 0 and len(self.editPassword.text()) != 0:
            existingUser = self.connection.cursor().execute("SELECT username, password FROM users WHERE username = ?",
                                                            (self.editLogin.text(),)).fetchall()
            if len(existingUser) > 0:
                self.showMessage("User with such username already exists")
            elif len(self.editPassword.text()) < 6:
                self.showMessage("Too short password")
            elif self.editPassword.text() != self.editConfirm.text():
                self.showMessage("Passwords don't match")
            else:
                self.connection.cursor().execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                                 (self.editLogin.text(),
                                                  hashlib.md5(self.editPassword.text().encode("utf-8")).hexdigest()))
                self.changeMode()
                self.showMessage("User created successfully")
                self.connection.commit()

    def showMessage(self, msg: str):
        self.labelMessage.setText(msg)
        self.timer.stop()
        self.timer.start(3000)

    def openLibrary(self):
        self.library = Library(self.editLogin.text())
        self.library.show()
        self.library.destroyed.connect(QApplication.instance().quit)
        self.hide()
        self.connection.close()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            self.buttonEnter.click()


class Library(QMainWindow, Ui_LibWindow):
    def __init__(self, username: str):
        super().__init__()
        self.selectedRows = []
        self.setupUi(self)
        self.username = username
        self.setWindowTitle(f"Library - {username}")
        self.model = QStandardItemModel()
        self.connection = sqlite3.connect("files/6.sqlite")
        self.initTable()

    def initTable(self):
        self.connection.cursor().execute("CREATE TABLE IF NOT EXISTS books("
                                         "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                                         "title TEXT NOT NULL, "
                                         "author TEXT NOT NULL, "
                                         "year INT CHECK (year > 1700 AND year <= 2025), "
                                         "genre TEXT, "
                                         "image TEXT, "
                                         "added_by TEXT NOT NULL)")
        self.connection.commit()
        self.refillTable()
        self.table.selectionModel().selectionChanged.connect(self.updateSelection)

    def refillTable(self):
        model = QStandardItemModel()
        cursor = self.connection.cursor()
        data = cursor.execute("SELECT * FROM books").fetchall()
        headers = [header[0] for header in cursor.description]
        model.setHorizontalHeaderLabels(headers)
        if len(data) > 0:
            for row in data:
                model.appendRow([QStandardItem(str(item)) for item in row])
        self.table.setModel(model)
        self.model = model

    def updateSelection(self):
        self.selectedRows = set([item.row() for item in self.table.selectionModel().selectedIndexes()])

    def contextMenuEvent(self, event):
        context = QMenu(self)
        action1 = context.addAction("New book")
        action1.triggered.connect(self.addBook)
        context.addSeparator()
        action2 = context.addAction("Edit")
        action2.triggered.connect(self.editBook)
        action3 = context.addAction("Delete")
        action3.triggered.connect(self.deleteBook)

        selectionLength = len(self.selectedRows)
        if selectionLength == 0:
            action2.setDisabled(True)
            action3.setDisabled(True)
        elif selectionLength == 1:
            action2.setDisabled(False)
            action3.setDisabled(False)
        else:
            action2.setDisabled(True)
            action3.setDisabled(False)
        context.exec(event.globalPos())

    def addBook(self):
        pass

    def editBook(self):
        pass

    def deleteBook(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AuthorizationForm()
    ex.show()
    sys.exit(app.exec())