from pathlib import Path
from sys import platform
UI_FOLDER_PATH = Path("windowUIFiles")

# Some programmers hate magic strings. While this seemed weird to me at first to write this as a constant,
# I think it'll just be easier to have this available as an autofill tbh.
# TODO: Make linux/mac versions of these. .EXE is a mainly windows thing (as I am a windows user rn, sorry for my sins).

if platform == "win32": #Windows
    DOLPHIN_EXE = "dolphin.exe"
    DOLPHIN_TOOL = "dolphintool.exe"
elif platform == "darwin": #MacOS
    DOLPHIN_EXE = "Dolphin.app/Contents/MacOS/Dolphin"
    DOLPHIN_TOOL = "dolphin-tool"
elif platform == "linux": #Linux
    DOLPHIN_EXE = "" #uhhh idk how to handle the flatpak values yet.
    DOLPHIN_TOOL = ""
SETTINGS_INI = "settings.ini"
MODSDB_INI = "modsDB.ini"
DB_INI = "db.ini"

ORIGINAL_ISO_DIR = "{}_ISO"
MOD_ISO_DIR = "{}_MOD"
MOD_PACK_DIR = "{}_mods"