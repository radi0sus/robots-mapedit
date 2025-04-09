import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog,
    QComboBox, QGridLayout, QVBoxLayout, QScrollArea,
    QShortcut, QCheckBox, QHBoxLayout
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from constants import (
    TILE_SIZE, DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT, MAP_WIDTH, MAP_HEIGHT,
    DEFAULT_NAV_SPEED, ANIMATION_INTERVAL, APP_WIDTH, APP_HEIGHT
)
from map_data import MapData
from tile_manager import TileManager
from animation import AnimationController
from ui_components import TilesetPaletteWidget, MapCanvasWidget

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
        
        # Navigation properties
        self.map_window_x = 0
        self.map_window_y = 0
        self.map_window_width = MAP_WIDTH
        self.map_window_height = MAP_HEIGHT
        self.nav_speed = DEFAULT_NAV_SPEED
        
        # Initial loading
        self.load_assets()
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Set focus to the canvas
        self.canvas.setFocus()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Map canvas
        self.canvas = MapCanvasWidget(self)
        self.canvas.window_width = MAP_WIDTH
        self.canvas.window_height = MAP_HEIGHT
        
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
        self.canvas.update()
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
        path, _ = QFileDialog.getSaveFileName(self, "Save Binary Map", "", "Binary Files (*.bin)")
        if path:
            if self.map_data.save_binary(path):
                self.info_label.setText(f"Map saved to {os.path.basename(path)}")
            else:
                self.info_label.setText("Error saving map")
    
    def load_binary_map_dialog(self):
        """Open dialog to load a binary map file"""
        path, _ = QFileDialog.getOpenFileName(self, "Load Binary Map", "", "Binary Files (*.bin)")
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
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        # Navigation
        if event.key() == Qt.Key_Left:
            self.navigate(-self.nav_speed, 0)
        elif event.key() == Qt.Key_Right:
            self.navigate(self.nav_speed, 0)
        elif event.key() == Qt.Key_Up:
            self.navigate(0, -self.nav_speed)
        elif event.key() == Qt.Key_Down:
            self.navigate(0, self.nav_speed)
        # Quick tile selection with number keys
        elif Qt.Key_0 <= event.key() <= Qt.Key_9:
            tile_num = event.key() - Qt.Key_0
            if tile_num < len(self.tile_manager.tiles):
                self.palette.set_selected_tile(tile_num)
        else:
            super().keyPressEvent(event)