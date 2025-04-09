# Tile Map Editor

A PyQt5-based editor for creating and editing tile-based maps, with support for animated tiles and various unit types. This application is designed for editing maps compatible with game engines like PETSCII Robots.

## Project Structure

The project is organized into several Python modules, each with specific responsibilities:

- **main.py**: The entry point that runs the application
- **tilemap_editor.py**: Main editor class that coordinates all components
- **map_data.py**: Classes for map data management and serialization
- **tile_manager.py**: Handles tile loading and organization
- **animation.py**: Manages tile animation states and timing
- **ui_components.py**: UI elements specific to this application
- **constants.py**: Shared constants and settings

## Features (not yet implemented)

- (Edit maps with customizable tile sets)
- Support for animated tiles (water, flags, etc.)
- (Unit placement and visualization (player, robots, items))
- Binary map file format loading (and saving)
- Undo/redo functionality
- Keyboard shortcuts for navigation and editing

## To do list
- add more level editing functions, [see](https://www.the8bitguy.com/pr-mapedit/)
- enhance UI for other map editing, features [see](https://www.the8bitguy.com/pr-mapedit/)
- save levels (maps) 

## Requirements

- Python 3.6+
- PyQt5

## Installation

1. Ensure you have Python (ver 3.x) installed
2. Create a virtual environment (`python3 -m venv...`)
3. Install PyQt5: `pip3 install PyQt5`
4. Clone or download this repository
5. Make a folder `tiles` in the same directory
6. Download tiles (`.png`) from: [https://github.com/zeropolis79/PETSCIIRobots-Amiga/tree/main/Amiga](https://github.com/zeropolis79/PETSCIIRobots-Amiga/tree/main/Amiga)
7. Copy the tiles in the folder `tiles`
8. Download levels from: [https://github.com/zeropolis79/PETSCIIRobots-Pet/tree/main](https://github.com/zeropolis79/PETSCIIRobots-Pet/tree/main)
9. Rename `level-a` to `level-a.bin` and so on
10. In case of `venv`: `source /path-to-pgrogram/bin/activate`
11. Run the application: `python3 main.py`

## Usage

### Basic Controls

- **Left-click**: Place the selected tile
- **Right-click**: Erase tile (set to empty)
- **Arrow keys**: Navigate around the map
- (**Number keys (0-9)**: Quick-select tiles)
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo

### Interface Elements

- **Top-left panel**: Map view with grid
- **Top-right panel**: Tile palette for selection
- **Bottom-right panel**: Controls for loading/saving and options

### Show units

[Unit codes and parameters](https://www.the8bitguy.com/pr-mapedit/)

- P: Player
- R: Robot 
- D: Door (parameter C)
- I: Item (key: parameter A, units: parameter A)
 
### Map Files

- The application loads maps (levels) in a binary format compatible with PETSCII Robots. 
- Rename the level to `level.bin`. 
- Only the original PET levels work out of the box. Levels for other systems could different offsets.
- Warning! Saving a level, will destroy it!

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
└── tiles/                # Directory for tile images
    └── animtiles.png     # Animated tile images
```


