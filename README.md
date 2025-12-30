<h1>
Reaper Co. Mod Manager - R.C.M.M.
</h1>

A Mod Manager for Dolphin Emulator Games, inspired by [HedgeModManager](https://github.com/thesupersonic16/HedgeModManager).

## Installation Guide

1. Download the latest release from the releases folder.
2. Create a folder (preferably in your Dolphin build directory). This will house all of your extracted games and mods.

<img width="666" height="240" alt="image" src="https://github.com/user-attachments/assets/aaf9b13d-07ba-4a14-b2e5-04d4fd8ae3f0" />

4. Open your downloaded release and launch the included executable.
5. In the settings tab, use the triple dot buttons to set your directories to the following:
- **Mods Directory** - Set to the folder created in step 2.
- **Dolphin Directory** - Set to the root of your Dolphin build (the folder where `dolphin.exe`/`dolphintool.exe` exists).
- **Modules Directory** - WIP, non-functional for now. In the future, we will support external scripts being connected to RCMM for any purpose.

<img width="785" height="229" alt="image" src="https://github.com/user-attachments/assets/54aaf583-f797-4407-b3a3-2fae3887ffe8" />

Now, set up some games!

## How do I add games?
Unlike Hedge Mod Manager, `R.C.M.M` does not scan all directories for available games, as you may not want hundreds of games to be extracted and/or have mods at once.

Instead, you add games manually using the interface.

1. At the bottom of the interface, use the drop-down to add a new game by selecting the option named `Add new game here`.

<img width="795" height="109" alt="image" src="https://github.com/user-attachments/assets/7ce2f162-721b-4a5a-a01a-5b68cc9e3a56" />
<br></br>

2. Select a GameCube ISO from your available Dolphin compatible games. GameCube ISOs are currently the only acceptable format. 

3. `R.C.M.M` will then extract the contents of your game to the Mods Directory and set up the required folders, placed under a folder with the corresponding game ID.
To find out what your game ID is, check the properties of the game in Dolphin itself with `right click on game -> Properties -> Info -> Game Details -> Game ID`.

**NOTE**: This process does NOT overwrite your original game copy. It simply creates a copy of the game that will be used as a base to add mods on top of.

4. When you look at `R.C.M.M` after this process finishes, the dropdown at the bottom will now read the title of your added game. You can now go back to this game's mod list by clicking it in the dropdown in the future.

<img width="793" height="826" alt="image" src="https://github.com/user-attachments/assets/782bba2e-43ad-4bdf-b913-89fd27db29f9" />

Now you can add mods!

## How do I add mods?
To add mods, press the `Add Mod` button on the mods tab to spawn this window.

<img width="372" height="233" alt="image" src="https://github.com/user-attachments/assets/670d6579-b501-453a-9cfd-6a4e86cc3a00" />

You can import a mod using `Installing from a zip folder` to import a zip that was created by RCMM. It will be unzipped and automatically added to your mods once a zip is selected.

To create a mod, use `Make a new mod`. **You must enter at least a title for your mod to be created.**

If you've modified files like `main.dol` to add new code to a game or modified any files that usually would go in the `sys` folder, enable `Create sys folder`. Place your new `main.dol` in this folder.
This is mainly for games with mods that add new functionality.

If you've modified game files that you usually would place in the `files` folder (music files like ADXs, model files, etc.), enable `Create files folder`. Place your files that would usually replace game files in here.
This is for games that may change things such as models, animations, music, etc.

Note: Enabling "Open Folder" will immediately spawn a file explorer process of where your mod was created.

<img width="390" height="424" alt="image" src="https://github.com/user-attachments/assets/92c3b390-3aeb-477b-97fe-1d40091d0bf9" />

In your Mods Directory -> folder corresponding with the game you want to add mods to (remember, check game ID), there's a folder called `gameID_Mods` (gameID = the actual ID of the game). 

<img width="709" height="245" alt="image" src="https://github.com/user-attachments/assets/7e09c157-42e3-4493-af03-3e8c83daf6d7" />
<br></br>

2. Adding folders in this directory will create a mod for your game. Name the folder whatever you want your mod to be named.

<img width="804" height="321" alt="image" src="https://github.com/user-attachments/assets/b9fca221-6aa2-4f2b-b19e-7cfea3368b96" />

4. Once you've finished adding files, re-open or press `Refresh List` in the mods tab in `R.C.M.M`. You should now see your new mods in the list on the mods page!

## Toggling mods
Turning mods on/off is as simple as choosing your game, clicking the checkboxes, and pressing save.

1. Select your added game from the dropdown list.

2. Check/uncheck the mods you want to use for your modded game.

The list goes in terms of least prioritized -> most prioritized from top to bottom. For mods that you are ok with overwriting, place them towards the top. Mods are written to your game copy from top -> bottom of this list.

<img width="797" height="374" alt="image" src="https://github.com/user-attachments/assets/9ef5c16f-ef07-411f-90f8-5bf5bd21598a" />

3. Press the save button to save your changes. 

4. Once saved, you can now start your game!

Your modded game copy is located in the `gameID_MOD` folder in your `gameID` directory. **It is highly suggested to set a path to the `.dol` file in the `sys` folder of `gameID_MOD` in Dolphin Emulator in order to play your modified copy with others, or without launching the mod manager**.

<img width="704" height="251" alt="image" src="https://github.com/user-attachments/assets/9673e14b-f3c6-41aa-8e2f-b8daa4c423a1" />
<br></br>

Options to start the game:
1. Press "Save and Play" in `R.C.M.M` to save the current mods and instantly start Dolphin. You can start the game without the main Dolphin window or with it, depending on the settings page option selected here.

<img width="792" height="358" alt="image" src="https://github.com/user-attachments/assets/b04ca941-91f7-46c8-83c0-d9e03c4b79fc" />

2. Drag the `main.dol` file in the `gameID_MOD` folder on top of Dolphin to start the game.
3. Set a path to the `sys` directory in the `gameID_MOD` folder in your Dolphin path configuration to have it show up in your launcher.



## For Developers
### Prerequisites
- [Python 3.14](https://www.python.org/downloads/) or above.
- The modules included in [requirements.txt](https://github.com/KidWizardOfTheWeb/ReaperCo.ModManager/blob/master/requirements.txt).
- A build of [Dolphin](https://dolphin-emu.org/), the GameCube/Wii emulator. BUILD MUST INCLUDE `dolphintool.exe`.

### Development instructions
1. Clone the repository into any folder of choice using git.
```
git clone https://github.com/KidWizardOfTheWeb/ReaperCo.ModManager
```

2. Create a folder (preferably in your Dolphin build directory). This will house all of your extracted games and mods.

<img width="638" height="589" alt="image" src="https://github.com/user-attachments/assets/96b9f066-d60b-4318-86e5-d145404ccc9f" />
<br></br>

3. Using your command line interface of choice, run the following commands to get to the installation and set up the program:
```bash
cd "path\to\your\cloned\repository"
pip install -r requirements.txt
```

Then in the same directory, run the program with the following command:
```python
py main.py
```


## Acknowledgements & Credits
`R.C.M.M` is directly inspired by the work of [HedgeModManager](https://github.com/thesupersonic16/HedgeModManager) and [SA-Mod-Manager](https://github.com/X-Hax/SA-Mod-Manager).

Originally designed for the purpose of unifying support for Sonic Riders mods, I hope this tool can be used to smooth out the process of testing, developing, and playing mods for GameCube and Wii games.

More features to be added soon, stay tuned.

PRs very much welcome! Especially for support for other platforms that may not be covered here.
