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
from constants import DOLPHIN_TOOL, SETTINGS_INI, MODSDB_INI, MOD_PACK_DIR, ORIGINAL_ISO_DIR, MOD_ISO_DIR, DB_JSON
from filemanagerutils import get_config_option, set_config_option


# Takes in the modsDB file, adds to the file as needed
# ONLY WRITES TO MODS SECTION, DO NOT TOUCH OTHER SECTIONS PLEASE
def set_modsDB(modsDB_data, path_to_gamemod_folder, gameID=None, mods_to_remove=None):
    # Any and all mods should be appended here if they do not already exist
    configdata = configparser.ConfigParser()
    configdata.read(modsDB_data)

    # get all top-level directories in gameID_mods folder
    path_to_mods_folder = os.path.join(path_to_gamemod_folder, Path(MOD_PACK_DIR.format(gameID)))

    # This used to only check the existing ones in the directory itself
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

        # In the future, we'll handle the deletions here as well. Problem: we'd need the GUIDs, so that's for later.
        # if not mods_to_remove:
        #     mods_to_remove = [v for v in stored_mods if os.path.basename(v) not in list_of_mods]
    except:
        # If there is no section, allow it through and let it generate
        has_no_mods = True

    # in list_of_mods
    for mod_pack in list_of_mods:
        path_of_mod = os.path.join(path_to_mods_folder, Path(mod_pack))
        if path_of_mod in stored_mods and not has_no_mods:
            continue

        # Check if this is actually a directory (zip files should NOT proc here)
        if not os.path.isdir(path_of_mod):
            continue

        # Write to our stored mods, generate new GUID
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
def generate_file_DB_for_mod(path_to_mod_root, path_to_db=None, game_ID=None):

    # Create main dict to store all folders
    output_dict = {}

    # We will store this hashmap with the mod.
    for dirpath, dirnames, filenames in os.walk(path_to_mod_root, topdown=True):

        curr_dir_basename = os.path.basename(dirpath)

        # Try this new structure:
        """
        1. Scour the whole mod/ISO
        2. If we hit a directory, add a key with a dict of the files in it as the value. If it's a file, make it a list.
        3. Things outside of sys/files are inconsequential it seems, so we don't need to check for those (until we hit Wii)
        """

        # Make sure this isn't our ISO path/main mod dir, prevents base directory from being assimilated
        if curr_dir_basename not in path_to_mod_root:
            # 1. Get path as segments up until this folder, go into directory
            # 2. Fill out all files into dict entry
            # 3. Make empty entries of folders for later
            # 4. Traceback our path to filter through our dictionary and place our files properly into their correct directories
            # 5. Repeat

            # This is our dict for all files in this current directory
            curr_dir_dict = {}

            # Get all segments of this path
            # This keeps track of depth here, we can get lost in some deep territory...
            def segment_paths(path_to_split):
                nonlocal game_ID
                segment_list = []
                path_name = Path(path_to_split).resolve().name
                for parent in Path(path_to_split).resolve().parents:
                    path_name = Path(path_name).resolve().name
                    if path_name == ORIGINAL_ISO_DIR.format(game_ID):
                        break
                    segment_list.append(path_name)
                    path_name = parent
                return segment_list

            dict_key_trace = segment_paths(dirpath)

            # Correct our path traceback (it usually comes in backwards)
            dict_key_trace.reverse()

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

                # Store to current directory's dictionary
                curr_dir_dict.update({filename: [fileLoc, fileType, fileHash256]})

            # Add the subfolders of this current directory into our entry
            for dirname in dirnames:
                curr_dir_dict.update({dirname: {}})

            def search_and_update():
                nonlocal output_dict
                nonlocal dirpath
                nonlocal curr_dir_basename
                nonlocal curr_dir_dict
                nonlocal dict_key_trace

                test_dict = output_dict
                # We will recurse down the key list until we find where we need to be, directory wise

                # Recurse until we hit our bottommost directory and make a clone (python does shallow copies by default)
                while dict_key_trace:
                    # Read the path traceback from earlier, keep moving down until it's empty (gone through the whole dict)
                    try:
                        # Normal behavior
                        test_dict = test_dict[dict_key_trace[0]]
                        dict_key_trace.pop(0)
                    except Exception as KeyError:
                        # If key error, add key (covers sys/files folder for now) (MIGHT BE DANGEROUS IN THE FUTURE)
                        test_dict.update({curr_dir_basename: curr_dir_dict})
                        return

                test_dict.update(curr_dir_dict)
                pass

            # Check if subfolder exists first, then update our output dictionary
            search_and_update()
            pass

    # GC ISOs follow this format, Wii ISOs have partitions and update folders

    # After all that parsing, we want to save our dicts as a JSON for later ref
    with open(os.path.join(path_to_db, DB_JSON), "w") as file:
        json.dump(output_dict, file, indent=4)  # indent for pretty-printing

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

# Gets the directory to the game based on game title
def get_path_to_game_folder(game_title):
    # Get our general mod directory location
    base_mod_dir = get_config_option(SETTINGS_INI, "config", "LauncherLoader", "modsdir")

    # Get all games and then gameID from this dictionary
    list_of_games = get_config_option(SETTINGS_INI, "config", "GameList", return_keys=True, return_values=True)
    gameID = list_of_games[game_title]

    # Combine the base directory + gameID to get to the main game directory
    game_mod_dir = os.path.join(Path(base_mod_dir), Path(gameID))

    # Return None if this does not exist
    if not os.path.isdir(game_mod_dir):
        return None

    return game_mod_dir

# Get game ID (probably little use for now since we can use the basename of the game folder)
def get_game_ID(game_title):
    game_dict = get_config_option(SETTINGS_INI, "config", "GameList", return_keys=True, return_values=True)

    # Match the key-value to current_game
    if not game_dict:
        return None

    gameID = game_dict[game_title]

    return gameID

# Merge ALL databases into final db.json for modded game
# Use base game ISO db as the original dict to add to
def merge_mod_dbs(active_mods, game_title):
    game_mod_dir = get_path_to_game_folder(game_title)
    gameID = os.path.basename(game_mod_dir)
    stored_mods = get_config_option(MODSDB_INI,
                                    path_to_config=game_mod_dir,
                                    section_to_check="Mods",
                                    return_keys=True,
                                    return_values=True)

    active_mod_found = []
    for mod_key in active_mods:
        # Use the GUID as our hashmap key to append the proper paths. This preserves order.
        # Genuinely no idea how I didn't do this first, probably because I returned names instead of IDs in the main call.
        mod_found = stored_mods[mod_key]
        active_mod_found.append(mod_found)
        generate_file_DB_for_mod(mod_found, mod_found)

    # Get ORIGINAL ISO db first
    original_iso_db = os.path.join(Path(game_mod_dir), Path(ORIGINAL_ISO_DIR.format(gameID)))

    combined_file_dict = {}

    with open(os.path.join(original_iso_db, DB_JSON), "r") as file:
        combined_file_dict = json.load(file)

    # Load all other dictionaries, OR them into the combined one
    for index in range(len(active_mods)):
        with open(os.path.join(Path(active_mod_found[index]), DB_JSON), "r") as file:
            new_dict_to_add = json.load(file)
            # Get the keys of the dictionary, update that key in combined_file_dict
            new_dict_keys = new_dict_to_add.keys()
            for keys in new_dict_keys:
                combined_file_dict[keys].update(new_dict_to_add[keys])

    # Write dict to gameID_MOD folder
    mod_iso_db = os.path.join(Path(game_mod_dir), Path(MOD_ISO_DIR.format(gameID)))

    # Note: we don't use this for the next function because R/W times slow this down a ton. We now keep this optionally as a debug toggle.
    write_final_DB = int(get_config_option(SETTINGS_INI,
                                       "config",
                                       "AppSettings",
                                       "createDBForFinalOutput"))
    if write_final_DB:
        with open(os.path.join(mod_iso_db, Path(DB_JSON)), "w") as file:
            json.dump(combined_file_dict, file, indent=4)  # indent for pretty-printing

    return mod_iso_db, combined_file_dict


def move_mod_files_to_final_place(mod_iso_db, file_dict):
    # Get file dict calculated from earlier
    combined_file_dict = file_dict

    # Go through every key (top-level directory), then every key-value[0] to get the file directory to move into gameID_MOD

    # This loop is heavily inefficient. Send help.
    # Get top level directory, then filelist.
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
            # check for subfolders.
            # if they exist, make them a directory and place things there
            # if isinstance(filedata, list): this is a file, use [0] for the location for shutil.copy(filedata[0], new_directory)
            # if isinstance(filedata, dict): this is a subfolder, add files/folders from where they come from
            if isinstance(filedata, list):
                shutil.copy(filedata[0], new_directory)
            elif isinstance(filedata, dict):
                recurse_subfolders_on_save(filedata, new_directory, filename)
            pass
        pass
    pass

def recurse_subfolders_on_save(filedata, new_directory, sub_folder):
    # new_directory must be modified to fit subdirectories, so check the dict for it
    new_directory = os.path.join(Path(new_directory), sub_folder)

    if os.path.exists(new_directory):
        shutil.rmtree(new_directory)

    # Generate the directory again and place files
    os.makedirs(new_directory, exist_ok=True)

    for subname, subdata in filedata.items():
        if isinstance(subdata, dict):
            # Recurse and go down more subfolders
            recurse_subfolders_on_save(subdata, new_directory, subname)
        elif isinstance(subdata, list):
            shutil.copy(subdata[0], new_directory)
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