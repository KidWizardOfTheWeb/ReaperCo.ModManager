from modfileutils import *
from filemanagerutils import *
from mainwindowui import run_main_window_loop

# WE SHOULD ONLY BE DOING SETUP HERE AND RUNNING THE MAIN WINDOW AT THE VERY END OF THE PROCESS.
# KEEP THIS AREA CLEAN (or at least cleaner than I usually do).

# TODO: add CLI options so that gamebanana can actually invoke the registry keys and download properly

if __name__ == '__main__':
    # Initial setup/housekeeping handled on startup here
    cwdPath = os.getcwd()

    '''
    1. Get user to set mods, dolphin directory
    2. Allow them to add a game with combobox.
    3. Adding a game does the following:
    a. Extracts entire disc with dolphin tool
    b. Places it in the mods directory as such:
    /gameID
    __/gameID_mods (mods for the game itself are stored here)
    __/gameID_ISO (original files of game, extracted)
    __/gameID_MOD (final modded version of game)
    '''

    # First, do all the config bits if it does not already exist
    # settings.ini are the launcher-specific settings
    settings_path = generate_config_ini_files(cwdPath)

    # make the config object reader
    config_data = configparser.ConfigParser()

    # This dot operator reads it into the config_data variable. You can now operate it like a dictionary
    config_data.read(settings_path)

    # Finally, read the modDB and populate the main window after generating, starting the main loop.
    run_main_window_loop()

    # The main window should then have hooks basically everywhere to handle the rest of the program. Good luck!