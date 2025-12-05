import os
import sys
import time

import threading

import richpresence
from addmodoptions import AddModFromOptionsWindow

from mainwindowfunc import * # Contains our functionality so we can read this file properly
from constants import * # Contains our paths
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QComboBox, QVBoxLayout, QWidget, QLineEdit, \
    QFileDialog, QHeaderView, QTableWidgetItem, QAbstractItemView

from modfileutils import get_path_to_game_folder
from addmodui import AddModWindow
from warningui import WarningWindow


# This class will handle our multithreading
# We've come far enough in python work that we need to multithread it, be proud

class Worker(QRunnable):
    """Worker thread.

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """Initialise the runner function with passed args, kwargs."""
        self.fn(*self.args, **self.kwargs)

# load our main window and hook all behaviors/connections to other windows here
# Functions attached to buttons should be in another file for readability
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load mainwindow file
        uic.loadUi(os.path.join(UI_FOLDER_PATH, 'mainwindow.ui'), self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # This does technically start a thread, but you can never update the thread... which sucks
        client_id = "1432755181598150908"
        # Init thread in window to access later?
        try:
            RPC_Thread = threading.Thread(name="discord-RPC", target=richpresence.RPC_loop(client_id), daemon=True)
            RPC_Thread.start()
        except Exception as e:
            print("Discord not found. Skipping rich presence...")


        # ATTACH ALL BUTTON BEHAVIOR IN HERE

        # THREAD POOL
        self.threadpool = QThreadPool()

        # SETTINGS BUTTONS - make sure to change these on load depending on the settings toggles
        self.launchDolphinPlayRadiobutton.setChecked(check_play_behavior(self.launchDolphinPlayRadiobutton.text()))
        self.launchDolphinPlayRadiobutton.toggled.connect(self.toggle_play_behavior)
        self.playGameRadiobutton.setChecked(check_play_behavior(self.playGameRadiobutton.text()))
        self.playGameRadiobutton.toggled.connect(self.toggle_play_behavior)
        self.checkBox_5.setChecked(settings_checkbox_init())
        self.checkBox_5.checkStateChanged.connect(self.toggle_checkbox_settings)

        # DIR PLAIN TEXT SETUP
        self.modsDirPathField.setPlainText(get_config_option(SETTINGS_INI,
                                                             "config",
                                                             "LauncherLoader",
                                                             "modsdir"))

        self.dolphinDirPathField.setPlainText(get_config_option(SETTINGS_INI,
                                                                "config",
                                                                "LauncherLoader",
                                                                "dolphindir"))

        self.pluginsDirPathField.setPlainText(get_config_option(SETTINGS_INI,
                                                                 "config",
                                                                 "LauncherLoader",
                                                                 "pluginsdir"))

        # DIR BUTTON SETUP
        self.dolphinDirToolbutton.clicked.connect(self.set_directory)
        self.modsDirToolbutton.clicked.connect(self.set_directory)
        self.pluginsDirToolbutton.clicked.connect(self.set_directory)
        self.openModsPushbutton.clicked.connect(self.open_directory)
        self.openDolphinPushbutton.clicked.connect(self.open_directory)

        # BOTTOM ROW OF BUTTONS
        self.addModButton.clicked.connect(self.install_mod)
        self.refreshListButton.clicked.connect(self.refresh_modsUI)
        self.compileModsButton.clicked.connect(self.compile_mods)

        # SAVE BUTTONS
        self.saveModsPushbutton.clicked.connect(self.save_mods)
        self.saveAndPlayPushbutton.clicked.connect(self.save_and_start_game)

        # GAME COMBOBOX
        # Create a dictionary of added games from the add_new_game function
        # TODO: add "last selected game" as a settings property to open up to the last selected game.
        self.currentGameCombobox.addItems(update_gamelist_combobox())
        self.currentGameCombobox.activated.connect(self.game_combo_box_option_select)

        # MOD QTABLEWIDGET
        mod_entries, mod_info = populate_modlist(self.currentGameCombobox.currentText())

        column_titles = ["Title", "Version", "Author", "Features"]

        self.modsTableWidget.itemChanged.connect(self.get_checked_mod) # Attach to each item's checkbox for enable/disable behaviors
        self.modsTableWidget.setRowCount(len(mod_entries))
        self.modsTableWidget.setColumnCount(4)
        self.modsTableWidget.setHorizontalHeaderLabels(column_titles)
        self.modsTableWidget.verticalHeader().setVisible(False)
        self.modsTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.modsTableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.modsTableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.modsTableWidget.setDragDropOverwriteMode(False)

        # MAKE SURE EVERYTHING IS HOOKED BEFORE CANCELLING FILLING THESE OUT
        if self.currentGameCombobox.count() <= 1:
            # There's no games here, switch the tab to settings and ignore the rest of init
            # dialog = WarningWindow(self, "No mods or games! Add a game with the combobox.")
            # dialog.exec()
            print("No mods or games! Add a game with the combobox.")
            self.tabWidget.setTabEnabled(0, False)
            self.tabWidget.setCurrentIndex(1)
            return

        if not mod_info:
            # There's no mods here, don't fill out mod list
            # dialog = WarningWindow(self, "No mods! Add some mods with the \"Add mod\" button on the mods screen.")
            # dialog.exec()
            print("No mods! Add some mods with the \"Add mod\" button on the mods screen.")
            return

        row = 0
        for info in mod_info:
            # Make item
            title_item = QtWidgets.QTableWidgetItem(info["title"])
            title_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            ver_item = QtWidgets.QTableWidgetItem(info["version"])
            ver_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            auth_item = QtWidgets.QTableWidgetItem(info["author"])
            auth_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            # desc_item = QtWidgets.QTableWidgetItem(info["description"])
            # desc_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)

            title_item.setCheckState(is_mod_enabled(self.currentGameCombobox.currentText(), title_item.text()))
            self.modsTableWidget.blockSignals(True)
            self.modsTableWidget.setItem(row, 0, title_item)
            self.modsTableWidget.setItem(row, 1, ver_item)
            self.modsTableWidget.setItem(row, 2, auth_item)
            # self.modsTableWidget.setItem(row, 3, desc_item)
            self.modsTableWidget.blockSignals(False)
            row += 1

        self.set_modbox_title("Loaded " + str(len(mod_entries)) + " mods.\n")
        print("Loaded " + str(len(mod_entries)) + " mods.\n")

    # FUNCTIONS

    # This runs literally every time they click the window. I wish there was a better way to do this.
    # def focusInEvent(self, event):
    #     # super().focusInEvent(event)  # Call the base class implementation
    #     self.refresh_modsUI()
    #     pass

    def compile_mods(self):
        pass
        # dialog = WarningWindow(self)
        # if dialog.exec():
        #     print("!")
        # else:
        #     print("...")

    def toggle_checkbox_settings(self, checked):
        save_checkbox_settings(self.sender().text(), checked)
        pass

    def toggle_play_behavior(self, checked):
        set_play_behavior(self.sender().text(), checked)
        pass

    # Adds mods
    def install_mod(self):
        install_options_window = AddModFromOptionsWindow()
        if install_options_window.exec():
            # Handle options
            if install_options_window.createModRadioButton.isChecked():
                create_mod_processing(self.currentGameCombobox.currentText())

            if install_options_window.installFolderRadioButton.isChecked():
                path_to_directory = QFileDialog.getOpenFileName(self, caption="Select Mod Zip archive")
                # Ensure we have a path here, otherwise do nothing.
                if path_to_directory[0]:
                    install_mod_by_folder(self.currentGameCombobox.currentText(), path_to_directory[0])
                pass

            if install_options_window.installArchiveRadioButton.isChecked():
                # path_to_directory = QFileDialog.getExistingDirectory(self, caption="Select Mod Folder")
                # install_mod_by_folder(self.currentGameCombobox.currentText(), path_to_directory)
                pass

            self.refresh_modsUI()
            return
        pass

    # Handles text display for info
    def set_modbox_title(self, text):
        self.modsBox.setTitle(text)
        pass

    # Wrap save mods and start the dolphin game selected
    def save_and_start_game(self):
        self.save_mods()
        start_dolphin_game(self.currentGameCombobox.currentText())
        pass

    def save_mods(self):
        # Save ALL activated mod databases here

        # So instead of getting enabled mods, get the mods that are checked, from top to bottom

        # Reconstruct our DB (yes, fully with new GUIDs)
        game_mod_dir = get_path_to_game_folder(self.currentGameCombobox.currentText())
        path_to_mods_db = os.path.join(game_mod_dir, MODSDB_INI)
        generate_modsDB_ini(path_to_mods_db, force_overwrite=True)
        gameID = os.path.basename(game_mod_dir)
        set_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir, gameID=gameID)

        # Now add our checked mods as active mods
        checked_mods = []
        for index in range(self.modsTableWidget.rowCount()):
            # Get current mod and see if checked
            current_item = self.modsTableWidget.item(index, 0)
            # If checked, add to our modsDB and append to our table
            if current_item.checkState() == QtCore.Qt.CheckState.Checked:
                has_been_enabled, mod_GUID = enable_mod(self.currentGameCombobox.currentText(), current_item.text(), return_GUID=True)
                if has_been_enabled:
                    # Changed this to append GUIDs instead, so we can just filter those in order
                    # checked_mods.append(current_item.text())
                    checked_mods.append(mod_GUID)
                pass
            pass


        # For now, this ensures that everything at the top of the list is prioritized. We will make this a toggle later.
        checked_mods.reverse()
        save_mods_to_modded_game(checked_mods, self.currentGameCombobox.currentText())
        self.refresh_modsUI()
        return

    def get_checked_mod(self, item):
        if item.column() != 0:
            # For QTableView, do NOT make anything checkable here.
            return
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            # REMOVED: handled at save_mods()
            # print(item.text() + " checked. Loading...")
            # Make this ASYNC
            # self.set_modbox_title(item.text() + " checked. Loading...")
            # Enable mod:
            # 1. Get mod path
            # 2. Generate DB
            # 3. Add to active mod list

            # enable_mod(self.currentGameCombobox.currentText(), item.text())
            self.set_modbox_title(item.text() + " enabled.\n")
        else:
            # REMOVED: handled at save_mods()
            # print(item.text() + " unchecked. Loading...")
            # Make this ASYNC
            # self.set_modbox_title(item.text() + " unchecked. Loading...")
            # disable_mod(self.currentGameCombobox.currentText(), item.text())
            self.set_modbox_title(item.text() + " disabled.\n")
            pass
        return

    def refresh_modsUI(self):
        # Check game title, then check mod entries for game
        # TODO: rework this into a function
        self.tabWidget.setTabEnabled(0, True)
        mod_entries, mod_info = populate_modlist(self.currentGameCombobox.currentText())

        # If game isn't found, repopulate game list and remove from our settings.ini
        if "INVALID_ENTRIES" in mod_entries:
            self.currentGameCombobox.clear()
            self.currentGameCombobox.addItems(update_gamelist_combobox())
            self.refresh_modsUI() # Refresh one more time with the game at the top of the list before ending
            return

        self.set_modbox_title("Loading " + str(len(mod_entries)) + " mods...")

        column_titles = ["Title", "Version", "Author", "Features"]

        self.modsTableWidget.setRowCount(len(mod_entries))
        self.modsTableWidget.setColumnCount(4)
        self.modsTableWidget.setHorizontalHeaderLabels(column_titles)
        self.modsTableWidget.verticalHeader().setVisible(False)
        self.modsTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.modsTableWidget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.modsTableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.modsTableWidget.setDragDropOverwriteMode(False)

        row = 0
        for info in mod_info:
            # Make item
            title_item = QtWidgets.QTableWidgetItem(info["title"])
            title_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            ver_item = QtWidgets.QTableWidgetItem(info["version"])
            ver_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            auth_item = QtWidgets.QTableWidgetItem(info["author"])
            auth_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)

            title_item.setCheckState(is_mod_enabled(self.currentGameCombobox.currentText(), title_item.text()))
            self.modsTableWidget.blockSignals(True)
            self.modsTableWidget.setItem(row, 0, title_item)
            self.modsTableWidget.setItem(row, 1, ver_item)
            self.modsTableWidget.setItem(row, 2, auth_item)
            self.modsTableWidget.blockSignals(False)
            row += 1

        # Note: move this modbox title set somewhere else, so I can show how many are saved
        print("Loaded " + str(len(mod_entries)) + " mods.\n")
        self.set_modbox_title("Loaded " + str(len(mod_entries)) + " mods.\n")
        pass


    # Opens the directory for these
    def open_directory(self):
        sent_button = self.sender()
        if sent_button == self.openModsPushbutton:
            if sys.platform == "win32":
                os.startfile(get_config_option(SETTINGS_INI,
                                            "config",
                                            "LauncherLoader",
                                            "modsdir"))
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, get_config_option(SETTINGS_INI,
                                            "config",
                                            "LauncherLoader",
                                            "modsdir")])

        if sent_button == self.openDolphinPushbutton:
            if sys.platform == "win32":
                os.startfile(get_config_option(SETTINGS_INI,
                                            "config",
                                            "LauncherLoader",
                                            "dolphindir"))
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, get_config_option(SETTINGS_INI,
                                            "config",
                                            "LauncherLoader",
                                            "dolphindir")])
        pass


    # Sets a directory into the correct config file for later use, update text box
    def set_directory(self):
        sent_button = self.sender()
        if sent_button == self.modsDirToolbutton:
            path_to_directory = QFileDialog.getExistingDirectory(self, caption="Select Mod Directory", options=QFileDialog.Option.ShowDirsOnly)
            plaintext = set_up_directory(path_to_directory, 'modsdir')
            self.modsDirPathField.setPlainText(plaintext)
        elif sent_button == self.dolphinDirToolbutton:
            path_to_directory = QFileDialog.getExistingDirectory(self, caption="Select Dolphin Directory", options=QFileDialog.Option.ShowDirsOnly)
            self.dolphinDirPathField.setPlainText(set_up_directory(path_to_directory, 'dolphindir'))
        elif sent_button == self.pluginsDirToolbutton:
            path_to_directory = QFileDialog.getExistingDirectory(self, caption="Select Plugins Directory", options=QFileDialog.Option.ShowDirsOnly)
            self.pluginsDirPathField.setPlainText(set_up_directory(path_to_directory, 'pluginsdir'))
        pass


    # Adds a new game or refreshes the mods list view for the new game chosen
    def game_combo_box_option_select(self):
        selected_item = self.currentGameCombobox.currentText()
        if selected_item == "Add new game here":
            path_to_new_game = QFileDialog.getOpenFileName(self, caption="Select Game", filter="Games (*.iso)")
            try:
                gameID, gameTitle = add_new_game_from_dolphin(path_to_new_game[0])
            except Exception as e:
                print("No file selected. Please select a game.\n")
                gameID = None
                gameTitle = None

            if gameID is None and gameTitle is None:
                return

            # Checks if game is already in list to prevent duplicates
            AllItems = [self.currentGameCombobox.itemText(i) for i in range(self.currentGameCombobox.count())]

            if gameTitle.lower() not in AllItems:
                # Add this game title to settings.ini, set box to new title
                # gameTitle MUST BE ONE CONTINUOUS STRING TO WORK IN INI
                gameTitle = gameTitle.replace(" ", "")
                self.currentGameCombobox.insertItem(0, gameTitle.lower())
                set_config_option(SETTINGS_INI,
                                  path_to_config=os.path.join(os.getcwd(), "config"),
                                  section_to_write="GameList",
                                  option_to_write=gameTitle,
                                  new_value=gameID)

            self.currentGameCombobox.setCurrentText(gameTitle.lower())
            self.refresh_modsUI()
        else:
            # Profile changed, update mod list here
            self.refresh_modsUI()
        pass


# Runs our main window here, executed from main.py
def run_main_window_loop():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
