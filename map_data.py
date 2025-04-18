import copy
import sys
#from constants import (DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT, MAP_DATA_OFFSET_LOAD,
#                       MAP_DATA_OFFSET_SAVE, 
#                       UNIT_TYPES_OFFSET, UNIT_X_OFFSET, 
#                       UNIT_Y_OFFSET, UNIT_A_OFFSET, 
#                       UNIT_B_OFFSET, UNIT_C_OFFSET, 
#                       UNIT_D_OFFSET, UNIT_H_OFFSET,
#                       UNIT_BLOCK_SIZE)
                       
from constants import (DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT,
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
        self.unit_offset = 0
        self.file_size = 0
        self.map_size = DEFAULT_MAP_WIDTH * DEFAULT_MAP_HEIGHT
        self.map_offet = 0
    
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
            #FILL_VALUE = self.fill_byte[0] 
            #bytes_to_write = bytearray([FILL_VALUE] * (MAP_DATA_OFFSET_SAVE + 128 * 64)) 
            bytes_to_write = bytearray([self.fill_byte[0]] * (self.map_offset + self.map_size)) 
            
            
            # Write the header bytes first
            bytes_to_write[0x0:0x02] = self.header_bytes
            #print(self.header_bytes)
            # Write unit data
              # Write unit data
            for i in range(UNIT_BLOCK_SIZE):
                # If the unit exists in our dictionary, use its data
                if i in self.unit_positions:
                    x, y, unit_type, a, b, c, d, h = self.unit_positions[i]
                    bytes_to_write[UNIT_TYPES_OFFSET + self.unit_offset + i] = unit_type
                    bytes_to_write[UNIT_X_OFFSET + self.unit_offset + i] = x
                    bytes_to_write[UNIT_Y_OFFSET + self.unit_offset + i] = y
                    bytes_to_write[UNIT_A_OFFSET + self.unit_offset + i] = a
                    bytes_to_write[UNIT_B_OFFSET + self.unit_offset + i] = b
                    bytes_to_write[UNIT_C_OFFSET + self.unit_offset + i] = c
                    bytes_to_write[UNIT_D_OFFSET + self.unit_offset + i] = d
                    bytes_to_write[UNIT_H_OFFSET + self.unit_offset + i] = h
                # If the unit doesn't exist, write fill bytes
                else:
                    bytes_to_write[UNIT_TYPES_OFFSET + self.unit_offset + i] = 0
                    bytes_to_write[UNIT_X_OFFSET + self.unit_offset + i]     = 0
                    bytes_to_write[UNIT_Y_OFFSET + self.unit_offset + i]     = 0
                    bytes_to_write[UNIT_A_OFFSET + self.unit_offset + i]     = 0
                    bytes_to_write[UNIT_B_OFFSET + self.unit_offset + i]     = 0
                    bytes_to_write[UNIT_C_OFFSET + self.unit_offset + i]     = 0
                    bytes_to_write[UNIT_D_OFFSET + self.unit_offset + i]     = 0
                    bytes_to_write[UNIT_H_OFFSET + self.unit_offset + i]     = 0
            # otherwise there will be a 01 in the beginning of the level if the values
            # of the player have been changed 
            if self.unit_offset == 2:
                bytes_to_write[0x0:0x02] = self.header_bytes
            
            # Write map data
            for y in range(min(self.height, 64)):
                for x in range(min(self.width, 128)):
                    # Convert -1 (empty) to 0 
                    tile = self.data[y][x]
                    if tile == -1:
                        tile = 0
                    ##### offset!!! depends on device!! 770 PET, 770-128-128 X16 
                    #bytes_to_write[MAP_DATA_OFFSET_SAVE + y * 128 + x] = tile & 0xFF
                    bytes_to_write[self.map_offset + y * 128 + x] = tile & 0xFF
            
            with open(filepath, 'wb') as f:
                f.write(bytes_to_write)
            
            print(f"\nLevel data saved to {filepath}.")
            
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
            self.header_bytes = binary_data[0x0:0x2]
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
            while binary_data[self.unit_offset] !=0x01:
                self.unit_offset += 1
                            
            unit_types = binary_data[UNIT_TYPES_OFFSET + self.unit_offset:UNIT_TYPES_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_xs = binary_data[UNIT_X_OFFSET + self.unit_offset:UNIT_X_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_ys = binary_data[UNIT_Y_OFFSET + self.unit_offset:UNIT_Y_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_a = binary_data[UNIT_A_OFFSET + self.unit_offset:UNIT_A_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_b = binary_data[UNIT_B_OFFSET + self.unit_offset:UNIT_B_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_c = binary_data[UNIT_C_OFFSET + self.unit_offset:UNIT_C_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_d = binary_data[UNIT_D_OFFSET + self.unit_offset:UNIT_D_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            unit_h = binary_data[UNIT_H_OFFSET + self.unit_offset:UNIT_H_OFFSET + self.unit_offset + UNIT_BLOCK_SIZE]
            # get the fill byte which is either 0xAA or 0x00 or "nothing" (X16 version)
            self.fill_byte = binary_data[UNIT_H_OFFSET + UNIT_BLOCK_SIZE + self.unit_offset:UNIT_H_OFFSET + UNIT_BLOCK_SIZE + self.unit_offset + 1]
            
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
            
            self.file_size = len(binary_data)
            self.map_offset = self.file_size - self.map_size
            #print(self.unit_offset + 512 + 128 * 64 - self.file_size - 512 - self.unit_offset)
            #print(self.file_size - 128 * 64)
            # get the first byte of the map
            #first_map_byte = binary_data[MAP_DATA_OFFSET_LOAD + self.unit_offset:MAP_DATA_OFFSET_LOAD + self.unit_offset + 1]
            #first_map_byte = binary_data[MAP_DATA_OFFSET_LOAD + self.unit_offset:MAP_DATA_OFFSET_LOAD + self.unit_offset + 1]
            first_map_byte = binary_data[self.map_offset + self.unit_offset:self.map_offset + self.unit_offset + 1]
            # if it is equal to self.fill_byte than there is no fill byte or offset is wrong
            
            #try to determine the level structure 
            if self.header_bytes[0] == 0x01 and self.file_size == 8960:
                print("\nThis is probably a level for the Amiga or MS-DOS.")
                print(f"First bytes: {self.header_bytes[0:2].hex().upper()}")
                print(f"File size  : {self.file_size}")
                print(f"Map offset : {self.map_offset}")
            elif self.header_bytes[1] == 0x5D and self.file_size == 8962:
                print("\nThis is probably a level for the PET, C64 or C128.")
                print(f"First bytes: {self.header_bytes[0:2].hex().upper()}")
                print(f"File size  : {self.file_size}")
                print(f"Map offset : {self.map_offset}")
            elif self.file_size == 8706:
                print("\nThis is probably a level for the X16.")
                print(f"First bytes: {self.header_bytes[0:2].hex().upper()}")
                print(f"File size  : {self.file_size}")
                print(f"Map offset : {self.map_offset}")
            else:
                print("\nUnknown level architecture. Exit.")
                print(f"First bytes: {self.header_bytes[0:2].hex().upper()}")
                print(f"File size  : {self.file_size}")
                print(f"Map offset : {self.map_offset}")
                sys.exit(1)
                
            if first_map_byte == self.fill_byte:
                print("\nFill Byte: None")
                print("\nExcept for the X16 version, the fill byte should be not 'None'.")
            else:
                print(f"\nFill Byte: {self.fill_byte.hex().upper()}")
                
            # Process map tiles
            print("\n--- Loading Map Tiles ---")
            #index = MAP_DATA_OFFSET_LOAD
            index = self.map_offset
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
            #print(f"Map data starts at offset: {MAP_DATA_OFFSET_LOAD}")
            print(f"Map data starts at offset: {self.map_offset}")
            print(f"Expected map size: {self.width * self.height} bytes")
            print(f"Actual data after offset: {self.file_size - self.map_offset} bytes")
            
            return True
        except IOError as e:
            print(f"Error loading binary map file '{filepath}': {e}")
            return False
