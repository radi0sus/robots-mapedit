import copy
from constants import (DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT, MAP_DATA_OFFSET_LOAD,
                       MAP_DATA_OFFSET_SAVE, 
                       UNIT_TYPES_OFFSET, UNIT_X_OFFSET, 
                       UNIT_Y_OFFSET, UNIT_A_OFFSET, 
                       UNIT_B_OFFSET, UNIT_C_OFFSET, 
                       UNIT_D_OFFSET, UNIT_H_OFFSET,
                       UNIT_BLOCK_SIZE)

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
        # header 
        self.header_bytes = bytearray([0x0, 0x0])  # Default to zeros
        self.fill_byte = 0x00
    
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
            # PETSCII Robots format with units
            #bytes_to_write = bytearray(770 + 128 * 64)  # Initialize with zeros
            #bytes_to_write = bytearray([FILL_VALUE] * (MAP_DATA_OFFSET_SAVE + 128 * 64)) 
            # fill byte array with fill byte (0x00, 0xAA or "nothing")
            FILL_VALUE = self.fill_byte[0]
            bytes_to_write = bytearray([FILL_VALUE] * (MAP_DATA_OFFSET_SAVE + 128 * 64)) 
            
            # Write the header bytes first
            bytes_to_write[0x0000:0x0002] = self.header_bytes
            #print(self.header_bytes)
            # Write unit data
            for unit_id, (x, y, unit_type, a, b, c, d, h) in self.unit_positions.items():
            #if 0 <= unit_id < 65:
                #bytes_to_write[unit_id] = unit_type                              # Unit type
                #bytes_to_write[BASE_ADDRESS+0x0040 + unit_id] = x               # X position
                #bytes_to_write[BASE_ADDRESS+0x0080 + unit_id] = y               # Y position
                #bytes_to_write[BASE_ADDRESS+0x00C0 + unit_id] = a               # Property A
                #bytes_to_write[BASE_ADDRESS+0x0100 + unit_id] = b               # Property B
                #bytes_to_write[BASE_ADDRESS+0x0140 + unit_id] = c               # Property C
                #bytes_to_write[BASE_ADDRESS+0x0180 + unit_id] = d               # Property D
                #bytes_to_write[BASE_ADDRESS+0x01C0 + unit_id] = h               # Health
                #UNIT_TYPES_OFFSET = UNIT_TYPES_OFFSET + BASE_ADDRESS 
                #UNIT_X_OFFSET = UNIT_X_OFFSET + BASE_ADDRESS
                #UNIT_Y_OFFSET = UNIT_Y_OFFSET + BASE_ADDRESS
                #UNIT_A_OFFSET = UNIT_A_OFFSET + BASE_ADDRESS
                #UNIT_B_OFFSET = UNIT_B_OFFSET + BASE_ADDRESS
                #UNIT_C_OFFSET = UNIT_C_OFFSET + BASE_ADDRESS
                #UNIT_D_OFFSET = UNIT_D_OFFSET + BASE_ADDRESS
                #UNIT_H_OFFSET = UNIT_H_OFFSET + BASE_ADDRESS
                bytes_to_write[UNIT_TYPES_OFFSET + unit_id] = unit_type  
                bytes_to_write[UNIT_X_OFFSET + unit_id] = x               # X position
                bytes_to_write[UNIT_Y_OFFSET + unit_id] = y               # Y position
                bytes_to_write[UNIT_A_OFFSET + unit_id] = a               # Property A
                bytes_to_write[UNIT_B_OFFSET + unit_id] = b               # Property B
                bytes_to_write[UNIT_C_OFFSET + unit_id] = c               # Property C
                bytes_to_write[UNIT_D_OFFSET + unit_id] = d               # Property D
                bytes_to_write[UNIT_H_OFFSET + unit_id] = h               # Health
            
            # Write map data
            for y in range(min(self.height, 64)):
                for x in range(min(self.width, 128)):
                    # Convert -1 (empty) to 0 
                    tile = self.data[y][x]
                    if tile == -1:
                        tile = 0
                    ##### offset!!! depends on device!! 770 PET, 770-128-128 X16 
                    bytes_to_write[MAP_DATA_OFFSET_SAVE + y * 128 + x] = tile & 0xFF
            
            with open(filepath, 'wb') as f:
                f.write(bytes_to_write)
            
            return True
        except IOError as e:
            print(f"Error saving binary map: {e}")
            return False
    
    def load_binary(self, filepath):
        """Load map from binary file format"""
        
        try:
            with open(filepath, 'rb') as f:
                binary_data = f.read()
            # Reset map data
            #self.data = [[-1 for _ in range(self.width)] for _ in range(self.height)]
            #self.unit_positions = {}
            #header
            self.header_bytes = binary_data[0x0000:0x0002]
            #print(self.header_bytes)
            # Extract unit data
            #UNIT_TYPES_OFFSET = UNIT_TYPES_OFFSET + BASE_ADDRESS 
            #UNIT_X_OFFSET = UNIT_X_OFFSET + BASE_ADDRESS
            #UNIT_Y_OFFSET = UNIT_Y_OFFSET + BASE_ADDRESS
            #UNIT_A_OFFSET = UNIT_A_OFFSET + BASE_ADDRESS
            #UNIT_B_OFFSET = UNIT_B_OFFSET + BASE_ADDRESS
            #UNIT_C_OFFSET = UNIT_C_OFFSET + BASE_ADDRESS
            #UNIT_D_OFFSET = UNIT_D_OFFSET + BASE_ADDRESS
            #UNIT_H_OFFSET = UNIT_H_OFFSET + BASE_ADDRESS
            unit_types = binary_data[UNIT_TYPES_OFFSET:UNIT_TYPES_OFFSET + UNIT_BLOCK_SIZE]
            unit_xs = binary_data[UNIT_X_OFFSET:UNIT_X_OFFSET + UNIT_BLOCK_SIZE]
            unit_ys = binary_data[UNIT_Y_OFFSET:UNIT_Y_OFFSET + UNIT_BLOCK_SIZE]
            unit_a = binary_data[UNIT_A_OFFSET:UNIT_A_OFFSET + UNIT_BLOCK_SIZE]
            unit_b = binary_data[UNIT_B_OFFSET:UNIT_B_OFFSET + UNIT_BLOCK_SIZE]
            unit_c = binary_data[UNIT_C_OFFSET:UNIT_C_OFFSET + UNIT_BLOCK_SIZE]
            unit_d = binary_data[UNIT_D_OFFSET:UNIT_D_OFFSET + UNIT_BLOCK_SIZE]
            unit_h = binary_data[UNIT_H_OFFSET:UNIT_H_OFFSET + UNIT_BLOCK_SIZE]
            # get the fill byte which is either 0xAA or 0x00 or "nothing" (X16 version)
            self.fill_byte = binary_data[UNIT_H_OFFSET + UNIT_BLOCK_SIZE:UNIT_H_OFFSET + UNIT_BLOCK_SIZE + 1]
            
            # Process units
            for i in range(UNIT_BLOCK_SIZE):
                x = unit_xs[i]
                y = unit_ys[i]
                t = unit_types[i]
                a = unit_a[i]
                b = unit_b[i]
                c = unit_c[i]
                d = unit_d[i]
                h = unit_h[i]

                self.unit_positions[i] = (x, y, t, a, b, c, d, h)
                if t == 1:
                    print(f"Player (Unit {i}): Position ({x}, {y}), Type: {t}, A: {a}, B: {b}, C: {c}, D: {d}, Health: {h}")
                    #self.unit_positions[0] = (x, y, t, a, b, c, d, h)  # Assign player to Unit 0
                else:
                    print(f"Unit {i}: Position ({x}, {y}), Type: {t}, A: {a}, B: {b}, C: {c}, D: {d}, Health: {h}")
                
                #if x < 128 and y < 64 and t != 0:
                #    self.unit_positions[i] = (x, y, t, a, b, c, d, h)
                #    if t == 1:
                #        print(f"Player (Unit {i}): Position ({x}, {y}), Type: {t}, A: {a}, B: {b}, C: {c}, D: {d}, Health: {h}")
                #        self.unit_positions[0] = (x, y, t, a, b, c, d, h)  # Assign player to Unit 0
                #    else:
                #        print(f"Unit {i}: Position ({x}, {y}), Type: {t}, A: {a}, B: {b}, C: {c}, D: {d}, Health: {h}")
            
            # get the first byte of the map
            first_map_byte = binary_data[MAP_DATA_OFFSET_LOAD:MAP_DATA_OFFSET_LOAD + 1]
            # if it is equal to self.fill_byte than there is no fill byte or offset is wrong
            if first_map_byte == self.fill_byte:
                print("\nFill Byte: None")
            else:
                print(f"\nFill Byte: {self.fill_byte.hex().upper()}")
            # Process map tiles
            print("\n--- Loading Map Tiles ---")
            index = MAP_DATA_OFFSET_LOAD
            for y in range(self.height):
                for x in range(self.width):
                    if index < len(binary_data):
                        tile_value = binary_data[index]
                        #if tile_value > 0:
                        if tile_value >= 0:
                            self.data[y][x] = tile_value
                    index += 1
            
            # Map info
            print(f"\nMap size: {self.width}x{self.height}")
            print(f"Map data starts at offset: {MAP_DATA_OFFSET_LOAD}")
            print(f"Expected map size: {self.width * self.height} bytes")
            print(f"Actual data after offset: {len(binary_data) - MAP_DATA_OFFSET_LOAD} bytes")
            
            return True
        except IOError as e:
            print(f"Error loading binary map file '{filepath}': {e}")
            return False
