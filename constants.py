# Application constants

# Tile and map dimensions
TILE_SIZE = 24
DEFAULT_MAP_WIDTH = 128
DEFAULT_MAP_HEIGHT = 64
MAP_WIDTH = 128
MAP_HEIGHT = 64

# Animation timing (ms)
ANIMATION_INTERVAL = 250

# Application dimensions
APP_WIDTH = 1200
APP_HEIGHT = 800

# Navigation settings
DEFAULT_NAV_SPEED = 1

# UI settings
PALETTE_COLS = 16
GRID_COLOR = (200, 200, 200, 100)
SELECTION_COLOR = "red"

# Unit overlay colors
PLAYER_COLOR = "blue"
ROBOT_COLOR = "red"
DOOR_COLOR = "green"
ITEM_COLOR = "magenta"

# Map binary file offsets
UNIT_TYPES_OFFSET  = 0x0000
UNIT_X_OFFSET      = 0x0040
UNIT_Y_OFFSET      = 0x0080
UNIT_A_OFFSET      = 0x00C0
UNIT_B_OFFSET      = 0x0100
UNIT_C_OFFSET      = 0x0140
UNIT_D_OFFSET      = 0x0180
UNIT_H_OFFSET = 0x01C0
MAP_DATA_OFFSET = 770  # PET:770, Amiga: 768, X16: 770-128-128