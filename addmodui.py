import os
import sys

from mainwindowfunc import * # Contains our functionality so we can read this file properly
from constants import * # Contains our paths
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
class AddModWindow(QDialog):
    def __init__(self):
        super().__init__()
        # Load file
        uic.loadUi(os.path.join(UI_FOLDER_PATH, 'addnewmod.ui'), self)

    # def accept(self):
    #     if not self.modTitleBox.toPlainText():
    #         print("Here")
    #         self.reject()
    #     else:
    #         print("There")
    #         return
            # event.accept()

    # def reject(self):
    #     pass
        # if not self.modTitleBox.toPlainText():
        #     event.ignore()
        # else:
        #     event.accept()
