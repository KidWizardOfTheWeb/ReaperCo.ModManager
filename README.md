<h1>
Reaper Co. Mod Manager - R.C.M.M.
</h1>

A Mod Manager for Dolphin Emulator Games, inspired by [HedgeModManager](https://github.com/thesupersonic16/HedgeModManager).

## Installation instructions
**Prerequisites** (you must have these to run the program until a binary is created):
> - [Python 3.14](https://www.python.org/downloads/) or above.
> - The modules included in [requirements.txt](https://github.com/KidWizardOfTheWeb/ReaperCo.ModManager/blob/master/requirements.txt).
> - A build of [Dolphin](https://dolphin-emu.org/), the GameCube/Wii emulator. BUILD MUST INCLUDE `dolphintool.exe`.

1. Clone the repository into any folder of choice using git.
```
git clone https://github.com/KidWizardOfTheWeb/ReaperCo.ModManager
```

2. Create a folder (preferably in your Dolphin build directory). This will house all of your extracted games and mods.

_Add image here._

3. Using your command line interface of choice, run the following commands to get to the installation and set up the program:
```bash
cd "path\to\your\cloned\repository"
pip install -r requirements.txt
```

**NOTE**:
`path\to\your\cloned\repository` is NOT literal. Get the actual path using your file explorer and replace that in the command.

Then in the same directory, run the program with the following command.
```python
py main.py
```

4. In the settings tab, use the triple dot buttons to set your directories to the following:
> - **Mods Directory** - Set to the folder created in step 2.
> - **Dolphin Directory** - Set to the root of your Dolphin build (the folder where `dolphin.exe`/`dolphintool.exe` exists).
> - **Textures Directory** - WIP, non-functional for now. You can set this to your `User/Load/Textures` path in Dolphin for now if you want.

_Add image here._

5. Now, set up some games!

## How do I add games?
Unlike Hedge Mod Manager, `R.C.M.M` does not scan all directories for available games, as you may not want hundreds of games to be extracted and/or have mods at once.

Instead, you add games manually using the interface.

1. At the bottom of the interface, use the drop-down to add a new game by selecting the option named `Add new game here`.

_Add image here._

2. Select a GameCube ISO from your available Dolphin compatible games. GameCube ISOs are currently the only acceptable format. 

_Add image here._

More format support for Wii, other compression formats TBA.

3. `R.C.M.M` will then extract the contents of your game to the Mods Directory and set up the required folders, placed under a folder with the corresponding game ID.
To find out what your game ID is, check the properties of the game in Dolphin itself with right click -> properties -> Info -> Game Details -> Game ID.

**NOTE**: This process does NOT overwrite your original game copy. It simply creates a copy of the game that will be used as a base to add mods on top of.

4. When you look at `R.C.M.M` after this process finishes, the dropdown at the bottom will now read the title of your added game. You can now go back to this game's mod list by clicking it in the dropdown in the future.

_Add image here._

5. Now you can add mods!

## How do I add mods?
For now, adding compatible mods is a manual process. However, adding mods are as easy as dragging and dropping files!

1. In your Mods Directory -> folder corresponding with the game you want to add mods to (remember, check game ID), there's a folder called `gameID_Mods` (gameID = the actual ID of the game). 

_Add image here._

2. Adding folders in this directory will create a mod for your game. Name the folder whatever you want your mod to be named.

_Add image here._

3. To actually add files to your mod, check what kind of files you've modified so far.

If you've modified files like `main.dol` to add new code to a game or modified any files that usually would go in the `sys` folder, add a folder inside your newly created mod folder named `sys`. Place your new `main.dol` in this folder.
This is mainly for games with mods that add new functionality.

If you've modified game files that you usually would place in the `files` folder (music files like ADXs, model files, etc.), add a folder inside your newly created mod folder named `files`. Place your files that would usually replace game files in here.
This is for games that may change things such as models, animations, music, etc.

_Add image here._

4. Once you've finished adding files, re-open or press `Refresh List` in `R.C.M.M`. You should now see your new mods in the list on the mods page!

## Toggling mods
Turning mods on/off is as simple as choosing your game, clicking the checkboxes, and pressing save.

1. Select your added game from the dropdown list.

_Add image here._

2. Check/uncheck the mods you want to use for your modded game. 

_Add image here._

3. Press the save button. This will open up a menu that will allow you to reorder your mods in terms of priority with drag/drop.

**You can skip this step by pressing "OK" if none of your mods have conflicting files, as this is for power users/mod priority fixes.** 

If you know your mods have conflicting files already, you can reorder the mods here.
The list goes in terms of least prioritized -> most prioritized from top to bottom. For mods that you are ok with overwriting, place them towards the top. Mods are written to your game copy from top -> bottom of this list.

Mod conflict recognition coming in a later update.

4. Once saved, you can now start your game!

Your modded game copy is located in the `gameID_MOD` folder in your `gameID` directory.

Options to start the game:
> 1. Press "Save and Play".
> 2. Drag the `main.dol` file in the `gameID_MOD` folder on top of Dolphin.
> 3. Set a path to the `sys` directory in the `gameID_MOD` folder in your Dolphin path configuration to have it show up in your launcher.


## Acknowledgements & Credits
`R.C.M.M` is directly inspired by the work of [HedgeModManager](https://github.com/thesupersonic16/HedgeModManager) and [SA-Mod-Manager](https://github.com/X-Hax/SA-Mod-Manager).

Originally designed for the purpose of unifying support for Sonic Riders mods, I hope this tool can be used to smooth out the process of testing, developing, and playing mods for GameCube and Wii games.

More features to be added soon, stay tuned.

PRs very much welcome! Especially for support for other platforms that may not be covered here.