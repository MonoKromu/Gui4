import math
import sys

from PyQt6.QtCore import Qt, QLine, QPointF
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow

from uis.ui_4 import Ui_MainWindow


class RunningButton(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.centralwidget.setMouseTracking(True)
        self.button.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.centralwidget.mapFromParent(event.pos())
        buttonRect = self.button.geometry()

        if buttonRect.contains(pos):
            centerX = buttonRect.x() + buttonRect.width() / 2
            centerY = buttonRect.y() + buttonRect.height() / 2
            dx = pos.x() - centerX
            dy = pos.y() - centerY
            if dx == 0 and dy == 0:
                dx = 1
            length = math.sqrt(dx * dx + dy * dy)
            dxNormalized = dx / length
            dyNormalized = dy / length
            moveDistX = abs(dxNormalized) * (
                        buttonRect.width() / 2 + abs(dx) - abs(dxNormalized) * buttonRect.width() / 2)
            moveDistY = abs(dyNormalized) * (
                        buttonRect.height() / 2 + abs(dy) - abs(dyNormalized) * buttonRect.height() / 2)
            newX = int(buttonRect.x() + -dxNormalized * moveDistX)
            newY = int(buttonRect.y() + -dyNormalized * moveDistY)
            maxX = self.centralwidget.width() - buttonRect.width()
            maxY = self.centralwidget.height() - buttonRect.height()
            if newX < 0:
                newX = maxX
            elif newX > maxX:
                newX = 0
            if newY < 0:
                newY = maxY
            elif newY > maxY:
                newY = 0
            self.button.setGeometry(newX, newY, buttonRect.width(), buttonRect.height())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RunningButton()
    ex.show()
    sys.exit(app.exec())