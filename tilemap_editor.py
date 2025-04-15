import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog,
    QComboBox, QGridLayout, QVBoxLayout, QScrollArea,
    QShortcut, QCheckBox, QHBoxLayout
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from constants import (
    TILE_SIZE, DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT,
    DEFAULT_NAV_SPEED, ANIMATION_INTERVAL, APP_WIDTH, APP_HEIGHT
)
from map_data import MapData
from tile_manager import TileManager
from animation import AnimationController
from ui_components import TilesetPaletteWidget, MapCanvasWidget

from unit_editor import UnitEditor

class TileMapEditor(QWidget):
    """Main tile map editor application"""
    
    def __init__(self, tileset_dir="tiles", animtiles_path="animtiles.png"):
        super().__init__()
        self.setWindowTitle("Tile Map Editor")
        
        # Initialize core components
        self.map_data = MapData()
        self.tile_manager = TileManager(TILE_SIZE)
        self.tile_manager.tileset_dir = tileset_dir
        
        # Ensure parent is set for callbacks
        #self.palette.parent = self  
        
        # Initialize UI components
        self.init_ui()
        
        # Initialize animation system
        self.animation_controller = AnimationController(
            interval=ANIMATION_INTERVAL,
            callback=self.on_animation_update
        )
        
        # Add tile patterns dictionary
        self.tile_patterns = {
        'block': [(0, 0), (1, 0), (0, 1), (1, 1)],                   # 2x2 block
        'large_block': [(x, y) for x in range(8) for y in range(8)], # 8x8 bblock
        'hline': [(0, 0), (1, 0), (2, 0)],               # Horizontal line of 3 tiles
        'long_hline':[(x, 0) for x in range(12)],        # Horizontal line of 12 tiles
        'vline': [(0, 0), (0, 1), (0, 2)],               # Vertical line of 3 tiles
        'long_vline': [(0, y) for y in range(12)],       # Vertical line of 12 tiles
        'corner': [(0, 0), (1, 0), (0, 1)],              # L-shape corner
        'long_corner': [(0, y) for y in range(8)] + [(x, 0) for x in range(1, 8)],
        'cross': [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]  # Cross pattern
        }
        
        # Special tile patterns with specific tile IDs
        self.special_tile_patterns = {
        'fan': [
            (0, 0, 196),  # x, y, tile_id
            (1, 0, 197),
            (0, 1, 200),
            (1, 1, 201)
            ],
        'horizontal_door': [
            (0, 0, 80),  # x, y, tile_id
            (1, 0, 81),
            (2, 0, 82),
            ],
        'vertical_door': [
            (0, 0, 68),  # x, y, tile_id
            (0, 1, 72),
            (0, 2, 76),
            ],
        'kitchen_corner': [
            (0, 0, 48),  # x, y, tile_id
            (1, 0, 49),
            (2, 0, 50),
            (0, 1, 52),
            (1, 1, 53),
            (2, 1, 54),
            (0, 2, 56),
            (1, 2, 57),
            ],
        'lander': [
            (0, 0, 132),  # x, y, tile_id
            (1, 0, 133),
            (0, 1, 136),
            (1, 1, 137),
            ]
        }
        
        
       
        # Pattern key bindings - now with modifiers
        # Format: (key, modifier): pattern_name
        self.pattern_keys = {
            (Qt.Key_B, Qt.NoModifier):      'block',          # B with no modifier
            (Qt.Key_B, Qt.ShiftModifier):   'large_block',    # Shift + B
            (Qt.Key_H, Qt.NoModifier):      'hline',
            (Qt.Key_H, Qt.ShiftModifier):   'long_hline',
            (Qt.Key_V, Qt.NoModifier):      'vline',
            (Qt.Key_V, Qt.ShiftModifier):   'long_vline',
            (Qt.Key_C, Qt.NoModifier):      'corner',
            (Qt.Key_C, Qt.ShiftModifier):   'long_corner',
            (Qt.Key_X, Qt.NoModifier):      'cross',
            (Qt.Key_F, Qt.NoModifier):      'fan',
            (Qt.Key_D, Qt.NoModifier):      'horizontal_door',
            (Qt.Key_D, Qt.ShiftModifier):   'vertical_door',
            (Qt.Key_K, Qt.NoModifier):      'kitchen_corner',
            (Qt.Key_L, Qt.NoModifier):      'lander',
        }
        
        # Navigation properties
        self.map_window_x = 0
        self.map_window_y = 0
        self.map_window_width = DEFAULT_MAP_WIDTH
        self.map_window_height = DEFAULT_MAP_HEIGHT
        self.nav_speed = DEFAULT_NAV_SPEED
        
        # Initial loading
        self.load_assets()
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Set focus to the canvas
        self.canvas.setFocus()
        
    def open_unit_editor(self):
        """Open the unit editor dialog"""
        editor = UnitEditor(self, self.map_data)
        # switch focus
        #editor.show()
        # unit editor has focus until close 
        editor.exec_()
        #
        # Update the display when the dialog closes
        self.update_map_display()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Map canvas
        self.canvas = MapCanvasWidget(self)
        self.canvas.window_width = DEFAULT_MAP_WIDTH
        self.canvas.window_height = DEFAULT_MAP_HEIGHT
        
        # Wrap the canvas in a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
               
        # Tile palette
        self.palette = TilesetPaletteWidget(parent=self)
        
        # Tileset selector
        self.tileset_combo = QComboBox()
        self.tileset_combo.currentIndexChanged.connect(self.on_tileset_changed)
        
        # Animation checkbox
        self.animate_cb = QCheckBox("Show Animations")
        self.animate_cb.setChecked(True)
        self.animate_cb.stateChanged.connect(self.toggle_animations)
        
        # Unit Overlay
        self.unitov_cb = QCheckBox("Show Units")
        self.unitov_cb.setChecked(True)
        self.unitov_cb.stateChanged.connect(self.toggle_unit_overlay)
        
        # Buttons
        load_button = QPushButton("Choose Tileset Directory")
        load_button.clicked.connect(self.choose_tileset_directory)
                
        load_binary_map_button = QPushButton("Load Binary Map")
        load_binary_map_button.clicked.connect(self.load_binary_map_dialog)
        
        save_binary_button = QPushButton("Save Binary Map")
        save_binary_button.clicked.connect(self.save_binary_map)
        
        # Info display
        self.info_label = QLabel("Cursor: 0,0 Tile: None")
        
        # Layout all controls
        buttons = QVBoxLayout()
        buttons.addWidget(self.tileset_combo)
        buttons.addWidget(load_button)
        buttons.addWidget(load_binary_map_button)
        buttons.addWidget(save_binary_button)
        buttons.addWidget(self.animate_cb)
        buttons.addWidget(self.unitov_cb)
        buttons.addWidget(self.info_label)
        
        # Main layout
        layout = QGridLayout()
        layout.addWidget(self.scroll_area, 0, 0, 2, 1)
        layout.addWidget(self.palette, 0, 1)
        layout.addLayout(buttons, 1, 1)
        
        unit_editor_button = QPushButton("Edit Units")
        unit_editor_button.clicked.connect(self.open_unit_editor)
        buttons.addWidget(unit_editor_button)
        
        self.setLayout(layout)
        
        self.setGeometry(100, 100, APP_WIDTH, APP_HEIGHT)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo)
        self.setFocusPolicy(Qt.StrongFocus)
    
    def load_assets(self):
        """Load tilesets and initialize the editor"""
        # Load tilesets
        tileset_files = self.tile_manager.scan_tileset_directory()
        self.tileset_combo.clear()
        self.tileset_combo.addItems(tileset_files)
        
        # Load animated tileset
        self.tile_manager.load_animated_tileset()
        
        # Load first tileset if available
        if tileset_files:
            self.tile_manager.load_tileset(tileset_files[0])
            self.palette.update_palette(self.tile_manager.tiles)
        
        # Update map display
        self.update_map_display()
    
    def on_tileset_changed(self, index):
        """Handle tileset selection change"""
        if 0 <= index < len(self.tile_manager.tileset_files):
            self.tile_manager.load_tileset(self.tile_manager.tileset_files[index])
            self.palette.update_palette(self.tile_manager.tiles)
            self.update_map_display()
    
    def update_map_display(self):
        """Update the map canvas display"""
        self.canvas.window_x = self.map_window_x
        self.canvas.window_y = self.map_window_y
        self.canvas.window_width = self.map_window_width
        self.canvas.window_height = self.map_window_height
        
        # Update the canvas with current state
        self.canvas.update_canvas(
            self.map_data.data,
            self.tile_manager,
            self.map_data.unit_positions,
            self.animation_controller.get_state(),
            self.animation_controller.is_enabled(),
            self.canvas.show_unit_overlay,
        )
    
    def on_animation_update(self, anim_state):
        """Callback when animation state updates"""
        self.update_map_display()
    
    def toggle_animations(self, state):
        """Enable or disable animations"""
        self.animation_controller.set_enabled(state == Qt.Checked)

    def toggle_unit_overlay(self, state):
        """Enable or unit overlay"""
        self.canvas.show_unit_overlay = bool(state)
        self.update_map_display() 
        #self.canvas.update()
        #self.update()  # Trigger a repaint
    
    def on_tile_selected(self, index):
        """Handle tile selection in palette"""
        self.palette.selected_tile = index
    
    def handle_canvas_click(self, event):
        """Handle clicks on the map canvas"""
        x = event.pos().x() // TILE_SIZE
        y = event.pos().y() // TILE_SIZE
        
        # Convert screen coordinates to map coordinates
        map_x = x + self.map_window_x
        map_y = y + self.map_window_y
        
        if event.buttons() == Qt.LeftButton:
            # Left click: place selected tile
            new_tile = self.palette.selected_tile
            if self.map_data.set_tile(map_x, map_y, new_tile):
                self.update_map_display()
        elif event.buttons() == Qt.RightButton:
            # Right click: erase tile
            if self.map_data.set_tile(map_x, map_y, -1):
                self.update_map_display()
    
    def handle_canvas_move(self, event):
        """Handle mouse movement over the canvas"""
        x = event.pos().x() // TILE_SIZE
        y = event.pos().y() // TILE_SIZE
        map_x = x + self.map_window_x
        map_y = y + self.map_window_y
        
        # Update cursor position display
        if (0 <= map_x < DEFAULT_MAP_WIDTH and 0 <= map_y < DEFAULT_MAP_HEIGHT):
            self.info_label.setText(f"Cursor: {map_x},{map_y} Tile: {self.palette.selected_tile}")
        
        # Handle drag painting
        if event.buttons() in (Qt.LeftButton, Qt.RightButton):
            self.handle_canvas_click(event)
    
    def navigate(self, dx, dy):
        """Move the view window by dx, dy tiles"""
        max_x = DEFAULT_MAP_WIDTH - self.map_window_width
        max_y = DEFAULT_MAP_HEIGHT - self.map_window_height
        
        self.map_window_x = max(0, min(self.map_window_x + dx, max_x))
        self.map_window_y = max(0, min(self.map_window_y + dy, max_y))
        
        # Update the map view
        self.update_map_display()
        
        # Make sure we keep focus for keyboard navigation
        self.canvas.setFocus()
    
    def choose_tileset_directory(self):
        """Open file dialog to choose a new tileset directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Choose Tileset Directory", "")
        if dir_path:
            self.tile_manager.tileset_dir = dir_path
            self.load_assets()
    
    def save_binary_map(self):
        """Save the map to a binary file"""
        #path, _ = QFileDialog.getSaveFileName(self, "Save Binary Map", "", "Binary Files (*.bin)")
        path, _ = QFileDialog.getSaveFileName(self, "Save Binary Map", "", "Map Files (*)")
        if path:
            if self.map_data.save_binary(path):
                self.info_label.setText(f"Map saved to {os.path.basename(path)}")
            else:
                self.info_label.setText("Error saving map")
    
    def load_binary_map_dialog(self):
        """Open dialog to load a binary map file"""
        #path, _ = QFileDialog.getOpenFileName(self, "Load Binary Map", "", "Binary Files (*.bin)")
        path, _ = QFileDialog.getOpenFileName(self, "Load Binary Map", "", "Map Files (*)")
        if path:
            self.load_binary_map(path)
    
    def load_binary_map(self, filepath):
        """Load a binary map file"""
        if self.map_data.load_binary(filepath):
            # Reset view position
            self.map_window_x = 0
            self.map_window_y = 0
            self.update_map_display()
            self.info_label.setText(f"Map loaded from {os.path.basename(filepath)}")
            self.setWindowTitle(f"{os.path.basename(filepath)}")
        else:
            self.info_label.setText(f"Error loading map")
    
    def undo(self):
        """Undo last map edit"""
        if self.map_data.undo():
            self.update_map_display()
            self.info_label.setText("Undo")
    
    def redo(self):
        """Redo last undone edit"""
        if self.map_data.redo():
            self.update_map_display()
            self.info_label.setText("Redo")
    
    def draw_tile_pattern(self, pattern_type):
        """Draw a pattern of tiles at the current cursor position"""
        # Get current cursor position from info label
        info_text = self.info_label.text()
        if "Cursor:" not in info_text:
            return  # No valid cursor position
        
        try:
            coords = info_text.split("Cursor: ")[1].split(" Tile:")[0].split(",")
            map_x = int(coords[0])
            map_y = int(coords[1])
        except (IndexError, ValueError):
            return  # Invalid cursor position format
        
        # Check if this is a special pattern with specific tile IDs
        if pattern_type in self.special_tile_patterns:
            # Special pattern with predefined tile IDs
            positions = self.special_tile_patterns[pattern_type]
            
            # Place each tile with its specific ID
            for dx, dy, tile_id in positions:
                self.map_data.set_tile(map_x + dx, map_y + dy, tile_id)
                
        else:
            # Regular pattern using currently selected tile
            # Get currently selected tile
            tile_id = self.palette.selected_tile
            
            # Use the selected pattern from our pattern dictionary
            # or default to a single tile if pattern not found
            positions = self.tile_patterns.get(pattern_type, [(0, 0)])
            
            # Place each tile in the pattern with the same tile ID
            for dx, dy in positions:
                self.map_data.set_tile(map_x + dx, map_y + dy, tile_id)
    
        # Update the display
        self.update_map_display()
        self.info_label.setText(f"Drew {pattern_type} pattern at {map_x},{map_y}")
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        # Get the key and modifiers
        key = event.key()
        modifiers = event.modifiers()
        
        # Navigation
        if key == Qt.Key_Left:
            self.navigate(-self.nav_speed, 0)
        elif key == Qt.Key_Right:
            self.navigate(self.nav_speed, 0)
        elif key == Qt.Key_Up:
            self.navigate(0, -self.nav_speed)
        elif key == Qt.Key_Down:
            self.navigate(0, self.nav_speed)
        # Quick tile selection with number keys (when no modifier is pressed)
        elif Qt.Key_0 <= key <= Qt.Key_9 and modifiers == Qt.NoModifier:
            tile_num = key - Qt.Key_0
            if tile_num < len(self.tile_manager.tiles):
                self.palette.set_selected_tile(tile_num)
        # Pattern drawing with defined key bindings and modifiers
        elif (key, modifiers) in self.pattern_keys:
            pattern_name = self.pattern_keys[(key, modifiers)]
            self.draw_tile_pattern(pattern_name)
        # Also check without modifiers for flexibility
        elif (key, Qt.NoModifier) in self.pattern_keys and modifiers == Qt.NoModifier:
            pattern_name = self.pattern_keys[(key, Qt.NoModifier)]
            self.draw_tile_pattern(pattern_name)
        else:
            super().keyPressEvent(event)
