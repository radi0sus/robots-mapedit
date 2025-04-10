# Tile Map Editor

A PyQt5-based editor for creating and editing tile-based maps, with support for animated tiles and various unit types. This application is designed for editing maps compatible with game engines like PETSCII Robots.

<img src='gfx/Screenshot1.png' width='1024' alt='Screenshot' align='center'>
<img src='gfx/Screenshot2.png' width='1024' alt='Screenshot' align='center'>
<img src='gfx/Screenshot3.png' width='1024' alt='Screenshot' align='center'>

## Project Structure

The project is organized into several Python modules, each with specific responsibilities:

- **main.py**: The entry point that runs the application
- **tilemap_editor.py**: Main editor class that coordinates all components
- **map_data.py**: Classes for map data management and serialization
- **tile_manager.py**: Handles tile loading and organization
- **animation.py**: Manages tile animation states and timing
- **ui_components.py**: UI elements specific to this application
- **unit_editor.py**: Add or delete units, change properties
- **constants.py**: Shared constants and settings

## Features 

- Edit maps 
- Support for animated tiles (water, flags, etc.)
- Unit placement (player, robots, items)
- Binary map file format loading and saving
- Undo/redo functionality (for tiles, not for units)
- Keyboard shortcuts for navigation 

## To do list
- enhance UI

## Requirements

- Python 3.6+
- PyQt5

## Installation

1. Ensure you have Python (ver 3.x) installed
2. Create a virtual environment (`python3 -m venv...`)
3. In case of `venv`: `source /path-to-program/bin/activate`
4. Install PyQt5: `pip3 install PyQt5`
5. Clone or download this repository
6. Make a folder `tiles` in the same directory
7. Download tiles (`.png`) from: [https://github.com/zeropolis79/PETSCIIRobots-Amiga/tree/main/Amiga](https://github.com/zeropolis79/PETSCIIRobots-Amiga/tree/main/Amiga)
8. Copy the tiles in the folder `tiles`
9. Download levels from: [https://github.com/zeropolis79/PETSCIIRobots-Pet/tree/main](https://github.com/zeropolis79/PETSCIIRobots-Pet/tree/main) or from other level locations (see *Map Files*).
10. Rename `level-a` to `level-a.bin` and so on
11. In case of `venv`: `source /path-to-program/bin/activate`
12. Run the application: `python3 main.py`

## Usage

### Basic Controls

- **Left-click**: Place the selected tile
- **Right-click**: Erase tile (set to empty)
- **Arrow keys**: Navigate around the map
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Edit Units**: The key for adding or deleting units and change their properties

### Interface Elements

- **Top-left panel**: Map view with grid
- **Top-right panel**: Tile palette for selection
- **Bottom-right panel**: Controls for loading/saving and options
- **Edit Units**: The key for adding or deleting units and change their properties

### Show units

[Unit codes and parameters](https://www.the8bitguy.com/pr-mapedit/)

- P: Player (blue)
- R: Robots (red)
- D: Doors (green)
- I: Items (magenta)

Example `R17-2`   : Robot with Unit ID 17, Type 2
Example `D38-10-3`: Door with Unit ID 17, Type 10, needs Key 3

### Edit units

- Blue Frame: Player
- Red Frame: Robots
- Green Frame: Doors, Rafts, ...
- Magenta Frames: Items
- Grey Frames: Unknown Type

- You should read the [Map Editor Intstructions](https://www.the8bitguy.com/pr-mapedit/). 
- If a unit slot is full, no other unit of the same type can be added. For example, if there are already 16 items, item 17 cannot be added.
- If there are empty slots (not used Unit IDs) in unit types, you can add a unit of the same type. For example, a raft in the "doors" type. Empty slots can be identified by *Unknown (0)....*
- It is also possible to delete a unit to free up a Unit ID.
- To add a unit at a specific position:
  1. Note a free Unit ID (check for *Unknown (0)...*).
  2. Close the Unit Editor.
  3. Right-click on the map.
  4. Add Unit.
  5. Insert the Unit ID.
  6. Change the type and properties.
  7. Save the changes
  8. Save the map.
- To change properties of a unit:
  1. Select the unit in the Edit Units window
  2. Change the type (if you like). But it must be of the same type, so replacing a robot with a robot is possible.
  3. Change the parameters. More ammo, more health or less...
  4. Save the changes
  5. Save the map.
     
### Map Files

- The application loads maps (levels) in a binary format compatible with PETSCII Robots.
- Check the `MAP_DATA_OFFSET` in `constants.py`, as it can differ across versions (I found 770 and 514 for two versions of the X16 robots). In case of a mismatch, units—such as hidden objects or robots—may appear shifted. However, the issue can be even more subtle.
- Check `MAP_DATA_OFFSET` in `constants.py`. It can be different for differnt versions.
- Warning! Saving the level may destroy it. Make a backup copy of the level before editing.

## Directory Structure

```
tile-map-editor/
├── main.py               # Application entry point
├── tilemap_editor.py     # Main editor interface
├── map_data.py           # Map data handling
├── tile_manager.py       # Tileset management
├── animation.py          # Animation controller
├── ui_components.py      # UI widgets
├── constants.py          # Shared constants
├── unit_editor.py        # Unit editor
└── tiles/                # Directory for tile images
    └── animtiles.png     # Animated tile images
```


