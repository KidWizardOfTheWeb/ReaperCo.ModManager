from pathlib import Path
from sys import platform
UI_FOLDER_PATH = Path("windowUIFiles")

# Some programmers hate magic strings. While this seemed weird to me at first to write this as a constant,
# I think it'll just be easier to have this available as an autofill tbh.

if platform == "win32": #Windows
    DOLPHIN_EXE = "dolphin.exe"
    DOLPHIN_TOOL = "dolphintool.exe"
elif platform == "darwin": #MacOS
    DOLPHIN_EXE = "Dolphin.app/Contents/MacOS/Dolphin"
    DOLPHIN_TOOL = "dolphin-tool"
elif platform == "linux": #Linux
    DOLPHIN_EXE = "org.DolphinEmu.dolphin-emu"
    DOLPHIN_TOOL = "--command=dolphin-tool"

SETTINGS_INI = "settings.ini"
MODSDB_INI = "modsDB.ini"
MODINFO_INI = "modinfo.ini"
DB_INI = "db.ini"
DB_JSON = "db.json"

ORIGINAL_ISO_DIR = "{}_ISO"
MOD_ISO_DIR = "{}_MOD"
MOD_PACK_DIR = "{}_Mods"

# Support for extra script plugins coming later
PLUGINS_DIR = "{}_Plugins"