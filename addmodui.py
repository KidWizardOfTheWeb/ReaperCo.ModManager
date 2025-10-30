import os
import sys

from mainwindowfunc import * # Contains our functionality so we can read this file properly
from constants import * # Contains our paths
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, QComboBox, QVBoxLayout, QWidget, QLineEdit, \
    QDialog

from modfileutils import merge_mod_dbs


# load our main window and hook all behaviors/connections to other windows here
# Functions attached to buttons should be in another file for readability
class AddModWindow(QDialog):
    def __init__(self):
        super().__init__()
        # Load mainwindow file
        uic.loadUi(os.path.join(UI_FOLDER_PATH, 'addmod.ui'), self)


        # self.listWidget.addItems(list_of_mods)

# def run_reorder_mods_loop():
#     app = QApplication(sys.argv)
#     window = ReorderModsWindow()
#     window.show()
#     app.exec()
#
# run_reorder_mods_loop()