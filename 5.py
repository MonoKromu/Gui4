import sys
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QLabel, QApplication, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from uis.ui_5 import Ui_MainWindow


class UfoGame(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ufo.setPixmap(QPixmap("files/5_ufo.png").scaled(self.ufo.width(), self.ufo.height()))
        self.keysPressed = {Qt.Key.Key_W: False, Qt.Key.Key_S: False, Qt.Key.Key_A: False, Qt.Key.Key_D: False}
        self.ufo.copiedHorizontal = False
        self.ufo.copiedVertical = False
        self.copies = [self.ufo]
        self.startTimer(10)

    def keyPressEvent(self, event: QKeyEvent):
        pressed = event.key()
        if pressed in self.keysPressed:
            self.keysPressed[pressed] = True

    def keyReleaseEvent(self, event: QKeyEvent):
        released = event.key()
        if released in self.keysPressed:
            self.keysPressed[released] = False

    def getUfoAngle(self):
        angleX = 0
        angleY = 0
        if self.keysPressed[Qt.Key.Key_A]:
            angleX = -1
        elif self.keysPressed[Qt.Key.Key_D]:
            angleX = 1
        if self.keysPressed[Qt.Key.Key_W]:
            angleY = -1
        elif self.keysPressed[Qt.Key.Key_S]:
            angleY = 1
        return [angleX, angleY]

    def timerEvent(self, event):
        ufoAngle = self.getUfoAngle()
        bounds = self.centralwidget.geometry()
        for ufo in self.copies:
            ufo.move(ufo.x() + ufoAngle[0] * 3, ufo.y() + ufoAngle[1] * 3)

            if bounds.contains(ufo.geometry()):
                ufo.copiedHorizontal = False
                ufo.copiedVertical = False
            elif not bounds.intersects(ufo.geometry()):
                self.copies.remove(ufo)
            else:
                copyX, copyY = ufo.x(), ufo.y()
                needCopyHorizontal = False
                needCopyVertical = False

                if ufo.x() < 0:
                    copyX = bounds.width() + ufo.x()
                    needCopyHorizontal = True
                elif ufo.x() + ufo.width() > bounds.width():
                    copyX = ufo.x() - bounds.width()
                    needCopyHorizontal = True

                if ufo.y() < 0:
                    copyY = bounds.height() + ufo.y()
                    needCopyVertical = True
                elif ufo.y() + ufo.height() > bounds.height():
                    copyY = ufo.y() - bounds.height()
                    needCopyVertical = True

                if (needCopyHorizontal and not ufo.copiedHorizontal) or (needCopyVertical and not ufo.copiedVertical):
                    newUfo = QLabel(parent=self.centralwidget)
                    newUfo.setPixmap(ufo.pixmap())
                    newUfo.setGeometry(copyX, copyY, ufo.width(), ufo.height())
                    newUfo.copiedHorizontal = needCopyHorizontal
                    newUfo.copiedVertical = needCopyVertical
                    self.copies.append(newUfo)
                    newUfo.show()

                    if needCopyHorizontal:
                        ufo.copiedHorizontal = True
                    if needCopyVertical:
                        ufo.copiedVertical = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = UfoGame()
    ex.show()
    sys.exit(app.exec())