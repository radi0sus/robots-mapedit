import copy
from constants import DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT

class MapData:
    """Manages the map data and provides undo/redo functionality"""
    
    def __init__(self):
        # Initialize map with empty tiles (-1)
        self.data = [[-1 for _ in range(DEFAULT_MAP_WIDTH)] for _ in range(DEFAULT_MAP_HEIGHT)]
        self.width = DEFAULT_MAP_WIDTH
        self.height = DEFAULT_MAP_HEIGHT
        self.undo_stack = []
        self.redo_stack = []
        self.unit_positions = {}  # Maps unit_id to (x, y, unit_type)
    
    def get_tile(self, x, y):
        """Get the tile at (x, y) coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return -1
    
    def set_tile(self, x, y, tile_id):
        """Set the tile at (x, y) coordinates and return True if successful"""
        if 0 <= x < self.width and 0 <= y < self.height:
            current = self.data[y][x]
            if current != tile_id:
                self.push_undo()
                self.data[y][x] = tile_id
                return True
        return False
    
    def push_undo(self):
        """Save current state to undo stack"""
        self.undo_stack.append(copy.deepcopy(self.data))
        self.redo_stack.clear()
    
    def undo(self):
        """Restore previous state from undo stack"""
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.data))
            self.data = self.undo_stack.pop()
            return True
        return False
    
    def redo(self):
        """Restore next state from redo stack"""
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.data))
            self.data = self.redo_stack.pop()
            return True
        return False
    
    def save_binary(self, filepath):
        """Save map to binary file format"""
        try:
            # PETSCII Robots format: 128x64 map
            bytes_to_write = bytearray()
            
            # Write map data
            for y in range(min(self.height, 64)):
                for x in range(min(self.width, 128)):
                    # Convert -1 (empty) to 0 
                    tile = self.data[y][x]
                    if tile == -1:
                        tile = 0
                    bytes_to_write.append(tile & 0xFF)
            
            # Pad to full 128x64 size if smaller
            remaining_bytes = 128 * 64 - len(bytes_to_write)
            if remaining_bytes > 0:
                bytes_to_write.extend([0] * remaining_bytes)
            
            with open(filepath, 'wb') as f:
                f.write(bytes_to_write)
            
            return True
        except IOError as e:
            print(f"Error saving binary map: {e}")
            return False
    
    def load_binary(self, filepath):
        """Load map from binary file format"""
        from constants import (MAP_DATA_OFFSET, UNIT_TYPES_OFFSET, UNIT_X_OFFSET, UNIT_Y_OFFSET, 
                              UNIT_A_OFFSET, UNIT_B_OFFSET, UNIT_C_OFFSET, UNIT_D_OFFSET ,UNIT_H_OFFSET)
        
        try:
            with open(filepath, 'rb') as f:
                binary_data = f.read()
            
            # Reset map data
            self.data = [[-1 for _ in range(self.width)] for _ in range(self.height)]
            self.unit_positions = {}
            
            # Extract unit data
            unit_types = binary_data[UNIT_TYPES_OFFSET:UNIT_TYPES_OFFSET+0x40]
            unit_xs = binary_data[UNIT_X_OFFSET:UNIT_X_OFFSET+0x40]
            unit_ys = binary_data[UNIT_Y_OFFSET:UNIT_Y_OFFSET+0x40]
            unit_a = binary_data[UNIT_A_OFFSET:UNIT_A_OFFSET+0x40]
            unit_b = binary_data[UNIT_B_OFFSET:UNIT_B_OFFSET+0x40]
            unit_c = binary_data[UNIT_C_OFFSET:UNIT_C_OFFSET+0x40]
            unit_d = binary_data[UNIT_D_OFFSET:UNIT_D_OFFSET+0x40]
            unit_h = binary_data[UNIT_H_OFFSET:UNIT_H_OFFSET+0x40]
            
            # Process units
            for i in range(64):
                x = unit_xs[i]
                y = unit_ys[i]
                t = unit_types[i]
                a = unit_a[i]
                b = unit_b[i]
                c = unit_c[i]
                d = unit_d[i]
                h = unit_h[i]
                if x < 128 and y < 64 and t != 0:
                    self.unit_positions[i] = (x, y, t, a, b, c, d, h)
                    if t == 1:
                        print(f"Player (Unit {i}): Position ({x}, {y}), Type: {t}, A: {a}, B: {b}, C: {c}, D: {d}, Health: {h}")
                        self.unit_positions[0] = (x, y, t, a, b, c, d, h)  # Assign player to Unit 0
                    else:
                        print(f"Unit {i}: Position ({x}, {y}), Type: {t}, A: {a}, B: {b}, C: {c}, D: {d}, Health: {h}")
            
            # Process map tiles
            print("\n--- Loading Map Tiles ---")
            index = MAP_DATA_OFFSET
            for y in range(self.height):
                for x in range(self.width):
                    if index < len(binary_data):
                        tile_value = binary_data[index]
                        if tile_value > 0:
                            self.data[y][x] = tile_value
                    index += 1
            
            # Map info
            print(f"\nMap size: {self.width}x{self.height}")
            print(f"Map data starts at offset: {MAP_DATA_OFFSET}")
            print(f"Expected map size: {self.width * self.height} bytes")
            print(f"Actual data after offset: {len(binary_data) - MAP_DATA_OFFSET} bytes")
            
            return True
        except IOError as e:
            print(f"Error loading binary map file '{filepath}': {e}")
            return False