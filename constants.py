from pathlib import Path
UI_FOLDER_PATH = Path("windowUIFiles")

# Some programmers hate magic strings. While this seemed weird to me at first to write this as a constant,
# I think it'll just be easier to have this available as an autofill tbh.
# TODO: Make linux/mac versions of these. .EXE is a mainly windows thing (as I am a windows user rn, sorry for my sins).
DOLPHIN_EXE = "dolphin.exe"
DOLPHIN_TOOL = "dolphintool.exe"
SETTINGS_INI = "settings.ini"
MODSDB_INI = "modsDB.ini"
DB_INI = "db.ini"

ORIGINAL_ISO_DIR = "{}_ISO"
MOD_ISO_DIR = "{}_MOD"
MOD_PACK_DIR = "{}_mods"