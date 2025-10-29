import hashlib
import sqlite3
import sys

from PyQt6.QtCore import QTimer, Qt, QRegularExpression, QRect
from PyQt6.QtGui import QKeyEvent, QStandardItemModel, QStandardItem, QRegularExpressionValidator, QIntValidator, \
    QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QMenu, QHeaderView, QDialog, QStyledItemDelegate, \
    QTableWidget, QTableView, QMessageBox

from uis.ui_6_auth import Ui_MainWindow
from uis.ui_6_edit import Ui_Dialog
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
        self.searchAuthor.textChanged.connect(self.filter)
        self.searchTitle.textChanged.connect(self.filter)
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

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 70)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 100)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 70)

        self.table.verticalHeader().setVisible(False)
        self.table.setItemDelegate(ImageDelegate(self.table, self))
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def refillTable(self):
        model = QStandardItemModel()
        cursor = self.connection.cursor()
        data = cursor.execute("SELECT * FROM books").fetchall()
        headers = [header[0] for header in cursor.description]
        model.setHorizontalHeaderLabels(headers)
        if len(data) > 0:
            for row in data:
                model.appendRow([QStandardItem(str(item)) if str(item) != "None" else QStandardItem() for item in row])
        self.table.setModel(model)
        for row in range(model.rowCount()):
            self.table.setRowHeight(row, 100)
        self.model = model
        self.table.selectionModel().selectionChanged.connect(self.updateSelection)

    def updateSelection(self):
        self.selectedRows = list(set([item.row() for item in self.table.selectionModel().selectedIndexes()]))

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
        dialog = EditDialog("add", "files/6.sqlite", self.username, parent=self)
        dialog.show()
        dialog.finished.connect(self.refillTable)

    def editBook(self):
        bookId = int(self.model.item(self.selectedRows[0], 0).text())
        dialog = EditDialog("edit", "files/6.sqlite", self.username, bookId=bookId,  parent=self)
        dialog.show()
        dialog.finished.connect(self.refillTable)

    def deleteBook(self):
        accept = QMessageBox.question(self, "Warning", f"Do you really want to delete {len(self.selectedRows)} book(s)?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if accept:
            ids = [int(self.model.item(row, 0).text()) for row in self.selectedRows]
            try:
                self.connection.cursor().execute(f"DELETE FROM books WHERE id IN ({','.join('?' * len(ids))})",
                                                 ids)
                self.connection.commit()
                self.refillTable()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Database error: {e}")

    def filter(self):
        title = self.searchTitle.text().lower()
        author = self.searchAuthor.text().lower()
        for row in range(self.model.rowCount()):
            match = ((title in self.model.item(row, 1).text().lower() or title == "")
                     and (author in self.model.item(row, 2).text().lower() or author == ""))
            self.table.setRowHidden(row, not match)

class EditDialog(QDialog, Ui_Dialog):
    def __init__(self, mode: str, db: str, user: str, bookId=-1, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.mode = mode
        self.bookId = bookId
        self.user = user
        self.setModal(True)
        self.connection = sqlite3.connect(db)
        self.initTable()
        self.setWindowTitle("Add book" if mode == "add" else "Edit book")
        self.buttonBox.accepted.connect(self.addBook if mode == "add" else self.editBook)
        self.buttonBox.rejected.connect(self.reject)

    def initTable(self):
        model = QStandardItemModel()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (self.bookId, ))
        headers = [header[0] for header in cursor.description]
        model.setHorizontalHeaderLabels(headers)
        data = cursor.fetchall()
        if len(data) > 0:
            model.appendRow([QStandardItem(str(item)) if str(item) != "None" else QStandardItem() for item in data[0]])
        else:
            model.appendRow([QStandardItem()] * len(headers))
        if self.mode == "add":
            model.setItem(0, len(headers) - 1, QStandardItem(self.user))
        self.tableView.setModel(model)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setItemDelegate(ValidatorDelegate(self.tableView, self))
        self.tableView.setEditTriggers(QTableView.EditTrigger.DoubleClicked)

        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tableView.setColumnWidth(0, 50)
        self.tableView.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tableView.setColumnWidth(3, 70)
        self.tableView.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tableView.setColumnWidth(4, 70)
        self.tableView.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.tableView.setColumnWidth(5, 100)

    def addBook(self):
        values = self.getValues()
        self.sendRequest("INSERT INTO books (title, author, year, genre, image, added_by) "
                         "VALUES (?, ?, ?, ?, ?, ?)", values[1:])

    def editBook(self):
        values = self.getValues()
        values.append(values[0])
        self.sendRequest("UPDATE books SET title = ?, author = ?, year = ?, "
                         "genre = ?, image = ?, added_by = ? WHERE id = ?", values[1:])

    def sendRequest(self, req: str, values):
        try:
            self.connection.cursor().execute(req, values)
            self.connection.commit()
            self.connection.close()
            super().accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")

    def getValues(self):
        model = self.tableView.model()
        values = []
        for column in range(model.columnCount()):
            values.append(model.data(model.index(0, column)))
        return values

    def reject(self):
        self.connection.close()
        super().reject()


class ValidatorDelegate(QStyledItemDelegate):
    def __init__(self, table: QTableWidget, parent=None):
        super().__init__(parent)
        self.table = table

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        header = self.table.model().headerData(index.column(), Qt.Orientation.Horizontal)
        if header in ["id", "added_by"]:
            editor.setReadOnly(True)
        elif header in ["title", "author", "image"]:
            editor.setValidator(QRegularExpressionValidator(QRegularExpression(r".{0,30}")))
        elif header == "genre":
            editor.setValidator(QRegularExpressionValidator(QRegularExpression(r".{0,15}")))
        elif header == "year":
            editor.setValidator(QIntValidator(1701, 2025))
        return editor


class ImageDelegate(QStyledItemDelegate):
    def __init__(self, table: QTableView, parent=None):
        super().__init__(parent)
        self.table = table

    def paint(self, painter, option, index):
        header = self.table.model().headerData(index.column(), Qt.Orientation.Horizontal)
        if header == "image":
            path = self.table.model().item(index.row(), index.column()).text()
            pixmap = QPixmap(path)
            if pixmap.isNull():
                pixmap.load("files/images/default.jpg")
            pixmap = pixmap.scaled(
                option.rect.width() - 4,
                option.rect.height() - 4,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            if pixmap:
                x = option.rect.center().x() - pixmap.width() // 2
                y = option.rect.center().y() - pixmap.height() // 2
                painter.drawPixmap(QRect(x, y, pixmap.width(), pixmap.height()), pixmap)
        else:
            super().paint(painter, option, index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AuthorizationForm()
    ex.show()
    sys.exit(app.exec())