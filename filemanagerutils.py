import sys
import os
import configparser
from pathlib import Path
import datetime

from constants import MODINFO_INI


def generate_settings_ini(settings_ini):
    # Learned about configparser here, so I'm using it since I can append easily:
    # https://stackoverflow.com/questions/8884188/how-to-read-and-write-ini-file-with-python3
    config_data = configparser.ConfigParser()

    if sys.platform == "linux":
        config_data['LauncherLoader'] = {
            "ISODir": "",
            "PluginsDir": "",
            "ModsDir": "",
            "DolphinDir": "Do Not Set This",
            "SaveAndPlayBehavior": "0"
        }
    else:
        config_data['LauncherLoader'] = {
            "ISODir": "",
            "PluginsDir": "",
            "ModsDir": "",
            "DolphinDir": "",
            "SaveAndPlayBehavior": "0"
        }

    config_data['AppSettings'] = {
        "autoUpdateCheckerLauncher": "1",
        "autoUpdateCheckerMods": "1",
        "createDBForFinalOutput": "0",
        "keepLauncherOpenAfterGameStart": "1",
        "Language": "English",
        "Theme": "Basic"
    }

    # Any games added to the mods section is recorded here:
    # GameID: GameTitle
    config_data['GameList'] = {}

    with open(os.path.join(settings_ini), 'w') as f:
        config_data.write(f)
    pass


# USE THIS WHEN ADDING A NEW GAME
def generate_modsDB_ini(modsDB_ini, force_overwrite=False):
    # config_dir = os.path.join(Path(cwdPath), "config")
    # THIS NEEDS TO BE GENERATED PER GAME. MOVE TO A LATER FUNCTION.
    # modsDB_ini = os.path.join(config_dir, "modsDB.ini")

    # Check if modsDB.ini exists
    # Generate that in settings directory if it does not exist
    if os.path.isfile(modsDB_ini) and not force_overwrite:
        print("modsDB.ini already generated.\n")
        return

    if not force_overwrite:
        print("No modsDB.ini found. Generating new file in generated config folder.")

    config_data = configparser.ConfigParser()

    '''
    How adding active/favorite mods work:
    
    Whenever a mod is checked ON, that is active.
    Append ActiveModX to this section (X being the active mod number)
    Tally these at the end to get total.
    
    Whenever a mod is starred, that is a favorite.
    Append FavoriteModX to this section (X being the favorite mod number)
    Tally these at the end to get total.
    '''
    config_data['Main'] = {
        "ManifestVersion": "",
        "ReverseLoadOrder": "",
        "ActiveModCount": "0",
        "FavoriteMod0": "",
        "FavoriteModCount": "0"
    }

    '''
    How adding mods to the mods list works:
    
    Each mod has a hash. The first field is the hash.
    The second field is the directory location of the mod/mod.ini file.
    Mod ini file contains data from gamebanana and more:
        [Desc]
        Author=""
        Title=""
        Version=1.1
        Description=""
        Date=""
        AuthorURL=""
        
        [Main]
        UpdateServer=""
        SaveFile=""
        ID=""
        IncludeDir0="."
        IncludeDirCount=1
        DependsCount=0
        DLLFile=""
        CodeFile=""
        ConfigSchemaFile=""
    
    Leave the initial list empty until a mod is appended.
    '''
    config_data['Mods'] = {}
    config_data['Codes'] = {}

    with open(Path(modsDB_ini), 'w') as f:
        config_data.write(f)

    print("modsDB.ini Generated!")
    return

# Use this to generate info when creating a mod
def generate_modInfo_ini_file(new_mod_data, path_to_mod_folder):
    # We create a file to hold the mod title, author, and other details to display in our window
    config_data = configparser.ConfigParser()

    # For now, there's only a few fields to generate here
    # Date is auto generated based on current time
    config_data['Desc'] = {
        "Author": new_mod_data["Author"],
        "Title": new_mod_data["Mod Title"],
        "Version": new_mod_data["Version"],
        "Description": new_mod_data["Description"],
        "Date": str(datetime.datetime.now())
    }

    mod_ini = os.path.join(Path(path_to_mod_folder), Path(MODINFO_INI))

    with open(mod_ini, 'w') as f:
        config_data.write(f)

    print(MODINFO_INI + " Generated!")
    pass

def generate_config_ini_files(cwdPath):
    # generate ini's here

    # Get config path, settings and modsDB
    config_dir = os.path.join(Path(cwdPath), "config")
    settings_ini = os.path.join(config_dir, "settings.ini")

    # # THIS NEEDS TO BE GENERATED PER GAME. MOVE TO A LATER FUNCTION.
    # modsDB_ini = os.path.join(config_dir, "modsDB.ini")

    # Just so users do not mess this up, generate the directory if it does not already exist
    os.makedirs(config_dir,
                exist_ok=True)

    # Check if settings.ini exists
    # Generate that in settings directory if it does not exist
    if not os.path.isfile(settings_ini):
        print("No settings.ini found. Generating new file in generated config folder.")
        generate_settings_ini(settings_ini)
        print("Settings.ini generated.\n")


    # # Check if modsDB.ini exists
    # # Generate that in settings directory if it does not exist
    # if not os.path.isfile(modsDB_ini):
    #     print("No modsDB.ini found. Generating new file in generated config folder.")
    #     generate_modsDB_ini(modsDB_ini)
    #     print("modsDB.ini generated.\n")

    return settings_ini

def get_config_ini_files(config_name, path_to_config):
    cwdPath = path_to_config
    path_to_config_file = os.path.join(cwdPath, config_name)
    return path_to_config_file

def get_config_option(config_name, path_to_config, section_to_check, option_to_check=None, return_keys=None, return_values=None):
    config_data = configparser.ConfigParser()
    path_to_config = get_config_ini_files(config_name, path_to_config)
    config_data.read(path_to_config)

    # If no option is sent, get all keys in the given section
    if option_to_check is None:

        # If both requested, return both in a dict
        if return_keys and return_values:
            return dict(config_data.items(section_to_check))

        # Otherwise, send a list back of one type or the other
        return_list = []
        for key, values in config_data.items(section_to_check):
            if return_keys: return_list.append(key)
            if return_values: return_list.append(values)

        return return_list

    return config_data.get(section_to_check, option_to_check)

def set_config_option(config_name, path_to_config, section_to_write, option_to_write, new_value="", clear_section=False, clear_option=False):
    config_data = configparser.ConfigParser()
    path_to_config = get_config_ini_files(config_name, path_to_config)
    config_data.read(path_to_config)

    # If we need to clear the section first, do that here and write back to the file
    if clear_section:
        config_data[section_to_write].clear()
        with open(path_to_config, 'w') as f:
            config_data.write(f)
        return

    if clear_option:
        config_data.remove_option(section_to_write, option_to_write)
        with open(path_to_config, 'w') as f:
            config_data.write(f)
        return

    # Otherwise, set this new key-value
    config_data.set(section_to_write, option_to_write, new_value)

    with open(path_to_config, 'w') as f:
        config_data.write(f)
    pass
