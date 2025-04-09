import os
from PyQt5.QtGui import QImage, QPixmap

class TileManager:
    """Manages tile loading and animation"""
    
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.tiles = []
        self.anim_tiles = []
        self.tileset_files = []
        self.tileset_dir = "tiles"
        self.current_tileset = None
        
        # Animation mapping: tile_id -> range of animation frames
        self.animation_map = {
            204: range(20, 24),   # WATER: frames 20, 21, 22, 23 in anim_tiles
            66: range(0, 4),      # FLAG: frames 0, 1, 2, 3
            148: range(4, 8),     # TRASH COMPACTOR: frames 4, 5, 6, 7
            143: range(16, 20),   # SERVER: frames 16, 17, 18, 19
            196: range(8, 10),    # HVAC 1: frames 8, 9
            197: range(10, 12),   # HVAC 2: frames 10, 11
            200: range(12, 14),   # HVAC 3: frames 12, 13
            201: range(14, 16),   # HVAC 4: frames 14, 15
            20: range(24, 28),    # CINEMA 1: frames 24, 25, 26, 27
            21: range(28, 32),    # CINEMA 2: frames 28, 29, 30, 31
            22: range(32, 36),    # CINEMA 3: frames 32, 33, 34, 35
        }
        
        # List of tiles that can be animated
        self.animated_tiles = [20, 21, 22, 66, 143, 148, 196, 197, 200, 201, 204]
    
    def scan_tileset_directory(self):
        """Scan the tileset directory for available tilesets"""
        self.tileset_files = [f for f in os.listdir(self.tileset_dir) if f.endswith(".png")]
        return self.tileset_files
    
    def load_tileset(self, filename):
        """Load a tileset from a PNG file"""
        self.current_tileset = filename
        path = os.path.join(self.tileset_dir, filename)
        tileset_img = QImage(path)
        self.tiles = []
        
        # Calculate how many tiles fit in the image
        tiles_per_row = tileset_img.width() // self.tile_size
        tiles_per_col = tileset_img.height() // self.tile_size
        
        # Extract individual tiles
        for y in range(tiles_per_col):
            for x in range(tiles_per_row):
                tile_rect = (x * self.tile_size, y * self.tile_size, 
                           self.tile_size, self.tile_size)
                tile = tileset_img.copy(*tile_rect)
                self.tiles.append(QPixmap.fromImage(tile))
        
        return len(self.tiles)
    
    def load_animated_tileset(self, filename='animtiles.png'):
        """Load animated tiles from a separate tileset"""
        path = os.path.join(self.tileset_dir, filename)
        if not os.path.exists(path):
            print(f"Warning: Animated tileset not found at {path}")
            return 0
            
        tileset_img = QImage(path)
        self.anim_tiles = []
        
        # Extract animation frames
        tiles_per_row = tileset_img.width() // self.tile_size
        tiles_per_col = tileset_img.height() // self.tile_size
        
        for y in range(tiles_per_col):
            for x in range(tiles_per_row):
                tile_rect = (x * self.tile_size, y * self.tile_size, 
                           self.tile_size, self.tile_size)
                tile = tileset_img.copy(*tile_rect)
                self.anim_tiles.append(QPixmap.fromImage(tile))
        
        return len(self.anim_tiles)
    
    def get_tile_pixmap(self, tile_id, anim_state=0, show_animations=True):
        """Get the pixmap for a tile, considering animation state"""
        # Check if it's an animated tile
        if show_animations and tile_id in self.animation_map:
            frame_range = self.animation_map[tile_id]
            num_frames = len(frame_range)
            
            if num_frames > 0 and len(self.anim_tiles) > frame_range.start + (anim_state % num_frames):
                frame_index = frame_range.start + (anim_state % num_frames)
                return self.anim_tiles[frame_index]
        
        # Return normal tile if not animated or animations disabled
        if 0 <= tile_id < len(self.tiles):
            return self.tiles[tile_id]
            
        return None