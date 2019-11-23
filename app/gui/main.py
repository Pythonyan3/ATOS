from PyQt5 import QtWidgets
import exeptions
from gui.file_widget import CustomWidget
from gui.main_window import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, atos, sign_window):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.sign_window = sign_window
        self.atos = atos
        self.show_files()

    def show_files(self):
        x, files = self.atos.show_dir(self.atos.location)
        path = self.atos.location
        path = path if path else '/'
        self.ui.lineEdit.setText(path)
        self.ui.tableWidget.setColumnCount(5)
        self.ui.tableWidget.setRowCount(1)
        i, j = 0, 0
        for file in files.values():
            if file.is_dir():
                item = CustomWidget(file.full_name, "img/folder.png")
            else:
                item = CustomWidget(file.full_name, "img/file.png")
            self.ui.tableWidget.setCellWidget(j, i, item)
            i += 1
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()
