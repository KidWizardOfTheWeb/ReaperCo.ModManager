import configparser
import sys
import os
import json
from math import trunc
from pathlib import Path
import shutil
import hashlib
import uuid
# import datetime
import tkinter
# from tkinter import filedialog
from constants import DOLPHIN_TOOL, SETTINGS_INI, MODSDB_INI, MOD_PACK_DIR, ORIGINAL_ISO_DIR, MOD_ISO_DIR, DB_JSON
from filemanagerutils import get_config_option, set_config_option
from warningui import WarningWindow


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

def generate_db_processing(path_to_read):
    file_dict = generate_file_DB_for_mod_pack(path_to_read)
    with open(os.path.join(path_to_read, DB_JSON), "w") as file:
        json.dump(file_dict, file, indent=4)  # indent for pretty-printing

# Recursive implementation of generate_file_DB_for_mod(). Can save time, but will probably suffer on longer mods.
def generate_file_DB_for_mod_pack(curr_path):
    if os.path.isdir(curr_path):
        # if the given path is a directory, add it to the dict as a key, then update the values
        output_dict = {}
        for item in os.listdir(curr_path):
            # check for subfolders.
            # if they exist, make them a directory and place things there
            if item == 'db.json' or item == 'modinfo.ini':
                continue
            full_path = os.path.join(curr_path, item)
            if os.path.isdir(full_path):
                # Add the directory as a key with value none, then recurse and go deeper
                output_dict[item] = generate_file_DB_for_mod_pack(full_path)
                pass
            else:
                with open(full_path, 'rb', buffering=0) as f:
                    fileHash256 = hashlib.file_digest(f, 'sha256').hexdigest()
                output_dict.update({item: [full_path, os.path.splitext(item)[1], fileHash256]})
                pass
        return output_dict
    print("DB generation finished.")
    pass

# Takes a file path and generates dictionary data for all files in from the given root downwards
# IF THE path_to_db == NONE, STORE THE DB FILES AT THE ROOT POSITION (add wrapper func with @)
# This function will be heading to the glue factory soon. Was my best attempt without recursion originally, but recursion is too good.
# Now unused and ready for deletion soon.
def generate_file_DB_for_mod(path_to_mod_root, path_to_db=None, game_ID=None, mod_title=None):

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
                    #  or path_name == mod_title
                    if path_name == ORIGINAL_ISO_DIR.format(game_ID) or path_name == MOD_PACK_DIR.format(game_ID):
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
                if len(dict_key_trace) > 2:
                    dict_key_trace.pop(0)
                while dict_key_trace:
                    # Read the path traceback from earlier, keep moving down until it's empty (gone through the whole dict)
                    try:
                        # Normal behavior
                        test_dict = test_dict[dict_key_trace[0]]
                        dict_key_trace.pop(0)
                    except Exception as KeyError:
                        # If key error, add key (covers sys/files folder for now) (MIGHT BE DANGEROUS IN THE FUTURE)
                        if dict_key_trace[-1] != 'sys' and dict_key_trace[-1] != 'files':
                            test_dict = test_dict[dict_key_trace[-1]]
                            dict_key_trace.pop(-1)
                        else:
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
        generate_db_processing(mod_found)

        # Benchmarks here, uncomment to check
        # start_time = datetime.datetime.now()
        # print("Time started for DB saving: " + str(start_time))
        # generate_file_DB_for_mod(mod_found, mod_found, game_ID=gameID, mod_title=os.path.basename(mod_found))
        # end_time = datetime.datetime.now()
        # print("Time ended: " + str(end_time))
        # print("Time spent saving DB: " + str(end_time - start_time) + "\n")

    # Get ORIGINAL ISO db first
    original_iso_db = os.path.join(Path(game_mod_dir), Path(ORIGINAL_ISO_DIR.format(gameID)))

    with open(os.path.join(original_iso_db, DB_JSON), "r") as file:
        iso_file_dict = json.load(file)

    # # Save the ISO first, then save all mods in order on top
    # # Write dict to gameID_MOD folder
    mod_iso_dir = os.path.join(Path(game_mod_dir), Path(MOD_ISO_DIR.format(gameID)))

    # ATTEMPT #3: The directory cannonball run.
    # Goal: walk paths, use directories as keys, trace through until we find files and write.
    # main_iso_dict = master list of files. DON'T TOUCH THIS. This gets updated with our dict_search_ptr iterating through everything in the directories.
    main_iso_dict = iso_file_dict

    # If this is enabled, ignore warnings in files that don't normally exist in the filesystem.
    check_ignore_toggle = int(get_config_option(SETTINGS_INI,
                                            "config",
                                            "AppSettings",
                                            "ignoreOriginalFileWarnings"))

    for mod_path in active_mod_found:
        path_to_mod_root = mod_path
        mod_title = os.path.basename(path_to_mod_root)
        dict_search_ptr = None
        skip_added_files_check = False
        for dirpath, dirnames, filenames in os.walk(path_to_mod_root, topdown=True):
            curr_dir_basename = os.path.basename(dirpath)  # One level up from dirnames being tested

            # Try key search w/ pointer here for top dir
            try:
                if not dict_search_ptr:
                    # Set up our search ptr here
                    dict_search_ptr = main_iso_dict[curr_dir_basename]
                else:
                    # Otherwise, move down directories
                    dict_search_ptr = dict_search_ptr[curr_dir_basename]
            except:
                # if the above doesn't work, it's for the following reasons:
                # 1. It's the base directory
                if curr_dir_basename == os.path.basename(path_to_mod_root):
                    continue
                # if the above doesn't work, we ended moving down directories, so set up the next based on where we enter from with os.walk

                # Set us back to the top, so we can now go back down and check our paths
                dict_search_ptr = main_iso_dict
                try:
                    # This assumes we go back to the top directory. This is faster for single dir games.
                    dict_search_ptr = dict_search_ptr[curr_dir_basename]
                except:
                    # If we're not at the top dir, then we have to do the whole searching shenanigans
                    # Here, we want to get the diff between the current mod dirpath and the root of the mod
                    # Keypaths contain the valid paths to where we are now, so we want to loop these until we get down there
                    key_paths = list(Path(dirpath.replace(path_to_mod_root,'')).parts)
                    key_paths.pop(0) # Remove the first slashes here (CHECK LINUX LATER)

                    # Use dirpath and Pathlib to find everything from sys/files up until our curr_dir_basename
                    while len(key_paths) > 0:
                        dict_search_ptr = dict_search_ptr[key_paths.pop(0)]
                pass

            def handle_file_db_writes():
                nonlocal filenames
                nonlocal dict_search_ptr
                nonlocal skip_added_files_check
                nonlocal check_ignore_toggle
                nonlocal game_mod_dir
                nonlocal gameID
                nonlocal curr_dir_basename
                for filename in filenames:
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
                    # there might be some caps problems here, so fix that for the key, otherwise dupe keys can happen.
                    try:
                        # This is our dummy check. If this fails, then we except. This verifies the file/folder name exists.
                        dict_search_ptr[filename]
                        # If it does work, the above does nothing, update dict normally
                        dict_search_ptr.update({filename: [fileLoc, fileType, fileHash256]})
                    except KeyError as e:
                        # Add error checking for new files.
                        is_corrected = False
                        # For now, the big error is with file extensions, as case matters for those.
                        # This loop is goofy, but we're doing it because I am a tired man.

                        # THIS LIST COMPREHENSION DOES NOT COVER FOR DICTS BEING IN THE LIST, try below:
                        # https://stackoverflow.com/questions/1724693/find-a-file-in-python
                        # all_original_file_names = [os.path.basename(item[0]) for item in list(dict_search_ptr.values())]
                        all_original_file_names = os.listdir(Path(game_mod_dir) / Path(ORIGINAL_ISO_DIR.format(gameID)) / Path(curr_dir_basename))
                        for item in all_original_file_names:
                            # If the names match (ignoring case), fix the title and the extension to match the original's
                            if filename.casefold() == item.casefold():
                                # print("Normalized extension for: " + filename + "\nInto: " + item)
                                dict_search_ptr.update({item: [fileLoc, os.path.splitext(item)[1], fileHash256]})
                                is_corrected = True
                                break

                        if is_corrected:
                            continue

                        # If either toggle is on, ignore for the rest of the mod pack or for all mod packs with the ignore_toggle
                        if skip_added_files_check or check_ignore_toggle:
                            dict_search_ptr.update({filename: [fileLoc, fileType, fileHash256]})
                            continue

                        # If we found a file that doesn't normally exist, warn a brother.
                        warn_text = "The file named:\n" + str(filename) + ("\nFrom the mod:\n" + mod_title
                                                                           + "\n\nIs either unexpected or considered an "
                                                                             "original file by the original game's file system.\n"
                                                                          "Press OK to accept all files like this in this specific mod, "
                                                                          "or press Cancel to ignore this file and"
                                                                             " to ask this again for each file in this specific mod.\n\n"
                                                                             "Hint: To disable this warning entirely when saving mods next time, "
                                                                             "enable: \"Disable file warnings when saving mods\" in the settings tab.")
                        dialog = WarningWindow(title="Unexpected file found!", warning_text=warn_text)
                        if dialog.exec():
                            # If they press ok, update the dict with the file and skip the rest.
                            dict_search_ptr.update({filename: [fileLoc, fileType, fileHash256]})
                            skip_added_files_check = True
                        else:
                            # If cancelled, don't add file.
                            # In the future, add another button to allow accepting the file but querying again.
                            pass
                        pass
                    pass

            if curr_dir_basename not in path_to_mod_root:
                # Handle files first, then directories
                handle_file_db_writes()
            pass

    # Toggle to write this file or not, since it isn't necessary. But it is helpful for debugging different build outputs.
    write_final_DB = int(get_config_option(SETTINGS_INI,
                                           "config",
                                           "AppSettings",
                                           "createDBForFinalOutput"))
    if write_final_DB:
        with open(os.path.join(mod_iso_dir, Path(DB_JSON)), "w") as file:
            json.dump(main_iso_dict, file, indent=4)  # indent for pretty-printing

    return mod_iso_dir, main_iso_dict


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
            
    # except IsADirectoryError:
    except FileExistsError:
        print("Mod already exists!\n")
        raise FileExistsError
    except FileNotFoundError:
        print("Path is incorrect!\n")
        raise FileNotFoundError
    pass