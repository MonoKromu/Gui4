import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QDialog, QMessageBox

from uis.ui_2 import Ui_MainWindow
from uis.ui_2_edit import Ui_Dialog


class EditDialog(QDialog, Ui_Dialog):
    def __init__(self, model: QStandardItemModel, genres, parent, tableCursor: sqlite3.Cursor, rowId: int):
        super().__init__(parent)
        self.tableCursor = tableCursor
        self.rowId = rowId
        self.setupUi(self)
        self.setModal(True)
        self.tableView.setModel(model)
        self.initTable()
        self.genres = genres
        self.show()

    def initTable(self):
        width = self.tableView.width()
        for i, w in enumerate([45, 15, 20, 18]):
            self.tableView.setColumnWidth(i, int(w * width / 100))
        self.tableView.verticalHeader().setVisible(False)

    def accept(self):
        model = self.tableView.model()
        title = model.item(0, 0).text()
        year = model.item(0, 1).text()
        genre = model.item(0, 2).text().lower()
        duration = model.item(0, 3).text()
        values = [title, year, genre, duration]
        error = self.checkErrors(*values)
        if error:
            QMessageBox.critical(self, "Error", error)
        else:
            try:
                if not genre.isdigit():
                    genre = self.genres.get(genre)
                if self.rowId == -1:
                    self.tableCursor.execute("INSERT INTO films (title, year, genre, duration) VALUES (?, ?, ?, ?);",
                                             (title, year, genre, duration))
                else:
                    self.tableCursor.execute("UPDATE films SET title = ?, year = ?, genre = ?, duration = ? WHERE  id = ?",
                                             (title, year, genre, duration, self.rowId))
                self.parent().updateTable()
                super().accept()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"{e}")

    def checkErrors(self, title, year, genre, duration):
        for value in [title, year, genre, duration]:
            if value == "":
                return "Some values are empty"
        if len(title) < 2 or len(title) > 100:
            return "Wrong title"
        elif not year.isdigit() or (int(year) < 1900 or int(year) > 2025):
            return "Wrong year"
        elif not (genre in self.genres.keys() or (genre.isdigit() and int(genre) in self.genres.values())):
            return "Wrong genre"
        elif not duration.isdigit() or (int(duration) < 5 or int(duration) > 600):
            return "Wrong duration"
        else:
            return None


class RemoveDialog(QMessageBox):
    def __init__(self, parent, cursor: sqlite3.Cursor, rowId: int):
        super().__init__(parent)
        self.tableCursor = cursor
        self.rowId = rowId
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.button(QMessageBox.StandardButton.Yes).clicked.connect(self.accept)
        self.setModal(True)
        self.setWindowTitle("Remove Film")
        self.setText("Are you sure you want to delete this film?")
        self.show()

    def accept(self):
        try:
            self.tableCursor.execute("DELETE FROM films WHERE id = ?;", (self.rowId, ))
            self.parent().updateTable()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"{e}")
        finally: super().accept()


class FilmsDB(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.selectedRow = None
        self.tableCursor = sqlite3.connect("files/2.sqlite").cursor()
        self.initTable()
        self.genres = dict(self.tableCursor.execute("SELECT title, id FROM genres").fetchall())
        self.editButton.clicked.connect(self.openEditDialog)
        self.editButton.edit = True
        self.addButton.clicked.connect(self.openEditDialog)
        self.addButton.edit = False
        self.removeButton.clicked.connect(self.removeRow)
        self.updateSelection()

    def initTable(self):
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.updateTable()
        self.table.verticalHeader().setVisible(False)
        width = self.table.width()
        for i, w in enumerate([5, 40, 15, 20, 17]):
            self.table.setColumnWidth(i, int(w * width / 100))

    def updateTable(self):
        model = QStandardItemModel()
        self.tableCursor.execute("SELECT f.id, f.title, f.year, g.title AS genre, f.duration "
                                 "FROM films f LEFT JOIN genres g ON f.genre = g.id")
        data = self.tableCursor.fetchall()
        headers = [header[0] for header in self.tableCursor.description]
        model.setHorizontalHeaderLabels(headers)
        for row in data:
            model.appendRow([QStandardItem(str(item)) for item in row])
        self.table.setModel(model)
        self.table.selectionModel().selectionChanged.connect(self.updateSelection)

    def openEditDialog(self):
        edit = self.sender().edit
        fullModel = self.table.model()
        model = QStandardItemModel()
        headers = []
        rowItems = []
        for col in range(1, fullModel.columnCount()):
            headers.append(fullModel.headerData(col, Qt.Orientation.Horizontal))
            if edit:
                item = QStandardItem(fullModel.item(self.selectedRow, col).text())
            else:
                item = QStandardItem("")
            rowItems.append(item)
        model.setHorizontalHeaderLabels(headers)
        model.appendRow(rowItems)
        rowId = int(fullModel.item(self.selectedRow, 0).text()) if edit else -1
        EditDialog(model, self.genres, self, self.tableCursor, rowId)

    def removeRow(self):
        RemoveDialog(self, self.tableCursor, int(self.table.model().item(self.selectedRow, 0).text()))

    def updateSelection(self):
        rows = [item.row() for item in self.table.selectionModel().selectedIndexes()]
        correct = len(set(rows)) == 1
        if correct:
            self.editButton.setDisabled(False)
            self.removeButton.setDisabled(False)
            self.selectedRow = rows[0]
        else:
            self.editButton.setDisabled(True)
            self.removeButton.setDisabled(True)
            self.selectedRow = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FilmsDB()
    ex.show()
    sys.exit(app.exec())