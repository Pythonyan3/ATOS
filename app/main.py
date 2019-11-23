import sys
import atos
from terminal import Terminal
from PyQt5 import QtWidgets
from gui.sign import SignWindow
from gui.main import MainWindow
from colorama import init

if __name__ == "__main__":

    atos = atos.Atos('os.txt')

    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        app = QtWidgets.QApplication([])
        sign = SignWindow(atos)
        sign.show()

        sys.exit(app.exec())
    else:
        init()
        terminal = Terminal('os.txt')
        terminal.run()
