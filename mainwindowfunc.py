import os.path
import json
import tkinter
from tkinter import filedialog
import shutil

from PyQt6 import QtCore

from constants import DOLPHIN_TOOL, SETTINGS_INI, MODSDB_INI, MOD_PACK_DIR, DB_INI, MOD_ISO_DIR, DOLPHIN_EXE
from filemanagerutils import get_config_option, set_config_option, generate_modsDB_ini
from modfileutils import generate_file_DB_for_mod, set_modsDB, get_modsDB, merge_mod_dbs, move_mod_files_to_final_place
import subprocess
from pathlib import Path, PurePath, WindowsPath

# Get all mods, add then to modsDB, populate list with 'em
def populate_modlist(current_game):

    # Get what games are in our game list
    # By getting the keys, we can track our folders because of our schema (indeed)
    game_dict = get_config_option(SETTINGS_INI, "config", "GameList", return_keys=True, return_values=True)

    # Match the key-value to current_game
    if not game_dict:
        return ["No mods. Open a game and add one!"]

    gameID = game_dict[current_game]

    # Search the main mod directory for the main folder for this game
    game_mod_dir = get_config_option(SETTINGS_INI, "config", "LauncherLoader", "modsdir")
    game_mod_dir = os.path.join(Path(game_mod_dir), gameID)

    # Get the modsDB.ini file and check/add to mods section
    path_to_mods_db = os.path.join(game_mod_dir, MODSDB_INI)
    path_to_mods_folder = os.path.join(game_mod_dir, Path(MOD_PACK_DIR.format(gameID)))

    while True:
        try:
            set_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir, gameID=gameID)
            list_of_mods = get_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir)
            break
        except:
            print("No modsDB.ini found for game! Generating and attempting to add mods...")
            generate_modsDB_ini(path_to_mods_db)

    # Regen DB if a folder does not exist
    for mod in list_of_mods:
        mod_to_test = os.path.join(path_to_mods_folder, Path(mod))
        if not os.path.exists(mod_to_test):
            generate_modsDB_ini(path_to_mods_db, force_overwrite=True)
            set_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir, gameID=gameID)
            list_of_mods = get_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir)
            # Don't need to do this for every one of them since this checks all of them, just break the first time you see it
            break

    print("Loading " + str(len(list_of_mods)) + " mods...")

    return list_of_mods


# Add games and always add "add game option" at the end
def update_gamelist_combobox():
    # Read all games from settings.ini, only return values (the actual game titles)
    # TODO: Remove games that do not actually exist.
    game_list = get_config_option(SETTINGS_INI, "config","GameList", return_keys=True)

    # Always add this at the end to allow user to add more
    game_list.append("Add new game here")
    return game_list


# Allows users to add a new game from dolphin, provided it's an ISO (other file supports coming later)
def add_new_game_from_dolphin():
    # Check if a path to dolphin and the mods dir is set first

    path_to_dolphin = get_config_option(SETTINGS_INI,
                                        "config",
                                          "LauncherLoader",
                                          "dolphindir")
    path_to_mods = get_config_option(SETTINGS_INI,
                                     "config",
                                       "LauncherLoader",
                                       "modsdir")

    if not path_to_dolphin and not path_to_mods:
        # Error window here, print what's missing, end function
        print("Error here! Path to dolphin or path to mods missing.")
        return


    # Open file dialog from here
    tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing

    # Return dol file selected
    # path_to_new_game = Path(filedialog.askopenfilename())
    path_to_new_game = filedialog.askopenfilename()

    if not path_to_new_game:
        return None, None

    path_to_new_game = Path(path_to_new_game)

    # get dolphin tool location
    path_to_dolphintool = os.path.join(Path(path_to_dolphin), Path(DOLPHIN_TOOL))

    # Get header data from dolphintool
    gameID = ""
    gameTitle = ""
    try:
        ans = subprocess.check_output([path_to_dolphintool, "header", "-i", path_to_new_game], text=True)
        print(ans)
        gameID = ans.split()[7]  # Returns gameID from output
        gameTitle = ans.split()[2] # Returns gameTitle from output
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        return

    # Generate new filetree in mods directory with the following spec:
    new_mod_dir = os.path.join(Path(path_to_mods), Path(gameID))
    # dirs_to_make = ["_Mods", "_ISO", "_MOD", "_ISO_DB", "_MOD_DB"]
    dirs_to_make = ["_Mods", "_ISO", "_MOD"]

    for dir_names in dirs_to_make:
        # if "_DB" in dir_names:
        #     os.makedirs(os.path.join(new_mod_dir, Path("DBs"), Path(gameID + dir_names)), exist_ok=True)
        # else:
        os.makedirs(os.path.join(new_mod_dir, Path(gameID + dir_names)), exist_ok=True)

    # using dolphintool, extract entire disc to the ISO folder
    extract_iso_path = os.path.join(new_mod_dir, Path(gameID + dirs_to_make[1]))
    ans = subprocess.check_output([path_to_dolphintool, "extract", "-i", path_to_new_game, "-o", extract_iso_path], text=True)

    # Generate DB files for vanilla ISO
    # iso_db_path = os.path.join(new_mod_dir, Path("DBs"), Path(gameID + dirs_to_make[3]))
    iso_db_path = os.path.join(new_mod_dir, Path(gameID + dirs_to_make[1]))
    generate_file_DB_for_mod(extract_iso_path, iso_db_path)

    # Search for dol (preferably in root, sys folders)
    # path_to_dol = ""
    # testDOL = ""
    # for dirpath, dir_names, filenames in os.walk(path_to_new_game, topdown=True):
    #     # Find dol in directories.
    #     # If found, record and use for later and break loop immediately
    #     testDOL = next((s for s in filenames if ".dol" in s), None)
    #     if testDOL:
    #         path_to_dol = os.path.join(Path(dirpath), Path(testDOL))
    #         break
    #     pass
    """
    /gameID
    __/gameID_Mods (mods for the game itself are stored here)
    __/gameID_ISO_DB (original files are parsed and stored here for base case)
    __/gameID_MOD_DB (final stored mod database)
    __/gameID_ISO (original files of game, extracted)
    __/gameID_MOD (final modded version of game)
    """


    # GENERATE modsDB.ini in root of game folder
    generate_modsDB_ini(os.path.join(new_mod_dir, Path(MODSDB_INI)))

    return gameID, gameTitle

def set_up_directory(directory_option):
    tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
    # Return file selected
    path_to_directory = filedialog.askdirectory()
    set_config_option(SETTINGS_INI,
                      path_to_config=os.path.join(os.getcwd(), "config"),
                      section_to_write="LauncherLoader",
                      option_to_write=directory_option,
                      new_value=path_to_directory)
    return path_to_directory


# Used for enable/disable logic to get the mod in question
def match_mod(game_title, mod_title):
    # Get our general mod directory location
    base_mod_dir = get_config_option(SETTINGS_INI, "config", "LauncherLoader", "modsdir")

    # Get all games and then gameID from this dictionary
    list_of_games = get_config_option(SETTINGS_INI, "config", "GameList", return_keys=True, return_values=True)
    gameID = list_of_games[game_title]

    # Combine the base directory + gameID to get to the main game directory
    game_mod_dir = os.path.join(Path(base_mod_dir), Path(gameID))

    # Return all paths to mods in this directory
    path_to_mods_db = os.path.join(game_mod_dir, MODSDB_INI)

    # Also get the GUIDs, we need that to store in mods.DB.ini
    list_of_mod_paths = get_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir,
                                   return_full_path=True, return_guids=True)
    # list_of_mod_paths = get_config_option(MODSDB_INI, game_modsDB_path, "Mods", return_values=True)

    # Now, find the right mod (the one that was checked, mod_title)
    # Use a loop that parses for it
    mod_found_path = None
    mod_GUID = None
    for mod_path in list_of_mod_paths:
        # os.path.basename(mod_path)
        title_of_path = os.path.basename(list(mod_path.values())[0])
        if title_of_path == mod_title:
            # We found it, we enable this one
            mod_found_path = list(mod_path.values())[0]
            mod_GUID = list(mod_path.keys())[0]
            break

    if not mod_found_path or not mod_GUID:
        print("Error: " + mod_title + " not found. This should not happen.")
        return

    return mod_GUID, mod_found_path, game_mod_dir

def enable_mod(game_title, mod_title):
    mod_GUID, mod_found_path, game_mod_dir = match_mod(game_title, mod_title)

    # If we find the mod (should happen), check if the db.ini is empty.
    # If empty, set it up!
    # If not, pull values from it.
    # Or we can just force setup every time. Would make it easier to get new files added.

    # path_to_db = os.path.join(Path(mod_found_path), Path(DB_INI))

    # Generates the JSON file (db.json)
    generate_file_DB_for_mod(mod_found_path, mod_found_path)

    # Load this file as a dict and merge it with the dict in the mod folder
    # with open(os.path.join(mod_found_path, "db.json"), "r") as file:
    #     loaded_dict = json.load(file)

    # Add this to active_mod in modsDB.ini
    # 1. Get all keys in [Main]
    # 2. Filter keys by 'activemod' in them
    # 3. Count number of those, then add this new mod with that number
    # 3a. e.g. if 0 mods, then this is activeMod0. If there's 1 mod (activeMod0 exists), then this is activeMod1, etc.
    main_sect_keys = get_config_option(MODSDB_INI, path_to_config=game_mod_dir, section_to_check='Main', return_keys=True)
    active_mod_keys = [s for s in main_sect_keys if "activemod" in s]
    # 'activemodcount' is also returned, so subtract 1
    active_mod_list_len = len(active_mod_keys) - 1
    set_config_option(MODSDB_INI,
                      path_to_config=game_mod_dir,
                      section_to_write='Main',
                      option_to_write=str('activemod' + str(active_mod_list_len)),
                      new_value=mod_GUID)

    # Increase active mod count too
    set_config_option(MODSDB_INI,
                      path_to_config=game_mod_dir,
                      section_to_write='Main',
                      option_to_write='activemodcount',
                      new_value=str(active_mod_list_len+1))

    # Now on next load, this option should be CHECKED.
    # If not, we can duplicate active mods (bad)

    print(mod_title + " enabled.\n")

    # Current issues:
    # 1. We can dupe mods
    # 2. If an old mod is active but the directory is gone from [Mods], it permeates and is a dead ID that needs to be removed.
    # 3. Mods can get out of order and update the wrong active mod. Fix list at the end of process if not ordered/starting at 0/
    # 3a. This is priority 1.
    pass

# This is basically our decorator for merging and then moving files
# TODO: Get active mods from modsDB.ini file instead of the checked items
def save_mods_to_modded_game(active_mods, game_title):
    print("Saving " + str(len(active_mods)) + " mods to the database...")
    # This should return a dictionary of ALL necessary mods and save it to gameID_MOD's database
    mod_iso_db_path = merge_mod_dbs(active_mods, game_title)
    # Move ALL mod files to final place in gameID_MOD
    move_mod_files_to_final_place(mod_iso_db_path)
    print("Saved " + str(len(active_mods)) + " to the database.\n")


def disable_mod(game_title, mod_title):
    # Get GUID and path to this particular mod
    mod_GUID, mod_found_path, game_mod_dir = match_mod(game_title, mod_title)

    path_to_mods_db = os.path.join(game_mod_dir, MODSDB_INI)

    # Find said mod in modsDB.ini by searching for all "activemodX" keys and matching to value.
    main_sect_keys = get_config_option(MODSDB_INI,
                                       path_to_config=game_mod_dir,
                                       section_to_check='Main',
                                       return_keys=True,
                                       return_values=True)

    active_mod_dict = dict([(key, val) for key, val in main_sect_keys.items() if "activemod" in key])

    for active_mod, ID in active_mod_dict.items():
        if active_mod != 'activemodcount' and mod_GUID == ID:
            # Remove this key-value pair
            set_config_option(MODSDB_INI,
                              path_to_config=game_mod_dir,
                              section_to_write='Main',
                              option_to_write=active_mod,
                              clear_option=True)
            break

    # Alter the active mod count (note: this was a lazy copy, optimize this man...)
    main_sect_keys = get_config_option(MODSDB_INI, path_to_config=game_mod_dir, section_to_check='Main',
                                       return_keys=True)
    active_mod_keys = [key for key in main_sect_keys if "activemod" in key]
    # 'activemodcount' is also returned, so subtract 1
    active_mod_list_len = len(active_mod_keys) - 1

    # Decrease active mod count too
    set_config_option(MODSDB_INI,
                      path_to_config=game_mod_dir,
                      section_to_write='Main',
                      option_to_write='activemodcount',
                      new_value=str(active_mod_list_len))

    main_sect_keys = get_config_option(MODSDB_INI,
                                       path_to_config=game_mod_dir,
                                       section_to_check='Main',
                                       return_keys=True,
                                       return_values=True)

    # FIX ALL OTHER MOD ENTRY KEYS HERE AND WRITE BACK
    # By getting all values from existing active mod key-pairs, we can re-gen the list ourselves.
    # 1. Get all values of active mods
    # 2. Delete all "activemodX" key pairs
    # 3. Re-gen list with activemod0 = value1, activemod1 = value2, etc.
    active_mod_dict = dict([(key, val) for key, val in main_sect_keys.items() if "activemod" in key])
    active_mod_number = 0
    for active_mod, ID in active_mod_dict.items():
        if active_mod != 'activemodcount':
            # Save the value (ID), remove and make a new key pair, starting at 0
            set_config_option(MODSDB_INI,
                              path_to_config=game_mod_dir,
                              section_to_write='Main',
                              option_to_write=active_mod,
                              clear_option=True)

            set_config_option(MODSDB_INI,
                              path_to_config=game_mod_dir,
                              section_to_write='Main',
                              option_to_write=str('activemod' + str(active_mod_number)),
                              new_value=ID)

            active_mod_number+=1

    print(mod_title + " disabled.\n")
    pass


def get_enabled_mods(game_title, mod_title, return_titles=False):
    # Get all relevant data by matching current item to the mod needed
    if game_title == "Add new game here":
        return QtCore.Qt.CheckState.Unchecked

    mod_GUID, mod_found_path, game_mod_dir = match_mod(game_title, mod_title)

    # Get all active mod keys

    main_sect_keys = get_config_option(MODSDB_INI,
                                       path_to_config=game_mod_dir,
                                       section_to_check='Main',
                                       return_keys=True,
                                       return_values=True)

    active_mod_dict = dict([(key, val) for key, val in main_sect_keys.items() if "activemod" in key])

    # If there's only one, that's always activemodcount, so set everything as unchecked
    if len(active_mod_dict) <= 1:
        if return_titles:
            return None
        else:
            return QtCore.Qt.CheckState.Unchecked

    # If the current item's GUID is in ANY of the active mod dict's values, then check it on
    if mod_GUID in active_mod_dict.values():
        if return_titles:
            return mod_title
        else:
            return QtCore.Qt.CheckState.Checked

    if return_titles:
        return None
    else:
        return QtCore.Qt.CheckState.Unchecked


def start_dolphin_game(game_title):
    path_to_dolphin = get_config_option(SETTINGS_INI,
                                        "config",
                                        "LauncherLoader",
                                        "dolphindir")
    path_to_mods = get_config_option(SETTINGS_INI,
                                     "config",
                                     "LauncherLoader",
                                     "modsdir")

    if not path_to_dolphin and not path_to_mods:
        # Error window here, print what's missing, end function
        print("Error here! Path to dolphin or path to mods missing.")
        return


    # Get what games are in our game list
    # By getting the keys, we can track our folders because of our schema (indeed)
    game_dict = get_config_option(SETTINGS_INI, "config", "GameList", return_keys=True, return_values=True)

    # Match the key-value to current_game
    if not game_dict:
        return ["No mods. Open a game and add one!"]

    gameID = game_dict[game_title]

    # Return dol file selected
    # This should hopefully exist
    path_to_game_dol = os.path.join(Path(path_to_mods), Path(gameID), Path(MOD_ISO_DIR.format(gameID)), Path("sys"), Path("main.dol"))

    if not os.path.exists(path_to_game_dol):
        print("Error here! Path to dol has no sys folder.")
        return

    # get dolphin location, subproc and detach
    path_to_dolphin_exe = os.path.join(Path(path_to_dolphin), Path(DOLPHIN_EXE))

    try:
        dolphin_proc = subprocess.Popen([path_to_dolphin_exe, "-e", path_to_game_dol],
                               creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        return