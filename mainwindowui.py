import os
import sys
import time

import threading
import richpresence

from mainwindowfunc import * # Contains our functionality so we can read this file properly
from constants import * # Contains our paths
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QComboBox, QVBoxLayout, QWidget, QLineEdit, \
    QFileDialog

from reordermodsui import ReorderModsWindow
from addmodui import AddModWindow




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

        # GAME COMBOBOX
        # Create a dictionary of added games from the add_new_game function
        self.currentGameCombobox.addItems(update_gamelist_combobox())
        self.currentGameCombobox.activated.connect(self.game_combo_box_option_select)

        # BOTTOM ROW OF BUTTONS
        self.addModButton.clicked.connect(self.create_mod)
        self.refreshListButton.clicked.connect(self.refresh_modsUI)

        # SAVE BUTTONS
        self.saveModsPushbutton.clicked.connect(self.save_mods)
        self.saveAndPlayPushbutton.clicked.connect(self.save_and_start_game)

        # MOD LISTVIEW
        # TODO: Change to tableview instead to allow for multiple columns
        mod_entries = populate_modlist(self.currentGameCombobox.currentText())

        self.model = QtGui.QStandardItemModel()
        self.model.itemChanged.connect(self.get_checked_mod) # Attach to each item's checkbox for enable/disable behaviors
        self.modsListView.setModel(self.model)

        for i in mod_entries:
            item = QtGui.QStandardItem(i)
            item.setEditable(False)  # User cannot edit names
            item.setCheckable(True)  # User can check to enable/disable mods
            item.setCheckState(get_enabled_mods(self.currentGameCombobox.currentText(), item.text()))
            self.model.appendRow(item)  # Add to table
            # TODO: Change to tableview instead to allow for multiple columns
            # TODO: Add column and header with mod details (from mod.ini)
            # TODO: Add ordering box for saving mods (numbered in priority)
        self.set_modbox_title("Loaded " + str(len(mod_entries)) + " mods.\n")
        print("Loaded " + str(len(mod_entries)) + " mods.\n")

    # FUNCTIONS

    def toggle_play_behavior(self, checked):
        set_play_behavior(self.sender().text(), checked)
        pass

    # Adds mods
    def create_mod(self):
        create_window = AddModWindow()
        if create_window.exec():
            # Get ALL relevant details from window here, create new mod dirs as needed

            new_mod_data = {
                "Mod Title": create_window.modTitleBox.toPlainText(),
                "Description": create_window.descBox.toPlainText(),
                "Version": create_window.versionBox.toPlainText(),
                "Author": create_window.authorBox.toPlainText(),
                "Create Sys": create_window.createSysCheckbox.isChecked(),
                "Create Files": create_window.createFilesCheckbox.isChecked(),
                "Open Folder": create_window.openFolderCheckbox.isChecked()
            }

            create_mod_processing(new_mod_data, self.currentGameCombobox.currentText())
            self.refresh_modsUI()
            return

        # If cancelled, don't save.

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
        # 1. Retrieve all active mods
        checked_mods = []
        for index in range(self.model.rowCount()):
            current_item = self.model.item(index)
            enabled_mod = get_enabled_mods(self.currentGameCombobox.currentText(), current_item.text(), return_titles=True)
            if enabled_mod:
                checked_mods.append(enabled_mod)
            pass

        # This allows re-ordering mods to prevent collisions
        # Pauses execution until window is closed
        # TODO: Figure out how to make this optional
        # Add config option for this?

        # If no mods are checked or there's only one mod, just save anyway and skip the window.
        if not checked_mods or len(checked_mods) <= 1:
            save_mods_to_modded_game(checked_mods, self.currentGameCombobox.currentText())
            return

        reorder = ReorderModsWindow(checked_mods)
        checked_mods.clear()
        if reorder.exec():
            for index in range (reorder.listWidget.count()):
                checked_mods.append(reorder.listWidget.item(index).text())
            # 2. Send checked mods for parsing of their DBs
            save_mods_to_modded_game(checked_mods, self.currentGameCombobox.currentText())
            return

        # If cancelled, don't save.
        print("Saving mods cancelled.\n")
        return

    def get_checked_mod(self, item):
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            print(item.text() + " checked. Loading...")
            # Make this ASYNC
            self.set_modbox_title(item.text() + " checked. Loading...")
            # Enable mod:
            # 1. Get mod path
            # 2. Generate DB
            # 3. Add to active mod list
            enable_mod(self.currentGameCombobox.currentText(), item.text())
            self.set_modbox_title(item.text() + " enabled.\n")
        else:
            print(item.text() + " unchecked. Loading...")
            # Make this ASYNC
            self.set_modbox_title(item.text() + " unchecked. Loading...")
            disable_mod(self.currentGameCombobox.currentText(), item.text())
            self.set_modbox_title(item.text() + " disabled.\n")
            pass
        pass

    def refresh_modsUI(self):
        # Check game title, then check mod entries for game
        mod_entries = populate_modlist(self.currentGameCombobox.currentText())

        # If game isn't found, repopulate game list and remove from our settings.ini
        if "INVALID_ENTRIES" in mod_entries:
            self.currentGameCombobox.clear()
            self.currentGameCombobox.addItems(update_gamelist_combobox())
            self.refresh_modsUI() # Refresh one more time with the game at the top of the list before ending
            return

        self.set_modbox_title("Loading " + str(len(mod_entries)) + " mods...")
        # print("Loading " + str(len(list_of_mods)) + " mods...")

        self.model = QtGui.QStandardItemModel()
        self.model.itemChanged.connect(self.get_checked_mod)  # Attach to each item's checkbox for enable/disable behaviors
        self.modsListView.setModel(self.model)
        self.model.clear()  # Clear all items first before adding new mods
        for i in mod_entries:
            item = QtGui.QStandardItem(i)
            item.setEditable(False)  # User cannot edit names
            item.setCheckable(True)  # User can enable/disable mods
            item.setCheckState(get_enabled_mods(self.currentGameCombobox.currentText(), item.text()))
            self.model.appendRow(item)  # Add to table
            # TODO: Change to tableview instead to allow for multiple columns
            # TODO: Add column and header with mod details (from mod.ini)
            # TODO: Add ordering box for saving mods (numbered in priority)
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
