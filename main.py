from modfileutils import *
from filemanagerutils import *
from mainwindowui import run_main_window_loop

# GLOBALS FOR CONFIG READING


# WE SHOULD ONLY BE DOING SETUP HERE AND RUNNING THE MAIN WINDOW AT THE VERY END OF THE PROCESS.
# KEEP THIS AREA CLEAN (or at least cleaner than I usually do).

# TODO: add CLI options so that gamebanana can actually invoke the registry keys and download properly

if __name__ == '__main__':
    # Initial setup/housekeeping handled on startup here
    cwdPath = os.getcwd()

    # TODO:
    '''
    1. Get user to set mods directory
    2. Allow them to add a game with a button of some sort.
    3. Adding a game does the following:
    a. Extracts entire disc with dolphin.tool
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
    # config_data.read(modsDB_path)

    # If no isodir/modsdir is set, get the user to do so in the settings tab of the frontend first.
    # The isodir will determine what game is active, and choose mods from that folder i.e. "GXEE8P_mods"
    # The modsdir will then generate that new folder so users can put their mods in that
    # One level above that folder is general data for the game itself
    # After they do, verify their vanilla copy and make sure their modsdir can be written to

    # vanilla_copy_path = Path("C:\\Users\\smasi\\Downloads\\RidersDolphin3Windows\\x64\\Games\\ModdedISO")
    # vanilla_DB_path = Path("C:\\Users\\smasi\\Downloads\\RidersDolphin3Windows\\x64\\ReaperCoMods\\GXEE8P\\DBs\\GXEE8P_ISO_DB")
    # verify_files_from_vanilla_copy(vanilla_copy_path, vanilla_DB_path)

    # Finally, read the modDB and populate the main window after generating, starting the main loop.
    run_main_window_loop()

    # The main window should then have hooks basically everywhere to handle the rest of the program. Good luck!