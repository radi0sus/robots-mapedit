#!/usr/bin/env python3
# robots level convert
# convert level files among different versions

# PET, C64, C128 <-> Amiga, MS-DOS <-> X16 (full version from 8-Bit Guy web site)

import sys
import argparse

# define values for detection and conversion
#
# PET, C64, C128 and X16 have 2 header bytes which are 00 5D 
# (once I found 00 7D for level-a X16)
# MS-DOS and Amiga have no header, it starts directly with the player id, which is 01
#
# after unit definitions there is an area of 256 bytes which are often 00 or AA (level-a)
# in case of PET, C64, C128, MS-DOS and Amiga - but not in case of X16
# in case of X16, the map starts directly after the unit definitions
#
# from that point on until the end of the file are map data
#
# total file sizes:
# PET, C64, C128 = 8962
# MS-DOS, Amiga  = 8960
# X16            = 8706
#
# the X16 levels from github are different from those of the download version
#
# 0x7D will not be written if a file is converted from or to X16
# the 256 byte region will be filled with 00 when converted from X16

LEVEL_PROP = {
        # MS-DOS and Amiga
        "MSD": {
            "FIRST_BYTES"     : 0x01,          # player unit id = 1 in case of MS-DOS/Amiga 
            "FIRST_BYTES_LEN" : 0,             # header size = 0
            "FILL_SIZE"       : 256,           # size of the AA or 00 filled region
            "UNITS_END_POS"   : 0x01C0 + 0x40, # end position for unit definitions
            "FILL_BYTE"       : 0x00,          # will be determined (AA or 00)
            "LEVEL_SIZE"      : 8960           # total level file size
        },                                   
        # PET, C64, C128
        "PET": {
            "FIRST_BYTES"     : 0x5D,          # header
            "FIRST_BYTES_LEN" : 2,             # header size
            "FILL_SIZE"       : 256,           # size of the AA or 00 filled region
            "UNITS_END_POS"   : 0x01C0 + 0x42, # end position for unit definitions
            "FILL_BYTE"       : 0x00,          # will be determined (AA or 00)
            "LEVEL_SIZE"      : 8962           # total level file size 
        },
        # X16 full version from 8-Bit Guy Homepage
        "X16": {
            "FIRST_BYTES"    : 0x5D,           # header, could be 0x7D as well
            "FIRST_BYTES_LEN": 2,              # header size
            "FILL_SIZE"      : 0,              # size of the AA or 00 filled region = 0
            "UNITS_END_POS"  : 0x01C0 + 0x42,  # end position for unit definitions
            "FILL_BYTE"      : 0x00,           # from X16 to other vers. = 00
            "LEVEL_SIZE"     : 8706            # total level file size 
        }
    }


# read the level
def read_level(file_name):
    try:    
        with open(file_name, 'rb') as level_file:
            level_data = level_file.read()
    except IOError as e:
        print(f"\nError loading level data '{file_name}': {e}. Exit.")
        sys.exit(1)
    return level_data

# save the level
# add suffix of the converted version
# suffix is .PET for PET, C64, C128
# suffix is .MSD for MS-DOS and Amiga
# suffix is .X16 for X16
def save_level(level_data, file_name, suffix):
    level_fill  = 0x00
    try:    
        with open(f'{file_name}.{suffix}', 'wb') as level_file:
            level_file.write(level_data)
            
        if suffix == 'PET':
            print("\nThe level has been converted to PET/C64/C128 format.")
            level_fill = level_data[LEVEL_PROP['PET']['UNITS_END_POS']:
                         LEVEL_PROP['PET']['UNITS_END_POS'] + 1]
                         
        elif suffix == 'MSD':
            print("\nThe level has been converted to Amiga/MS-DOS format.")
            level_fill = level_data[LEVEL_PROP['MSD']['UNITS_END_POS']:
                         LEVEL_PROP['MSD']['UNITS_END_POS'] + 1]
                         
        elif suffix == 'X16':
            print("\nThe level has been converted to X16 format.")
            level_fill = None
        
        first_bytes = level_data[0:2]
        print(f'First Bytes: {first_bytes.hex().upper()}')
        print(f'Size: {len(level_data)}')
        
        if level_fill:
            print(f"Fill Byte: {level_fill.hex().upper()}")
        else:
            print("Fill Byte: None")
            
        print(f"\n{file_name}.{suffix} written.")
        
    except IOError as e:
        print(f"\nError saving level data {file_name}.{suffix}: {e}. Exit.")
        sys.exit(1)
    return level_data

# detect the robots version from level data (mainly via file size and first byte) 
# return the detected version
def det_lvl_form(level_data):

    level_ver   = "UNK"
    level_fill  = 0x00
    first_bytes = level_data[0:2]
    
    print(f'\nFirst Bytes: {first_bytes.hex().upper()}')
    print(f'Size: {len(level_data)}')
    
    if level_data[0] == LEVEL_PROP['MSD']['FIRST_BYTES'] and \
       len(level_data) == LEVEL_PROP['MSD']['LEVEL_SIZE']:
       
        print("\nThis level is probably Amiga or MS-DOS format.")
        level_ver = "MSD"
        level_fill = level_data[LEVEL_PROP['MSD']['UNITS_END_POS']:
                                LEVEL_PROP['MSD']['UNITS_END_POS'] + 1]
        print(f"Fill Byte: {level_fill.hex().upper()}")
        # get the Fill Byte (00 or AA)
        LEVEL_PROP['MSD']['FILL_BYTE'] = level_fill[0]
                
    elif level_data[0:2] == LEVEL_PROP['PET']['FIRST_BYTES'] \
                            .to_bytes(2, byteorder = 'big') and \
                            len(level_data) == LEVEL_PROP['PET']['LEVEL_SIZE']:
         
        print("\nThis level is probably PET, C64 or C128 format.")
        level_ver = "PET"
        level_fill = level_data[LEVEL_PROP['PET']['UNITS_END_POS']:
                                LEVEL_PROP['PET']['UNITS_END_POS'] + 1]
        print(f"Fill Byte: {level_fill.hex().upper()}")
        #LEVEL_PROP['PET']['FIRST_BYTES'] = int.from_bytes(level_data[0:2], byteorder='big')
        # get the Fill Byte (00 or AA)
        LEVEL_PROP['PET']['FILL_BYTE'] = level_fill[0]
        
    elif len(level_data) == LEVEL_PROP['X16']['LEVEL_SIZE']:
    
        print("\nThis level is probably X16 format.")
        level_ver = "X16"
        # no fill byte in case of X16
        print("Fill Byte: None")
        #LEVEL_PROP['X16']['FIRST_BYTES'] = int.from_bytes(level_data[0:2], byteorder='big')
    else:
        # Unkown level type or version
        print("\nUnknown level architecture.")
        level_ver = None
        
    return level_ver

# convert the level to the specified version [PET, MS-DOS, X16]
# PET includes C64 & C128, MS-DOS includes Amiga
def lvl_cnv(from_ver, to_ver, level_data):
    level = bytearray(0)
    # in case of PET & X16, write the first two bytes
    if LEVEL_PROP[to_ver]['FIRST_BYTES_LEN']:
        first_bytes = LEVEL_PROP[to_ver]['FIRST_BYTES'] \
                      .to_bytes(LEVEL_PROP[to_ver]['FIRST_BYTES_LEN'], byteorder='big')
        level = first_bytes
    # unit bytes
    unit_bytes = level_data[LEVEL_PROP[from_ver]['FIRST_BYTES_LEN']:
                             LEVEL_PROP[from_ver]['UNITS_END_POS']]
    # region that is filled with AA or 00
    fill_bytes = bytearray([LEVEL_PROP[from_ver]['FILL_BYTE']] * 
                            LEVEL_PROP[to_ver]['FILL_SIZE'])
    # remainign map bytes
    map_bytes  = level_data[LEVEL_PROP[from_ver]['UNITS_END_POS'] + 
                            LEVEL_PROP[from_ver]['FILL_SIZE']:]
    # combine them all together to the level file
    level = level + unit_bytes + fill_bytes + map_bytes
    return level

############# Argument parser START
parser = argparse.ArgumentParser(prog = 'cnvlvl', 
         description = "Convert level for different Robots versions.")

#filename is required
parser.add_argument('filename',
                    type = str,
                    help = 'filename of the level to be converted; e.g. level-a')

# convert to
parser.add_argument('convert_to',
                    type = str,
                    default = 'X16',
                    choices = ['PET', 'MSD', 'X16'],
                    help    = 'Target level format for conversion. PET includes C64 and \
                               C128, MSD includes MS-DOS and Amiga. The file extension \
                               denotes the format of the converted level, e.g. level-a.PET')

args = parser.parse_args()
############# Argument parser END

# read level data
level_data = read_level(args.filename)
# determine level version
level_ver  = det_lvl_form(level_data)

if level_ver:
    # convert the level to the specified version
    cnv_level = lvl_cnv(level_ver, args.convert_to, level_data)
    # save the level in the new format
    save_level(cnv_level, args.filename, args.convert_to)
else:
    # exit in case of unknown level architecture
    print("\nFiles with unknown level architecture can't be converted. Exit.")
    sys.exit(1)
