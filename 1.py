import csv
import sys

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem, QAbstractItemView, QComboBox

from uis.ui_1 import Ui_MainWindow


class ResultsTable(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.schools = []
        self.classes = []
        self.fillTable("1.csv")
        self.fillComboBox(self.comboSchool, self.schools)
        self.fillComboBox(self.comboClass, self.classes)

    def fillTable(self, csvPath: str):
        with open(csvPath, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=',', quotechar='"')
            next(reader)
            for i, row in enumerate(reader):
                name = " ".join(row[1].split()[3:])
                login = row[2]
                schoolNumber, classNumber = [int(x) for x in login.split("-")[2:4]]
                if schoolNumber not in self.schools:
                    self.schools.append(schoolNumber)
                if classNumber not in self.classes:
                    self.classes.append(classNumber)
                score = row[7]

                self.table.setRowCount(self.table.rowCount() + 1)
                self.table.setItem(i, 0, QTableWidgetItem(login))
                self.table.setItem(i, 1, QTableWidgetItem(name))
                self.table.setItem(i, 2, QTableWidgetItem(score))
                self.table.setItem(i, 3, QTableWidgetItem(str(schoolNumber)))
                self.table.setItem(i, 4, QTableWidgetItem(str(classNumber)))
        self.schools.sort()
        self.classes.sort()
        self.table.setColumnHidden(3, True)
        self.table.setColumnHidden(4, True)

    def fillComboBox(self, box: QComboBox, values):
        box.addItem("Все")
        box.addItems([str(x) for x in values])
        box.setCurrentIndex(0)
        box.currentIndexChanged.connect(self.filter)

    def filter(self):
        schoolFilter = self.comboSchool.currentText()
        classFilter = self.comboClass.currentText()
        visibleScores = []

        for row in range(self.table.rowCount()):
            schoolText = self.table.item(row, 3).text()
            classText = self.table.item(row, 4).text()
            schoolMatch = (schoolFilter == "Все") or (schoolText == schoolFilter)
            classMatch = (classFilter == "Все") or (classText == classFilter)

            if schoolMatch and classMatch:
                score = int(self.table.item(row, 2).text())
                visibleScores.append(score)

        if visibleScores:
            topScores = sorted(set(visibleScores), reverse=True)[:3]
        else:
            topScores = []

        for row in range(self.table.rowCount()):
            schoolText = self.table.item(row, 3).text()
            classText = self.table.item(row, 4).text()
            schoolMatch = (schoolFilter == "Все") or (schoolText == schoolFilter)
            classMatch = (classFilter == "Все") or (classText == classFilter)
            self.table.setRowHidden(row, not (schoolMatch and classMatch))

            if schoolMatch and classMatch:
                score = int(self.table.item(row, 2).text())
                color = QColor(255, 255, 255)
                if not (schoolFilter == "Все" and classFilter == "Все") and topScores:
                    if len(topScores) > 0 and score == topScores[0]:
                        color = QColor(255, 215, 0)
                    elif len(topScores) > 1 and score == topScores[1]:
                        color = QColor(192, 192, 192)
                    elif len(topScores) > 2 and score == topScores[2]:
                        color = QColor(205, 127, 50)
                for col in range(self.table.columnCount()):
                    self.table.item(row, col).setBackground(color)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ResultsTable()
    ex.show()
    sys.exit(app.exec())