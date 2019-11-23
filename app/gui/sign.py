from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import exeptions
from gui.sign_window import Ui_MainWindow
from gui.main import MainWindow


class SignWindow(QtWidgets.QMainWindow):

    def __init__(self, atos):
        super(SignWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.atos = atos
        self.main = MainWindow(self.atos, self)
        self.ui.sign_in.clicked.connect(self.sign_in)

    def sign_in(self):
        login = self.ui.login.text()
        password = self.ui.password.text()
        try:
            self.atos.login(login, password)
            self.main.show()
            self.hide()
        except exeptions.FSExeption as e:
            print(e)
