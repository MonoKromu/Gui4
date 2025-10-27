import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from uis.ui_6 import Ui_MainWindow


class AuthorizationForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.mode = "signIn"
        self.buttonMode.clicked.connect(self.changeMode)

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
        self.editLogin.clear()
        self.editPassword.clear()
        self.editConfirm.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AuthorizationForm()
    ex.show()
    sys.exit(app.exec())