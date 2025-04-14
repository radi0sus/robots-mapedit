# Application constants

# Tile and map dimensions
TILE_SIZE = 24
DEFAULT_MAP_WIDTH = 128
DEFAULT_MAP_HEIGHT = 64
#MAP_WIDTH = 128
#MAP_HEIGHT = 64

# Animation timing (ms)
ANIMATION_INTERVAL = 250

# Application dimensions
APP_WIDTH = 1200
APP_HEIGHT = 800

# Navigation settings
DEFAULT_NAV_SPEED = 1

# Animated tiles filename
ANIM_TILES_NAME = "animtiles.png"

# UI settings
PALETTE_COLS = 15
GRID_COLOR = (200, 200, 200, 100)
SELECTION_COLOR = "red"
TILE_FONT_COLOR = (0, 255, 0, 255)
SHOW_TILE_NUMBER = True

# Unit overlay colors
PLAYER_COLOR = "blue"
ROBOT_COLOR = "red"
DOOR_COLOR = "green"
ITEM_COLOR = "magenta"

# Map binary file offsets
# There seem to be a two byte header before the player unit
#BASE_ADDRESS = 0x0002
#BASE_ADDRESS = 0x0000

UNIT_TYPES_OFFSET  = 0x0000 #+ BASE_ADDRESS
UNIT_X_OFFSET      = 0x0040 #+ BASE_ADDRESS
UNIT_Y_OFFSET      = 0x0080 #+ BASE_ADDRESS
UNIT_A_OFFSET      = 0x00C0 #+ BASE_ADDRESS
UNIT_B_OFFSET      = 0x0100 #+ BASE_ADDRESS
UNIT_C_OFFSET      = 0x0140 #+ BASE_ADDRESS
UNIT_D_OFFSET      = 0x0180 #+ BASE_ADDRESS
UNIT_H_OFFSET      = 0x01C0 #+ BASE_ADDRESS
# UNIT_BLOCK_SIZE    = 0x40 # if MAP_OFFSET is 768 (MS-DOS, Amiga)
UNIT_BLOCK_SIZE    = 0x42   # if MAP_OFFSET is 770 (PET, C64, C128) or 770 -128 -128 (X16)
# MAP_DATA_OFFSET = 770 
# PET, C64x:770, 
# Amiga, MS-DOS: 768 
# X16-Robots (from 8-Bit-Guy Homepage): 770 - 128 - 128
# X16-Robots (from GitHub): 770 (?)
# WARNING MAP_DATA_OFFSET is crucial 
# Check if the item location match
MAP_DATA_OFFSET = 770 #- 128 - 128
MAP_DATA_OFFSET_LOAD = MAP_DATA_OFFSET
MAP_DATA_OFFSET_SAVE = MAP_DATA_OFFSET
# MAP_DATA_OFFSET = 0x0200
# PLAYER_UNIT_ID = 0 # if MAP_OFFSET is 768 (MS-DOS and Amiga)
PLAYER_UNIT_ID = 2   # if MAP_OFFSET is 770 (PET, C64, C128) or 770 -128 - 128 (X16)
