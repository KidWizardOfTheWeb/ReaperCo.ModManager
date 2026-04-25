import os
import sys

from mainwindowfunc import * # Contains our functionality so we can read this file properly
from constants import * # Contains our paths
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
class WindowFactory(QDialog):
    def __init__(self, parent=None, title="Dialog", main_text="PLACEHOLDER.", window_file=""):
        super().__init__(parent)
        # Load file
        if window_file:
            uic.loadUi(os.path.join(UI_FOLDER_PATH, window_file), self)