import random
import sys

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QMouseEvent, QPen, QBrush, QKeyEvent, QPolygonF
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene

from uis.ui_3 import Ui_MainWindow


class Painter(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pos = QPointF()
        self.graphicsView.setScene(QGraphicsScene())
        self.graphicsView.scene().setSceneRect(QRectF(self.graphicsView.rect()))

        self.graphicsView.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.graphicsView.setMouseTracking(True)

        self.graphicsView.mousePressEvent = self.graphicsMousePressEvent
        self.graphicsView.keyPressEvent = self.graphicsKeyPressEvent
        self.graphicsView.mouseMoveEvent = self.graphicsMouseMoveEvent

    def graphicsMousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.graphicsView.scene().addEllipse(self.pos.x() - 25, self.pos.y() - 25, 50, 50,
                                                 QPen(self.getRandomColor(), 2), QBrush(self.getRandomColor()))
        elif event.button() == Qt.MouseButton.RightButton:
            self.graphicsView.scene().addRect(self.pos.x() - 25, self.pos.y() - 25, 50, 50,
                                                 QPen(self.getRandomColor(), 2), QBrush(self.getRandomColor()))

    def graphicsKeyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.graphicsView.scene().addPolygon(QPolygonF([
                QPointF(self.pos.x() - 25, self.pos.y() - 25),
                QPointF(self.pos.x() + 25, self.pos.y() - 25),
                QPointF(self.pos.x(), self.pos.y() + 25)
            ]), QPen(self.getRandomColor(), 2), QBrush(self.getRandomColor()))

    def graphicsMouseMoveEvent(self, event: QMouseEvent):
        self.pos = self.graphicsView.mapToScene(event.pos())


    def getRandomColor(self):
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Painter()
    ex.show()
    sys.exit(app.exec())