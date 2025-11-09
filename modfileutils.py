import configparser
import sys
import os
import json
from math import trunc
from pathlib import Path
import shutil
import hashlib
import uuid
import tkinter
# from tkinter import filedialog
from constants import DOLPHIN_TOOL, SETTINGS_INI, MODSDB_INI, MOD_PACK_DIR, ORIGINAL_ISO_DIR, MOD_ISO_DIR
from filemanagerutils import get_config_option, set_config_option


# Takes in the modsDB file, adds to the file as needed
def set_modsDB(modsDB_data, path_to_gamemod_folder, gameID=None, mods_to_remove=None):
    # Any and all mods should be appended here if they do not already exist
    configdata = configparser.ConfigParser()
    configdata.read(modsDB_data)

    # get all top-level directories in gameID_mods folder
    path_to_mods_folder = os.path.join(path_to_gamemod_folder, Path(MOD_PACK_DIR.format(gameID)))
    list_of_mods = os.listdir(path_to_mods_folder)

    # Clear all mods from this section so we can repopulate this entirely (better than combing every key-val for matches)
    # REMOVE THIS
    # set_config_option(MODSDB_INI,
    #                   path_to_config=path_to_gamemod_folder,
    #                   section_to_write="Mods",
    #                   option_to_write=str(uuid.uuid4()),
    #                   new_value="",
    #                   clear_section=True)

    # Loop that adds all mods to the mod config section w/ randomly generated GUID as key

    has_no_mods = False
    stored_mods = []

    # Check which mods already exist.
    # IF THEY ALREADY EXIST, keep them and just append the new mods
    try:
        stored_mods = get_config_option(MODSDB_INI,
                                        path_to_config=path_to_gamemod_folder,
                                        section_to_check="Mods",
                                        # option_to_check="",
                                        # return_keys=True,
                                        return_values=True)
    except:
        # If there is no section, allow it through and let it generate
        has_no_mods = True

    for mod_pack in list_of_mods:
        path_of_mod = os.path.join(path_to_mods_folder, Path(mod_pack))
        if path_of_mod in stored_mods and not has_no_mods:
            continue

        # Check if this is actually a directory (zip files should NOT proc here)
        if not os.path.isdir(path_of_mod):
            continue
        # Write to our stored mods
        set_config_option(MODSDB_INI,
                          path_to_config=path_to_gamemod_folder,
                          section_to_write="Mods",
                          option_to_write=str(uuid.uuid4()),
                          new_value=path_of_mod)

    # TODO: add mod.ini writes?
    # Might not be necessary if user installs properly and this is included...
    # But if a mod is created locally, might be necessary for that case...
    # At least, add a blank one I'd think
    # NOTE: any files are safe to put w/ sys-files setup as long as it doesn't breach entry into either folder (i.e. stays at the root above them)

    # If there are mods to remove, do it here
    if mods_to_remove:
        for removal_guid in mods_to_remove:
            set_config_option(MODSDB_INI,
                              path_to_config=path_to_gamemod_folder,
                              section_to_write="Mods",
                              option_to_write=removal_guid,
                              clear_option=True)
    pass

def get_modsDB(modsDB_data, path_to_gamemod_folder, return_full_path=False, return_guids=False):
    # Get all mods from the modsDB.ini file and return
    configdata = configparser.ConfigParser()
    configdata.read(modsDB_data)

    # Make a loop that adds all mods to the mod config section
    list_of_mod_dirs = get_config_option(MODSDB_INI,
                                         path_to_config=path_to_gamemod_folder,
                                         section_to_check="Mods",
                                         return_keys=return_guids,
                                         return_values=True)

    list_of_mods = []

    # Get all basenames of mods here and return

    # If we need the key-value pair (enabling/disabling mods), do it here
    if return_guids:
        for guids, mod_dirs in list_of_mod_dirs.items():
            if return_full_path:
                list_of_mods.append({guids: mod_dirs})
            else:
                list_of_mods.append({guids: os.path.basename(mod_dirs)})

    else:
        for mod_dirs in list_of_mod_dirs:
            if return_full_path:
                list_of_mods.append(mod_dirs)
            else:
                list_of_mods.append(os.path.basename(mod_dirs))

    return list_of_mods


# Takes a file path and generates dictionary data for all files in from the given root downwards
# IF THE path_to_db == NONE, STORE THE DB FILES AT THE ROOT POSITION (add wrapper func with @)
def generate_file_DB_for_mod(path_to_mod_root, path_to_db=None):

    # Create main dict to store all folders
    output_dict = {}

    # TODO: Update later so it's not hardcoded to these two only (this is based off of Sonic Riders GC setup)
    files_dict = {}
    sys_dict = {}

    # We will store this hashmap with the mod.
    # TODO: If it does exist already, only add new entries (can just do with "or" operation)
    for dirpath, dirnames, filenames in os.walk(path_to_mod_root, topdown=True):

        # TODO: Update later so it's not hardcoded to these two folders only
        # GC ISOs follow this format, Wii ISOs have partitions and update folders so we need to add support for those
        # Only add files from these directories
        inFilesPath = os.path.basename(dirpath) == 'files'
        inSysPath = os.path.basename(dirpath) == "sys"

        if (inFilesPath or inSysPath):
            for filename in filenames:
                # IF ON WINDOWS, THIS FILE SHOULD NOT BE ADDED
                # Thanks, windows configs...
                # For context, windows generates this IN FOLDER if the view settings for the folder are changed
                if filename == "desktop.ini":
                    continue

                # Original location to return to
                fileLoc = os.path.join(dirpath, filename)

                # File type (for tagging and organization)
                fileType = os.path.splitext(filename)[1]

                # Checksum of file (in case we need to compare those and source the original)
                with open(fileLoc, 'rb', buffering=0) as f:
                    fileHash256 = hashlib.file_digest(f, 'sha256').hexdigest()

                # Store to proper dict
                if inFilesPath:
                    files_dict.update({filename: [fileLoc, fileType, fileHash256]})

                if inSysPath:
                    sys_dict.update({filename: [fileLoc, fileType, fileHash256]})
            pass

    # path_to_isoDB_root = Path("C:\\Users\\smasi\\Downloads\\RidersDolphin3Windows\\x64\\ReaperCoMods\\CurrentTE")

    # TODO: Update later so it's not hardcoded to these two folders only
    # GC ISOs follow this format, Wii ISOs have partitions and update folders so we need to add support for those
    # Only add these if the dicts exist
    if sys_dict: output_dict.update({"sys": sys_dict})
    if files_dict: output_dict.update({"files": files_dict})

    # After all that parsing, we want to save our dicts as a JSON for later ref
    with open(os.path.join(path_to_db, "db.json"), "w") as file:
        json.dump(output_dict, file, indent=4)  # indent for pretty-printing

    # Read it back
    # with open(os.path.join(path_to_db, "db.json"), "r") as file:
        # loaded_dict = json.load(file)

    # TODO: Add configparser file for mod information
    # Add mod.ini generation here?

    pass


# Load all files from the file folder of the game and parse properly into a hashmap (dict)
# UNUSED RIGHT NOW
def verify_files_from_vanilla_copy(path_to_iso_root=None, path_to_isoDB_root=None):

    # If either of these parameters are none (especially the first since the second can be generated),
    # Get the user to input the paths
    if not path_to_iso_root or not path_to_isoDB_root:
        # Error window here, print what's missing, end function
        print("No path detected!!")
        # path_to_iso_root = Path(input("Please enter the path to the extracted ISO (if it's not a path, prepare for a crash)."))
        return

        # Set path to isoDB to the main mods folder if the user has to enter a path here

    # Error checks for sys AND files not existing (HIGHLY NECESSARY)
    # TODO: Update later so it's not just hardcoded to these two
    if sorted(os.listdir(path_to_iso_root)) != ['files', 'sys']:
        print("Not all folders detected from original game copy!")
    else:
        generate_file_DB_for_mod(path_to_iso_root, path_to_isoDB_root)



    # NOTE: copytree only copies to a NONEXISTING FOLDER. If the folder exists already, that's an error.

    # Copies ENTIRE DIRECTORY to final location (for now)
    # shutil.copytree(path_to_iso_root, path_to_isoDB_root)

    """
    After you get a dictionary of files, any other dictionary merged in (if it has the same keys as the original)
    will replace the original dictionary's key-pair entries.
    
    i.e.:
    If OGDict has 00.adx and newMod has 00.adx:
        OGDict['00.adx'] is replaced by newMod['00.adx'] in final produced dictionary
        
    This is important because we can essentially take the original dict + all added mods and pull the files we need
    from the final dict to the files folder as needed.
    
    How to calculate final dictionary of needed files:
    Vanilla Game Sys/Files Dicts + any mod dicts = final dict
    
    This works because of the collision handling that python does, where the values for keys being merged into the original
    dict overwrites it.
    
    Once final dict is calculated, move all the files in the dict to the files folder as needed.
    
    To get back to vanilla, user only has to save their mods with none turned on, essentially performing this:
    Vanilla Game Sys/Files Dicts + no mods = final dict
    
    functions to create to handle all of this:
    
    store original vanilla files (in a state where files are NOT easily modified)
    
    generate hashes for new mod
    
    add vanilla file dicts + mod dicts to get final dict
    
    move files to final location from final dict
    
    prevent file mods moving if game is running
    
    How do we return the files though?
    If we calculate a new mod database and the files have been moved, what do we do?
    
    """

# Merge ALL databases into final db.json for modded game
# Use base game ISO db as the original dict to add to
def merge_mod_dbs(active_mods, game_title):
    # Get our general mod directory location
    base_mod_dir = get_config_option(SETTINGS_INI, "config", "LauncherLoader", "modsdir")

    # Get all games and then gameID from this dictionary
    list_of_games = get_config_option(SETTINGS_INI, "config", "GameList", return_keys=True, return_values=True)
    gameID = list_of_games[game_title]

    # Combine the base directory + gameID to get to the main game directory
    game_mod_dir = os.path.join(Path(base_mod_dir), Path(gameID))

    # Return all paths to mods in this directory
    path_to_mods_db = os.path.join(game_mod_dir, MODSDB_INI)
    list_of_mod_paths = get_modsDB(modsDB_data=path_to_mods_db, path_to_gamemod_folder=game_mod_dir,
                                   return_full_path=True)
    # list_of_mod_paths = get_config_option(MODSDB_INI, game_modsDB_path, "Mods", return_values=True)

    # Now, find ALL checked mods
    # mod_found_path returns all paths of mods that are valid
    # Use these, append 'db.json' and read those, combine them
    mod_found_path = []
    for mod_path in list_of_mod_paths:
        if os.path.basename(mod_path) in active_mods:
            # We found it, we enable this one
            mod_found_path.append(mod_path)

            # If we found one to enable, regen the databases just in case files were updated
            generate_file_DB_for_mod(mod_path, mod_path)

    # Get ORIGINAL ISO db first
    original_iso_db = os.path.join(Path(game_mod_dir), Path(ORIGINAL_ISO_DIR.format(gameID)))

    combined_file_dict = {}

    with open(os.path.join(original_iso_db, "db.json"), "r") as file:
        combined_file_dict = json.load(file)

    # Load all other dictionaries, OR them into the combined one
    for index in range(len(active_mods)):
        with open(os.path.join(Path(mod_found_path[index]), "db.json"), "r") as file:
            # combined_file_dict.update(json.load(file))
            new_dict_to_add = json.load(file)
            # Get the keys of the dictionary, update that key in combined_file_dict
            new_dict_keys = new_dict_to_add.keys()
            for keys in new_dict_keys:
                combined_file_dict[keys].update(new_dict_to_add[keys])

    # Write dict to gameID_MOD folder
    mod_iso_db = os.path.join(Path(game_mod_dir), Path(MOD_ISO_DIR.format(gameID)))
    with open(os.path.join(mod_iso_db, Path("db.json")), "w") as file:
        json.dump(combined_file_dict, file, indent=4)  # indent for pretty-printing

    return mod_iso_db


def move_mod_files_to_final_place(mod_iso_db):
    # Get file dict from... file
    combined_file_dict = {}
    with open(os.path.join(mod_iso_db, Path("db.json")), "r") as file:
        combined_file_dict = json.load(file)

    # Go through every key (top-level directory), then every key-value[0] to get the file directory to move into gameID_MOD

    # This loop is heavily inefficient. Send help.
    # Get top level directory, then filelist
    for directory, filelist in combined_file_dict.items():
        # Then get filename, then directory (filedata[0])
        # Use this to move.

        # Make the directory first before each iteration
        new_directory = os.path.join(Path(mod_iso_db), Path(directory))

        # Clear this directory first to avoid holdover files
        # Possibly find a way to detect mod files to remove? Add property to dict possibly?

        if os.path.exists(new_directory):
            shutil.rmtree(new_directory)

        # Generate the directory again and place files
        os.makedirs(new_directory, exist_ok=True)

        for filename, filedata in filelist.items():
            shutil.copy(filedata[0], new_directory)
            pass
        pass
    pass

def create_mod_dirs(new_mod_data, path_to_add):
    try:
        os.mkdir(path_to_add)
        if new_mod_data["Create Sys"]:
            sys_path = os.path.join(path_to_add, Path("sys"))
            os.mkdir(sys_path)
        if new_mod_data["Create Files"]:
            files_path = os.path.join(path_to_add, Path("files"))
            os.mkdir(files_path)
        if new_mod_data["Open Folder"]:
            if sys.platform == "win32":
                os.startfile(path_to_add)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path_to_add])
            

    except FileExistsError:
        print("Mod already exists!")
        pass
    except FileNotFoundError:
        print("Path is incorrect!")
        pass
    pass