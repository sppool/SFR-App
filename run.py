from PyQt5 import QtWidgets

from controller import MainWindow_controller

import sys
import os
import pathlib
os.chdir(pathlib.Path(__file__).parent.absolute())  # 把目前Path移動到本檔案處

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec_())
