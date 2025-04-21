import xml.etree.ElementTree as ET
import xml.dom.minidom
import argparse
import sys
import os

# map sizes
MAP_WIDTH = 128
MAP_HEIGHT = 64 

# Offsets
UNIT_TYPES_OFFSET  = 0x0000 
UNIT_X_OFFSET      = 0x0040 
UNIT_Y_OFFSET      = 0x0080 
UNIT_A_OFFSET      = 0x00C0 
UNIT_B_OFFSET      = 0x0100 
UNIT_C_OFFSET      = 0x0140 
UNIT_D_OFFSET      = 0x0180 
UNIT_H_OFFSET      = 0x01C0 
UNIT_BLOCK_SIZE    = 0x40   

# animation
ANIM_DURATION = 250 #ms
# combined tiles.png and animtiles.png to show animations
# if not present, dont't show animated tiles
MERGED_TILES = "tiles/merged_tiles.png" 


# unit types
unit_types = {
  0: "Unknown",
  1: "Player",
  2: "HBot l/r",
  3: "HBot u/d",
  4: "HBot chase attack mode",
  7: "Transporter pad",
  9: "Evilbot",
 10: "Door",
 16: "Trash comp",
 17: "RBot u/d",
 18: "RBot l/r",
 19: "Lift",
 22: "Water raft",
128: "Key",
129: "Time bomb",
130: "EMP",
131: "Pistol",
132: "Plasma gun",
133: "Medkit",
134: "Magnet"
}

# tiles to special units
unit_tiles = {
  0: 1,
  1: 301,
  2: 350,
  3: 350,
  4: 350,
  7: 31,
  9: 358,
 10: 254,
 16: 149,
 17: 354,
 18: 354,
 19: 82,
 22: 242,
128: 501,
129: 406,
130: 404,
131: 401,
132: 402,
133: 403,
134: 405
}

# special attributes of units
unit_attributes = {
  1: ["A", "B", "C", "D", "Health"],
  2: ["A", "B", "C", "D", "Health"],
  3: ["A", "B", "C", "D", "Health"],
  4: ["A", "B", "C", "D", "Health"],
  7: ["A: Activation (0=always active 1=only active when all robots are dead)", 
      "B: Destination (0=completes level 1=send to coordinates)", 
      "C: X-coordinate", 
      "D: Y-coordinate", 
      "H"],
  9: ["A", "B", "C", "D", "Health"],
 10: ["A: Orientation (0=horizontal 1=vertical)", 
      "B: Current State (0=opening-A 1=opening-B 2=OPEN / 3=closing-A 4=closing-B 5-CLOSED)", 
      "C: Locking (0=unlocked / 1=locked spade 2=locked heart 3=locked star)", 
      "D", 
      "H"],
 16: ["A", "B", "C", "D", "H"],
 17: ["A", "B", "C", "D", "Health"],
 18: ["A", "B", "C", "D", "Health"],
 19: ["A", 
      "B: Current State (0=opening-A 1=opening-B 2=OPEN / 3=closing-A 4=closing-B 5-CLOSED)", 
      "C: Which floor corresponds to this unit?", 
      "D: Max number of levels (number should be between 2 and 5)", 
      "H"],
 22: ["A: Current direction (0=left 1=right)", 
      "B: Left-most coordinate", 
      "C: Right-most coordinate", 
      "D", 
      "H"],
128: ["A: 0=SPADE 1=HEART 2=STAR", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H"],
129: ["A: Quantity (between 1 and 255)", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H"],
130: ["A: Quantity (between 1 and 255)", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H:"],
131: ["A: Quantity (between 1 and 255)", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H"],
132: ["A: Quantity (between 1 and 255)", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H"],
133: ["A: Quantity (between 1 and 255)", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H"],
134: ["A: Quantity (between 1 and 255)", 
      "B", 
      "C: Extend search area horizontal (between 0 and 127)", 
      "D: Extend search area vertical (between 0 and 63)", 
      "H"],
}

# load map
def load_map(filename = "level-a"):
    unit_offset = 0
    try:
        with open(filename, 'rb') as f:
            binary_data = f.read()

        while binary_data[unit_offset] !=0x01:
                unit_offset += 1
                
        header_bytes = binary_data[0:unit_offset]
        
        unit_t = binary_data[UNIT_TYPES_OFFSET + unit_offset:UNIT_TYPES_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_x = binary_data[UNIT_X_OFFSET + unit_offset:UNIT_X_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_y = binary_data[UNIT_Y_OFFSET + unit_offset:UNIT_Y_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_a = binary_data[UNIT_A_OFFSET + unit_offset:UNIT_A_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_b = binary_data[UNIT_B_OFFSET + unit_offset:UNIT_B_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_c = binary_data[UNIT_C_OFFSET + unit_offset:UNIT_C_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_d = binary_data[UNIT_D_OFFSET + unit_offset:UNIT_D_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        unit_h = binary_data[UNIT_H_OFFSET + unit_offset:UNIT_H_OFFSET + unit_offset + UNIT_BLOCK_SIZE]
        file_size = len(binary_data)
        map_size = MAP_WIDTH * MAP_HEIGHT
        map_offset = file_size - map_size
        fill_bytes = binary_data[UNIT_H_OFFSET + unit_offset + UNIT_BLOCK_SIZE:map_offset]
        map_data = binary_data[map_offset:file_size]
        
        level_dict = {
            "File Name"   : filename,
            "File Size"   : file_size,
            "Header Bytes": list(header_bytes),
            "Fill Bytes"  : list(fill_bytes),
            "Units offset": unit_offset,
            "Unit type"   : list(unit_t),
            "X"           : list(unit_x),
            "Y"           : list(unit_y),
            "A"           : list(unit_a),
            "B"           : list(unit_b),
            "C"           : list(unit_c),
            "D"           : list(unit_d),
            "H"           : list(unit_h),
            "Map offset"  : map_offset,
            "Map data"    : list(map_data)
        }
        
        return level_dict
        
    except IOError as e:
        print(f"Error loading binary map file '{filepath}': {e} . Exit.")
        sys.exit(1)

# generate the xml for Tiled        
def generate_tmx_file(tile_data, name):

    map_attrib = {
        "version"     : "1.10",
        "tiledversion": "1.11.2",
        "orientation" : "orthogonal",
        "renderorder" : "right-down",
        "width"       : str(MAP_WIDTH),
        "height"      : str(MAP_HEIGHT) ,
        "tilewidth"   : "24",
        "tileheight"  : "24",
        "infinite"    : "0",
        "nextlayerid" : "1",
        "nextobjectid": "1"
    }
    
    if os.path.exists(MERGED_TILES):
        tile_set_bg_attrib = {
            "firstgid"  : "1",
            "name"      : "tiles",
            "tilewidth" : "24",
            "tileheight": "24",
            "tilecount" : "277",
            "columns"   : "1"
        }
    else:
        tile_set_bg_attrib = {
            "firstgid"  : "1",
            "name"      : "tiles",
            "tilewidth" : "24",
            "tileheight": "24",
            "tilecount" : "253",
            "columns"   : "1"
        }
    tile_set_sprites_attrib = {
        "firstgid"  : "301",
        "name"      : "sprites",
        "tilewidth" : "24",
        "tileheight": "24",
        "tilecount" : "83",
        "columns"   : "1"
    }
      
    tile_set_secrets_attrib = {
        "firstgid"  : "401",
        "name"      : "secrets",
        "tilewidth" : "48",
        "tileheight": "21",
        "tilecount" : "6",
        "columns"   : "1",
        "fillmode"  : "preserve-aspect-fit"
    } 
    
    tile_set_keys_attrib = {
        "firstgid"  : "501",
        "name"      : "keys",
        "tilewidth" : "16",
        "tileheight": "14",
        "tilecount" : "3",
        "columns"   : "1"
    } 
    

    if os.path.exists(MERGED_TILES):       
        image_bg_attrib = {
            "source": MERGED_TILES,
            "width" : "32",
            "height": "6448"
        }
    else:
        image_bg_attrib = {
            "source": "tiles/tiles.png",
            "width" : "32",
            "height": "6072"
        }
     
    image_sprites_attrib = {
        "source": "tiles/spritesalpha.png",
        "width" : "24",
        "height": "1992",
        "trans" : "FF00FF"
    }
    
    image_secrets_attrib = {
        "source": "tiles/items.png",
        "width" : "48",
        "height": "126",
        "trans" : "000000"
    }
    
    image_keys_attrib = {
        "source": "tiles/keys.png",
        "width" : "42",
        "height": "16",
        "trans" : "000000"
    }
    
    layer_attrib = {
        "id": "1",
        "name"  : str(name),
        "width" : str(MAP_WIDTH),
        "height": str(MAP_HEIGHT),
    }
    
    data_attrib = {
        "encoding": "csv"
    }    
            
    map_tiles     = [(tile + 1) for tile in level_data['Map data']]
    
    map_elem      = ET.Element("map", map_attrib)
    
    propties_map_elem = ET.SubElement(map_elem, "properties")
    prop_map_attrib = {
            "name" : "File Name",
            "value": str(level_data["File Name"]),
        }
    prop_map_elem = ET.SubElement(propties_map_elem, "property", prop_map_attrib)
    
    prop_map_attrib = {
            "name" : "File Size",
            "value": str(level_data["File Size"]),
        }
    prop_map_elem = ET.SubElement(propties_map_elem, "property", prop_map_attrib)
    
    prop_map_attrib = {
            "name" : "Header bytes",
            "value": str(level_data["Header Bytes"]),
        }
    prop_map_elem = ET.SubElement(propties_map_elem, "property", prop_map_attrib)
    
    prop_map_attrib = {
            "name" : "Fill bytes",
            "value": str(level_data["Fill Bytes"]),
        }
    prop_map_elem = ET.SubElement(propties_map_elem, "property", prop_map_attrib)
    
    prop_map_attrib = {
            "name" : "Unit offset",
            "value": str(level_data["Units offset"]),
        }
    prop_map_elem = ET.SubElement(propties_map_elem, "property", prop_map_attrib)
    
    prop_map_attrib = {
            "name" : "Map offset",
            "value": str(level_data["Map offset"]),
        }
    prop_map_elem = ET.SubElement(propties_map_elem, "property", prop_map_attrib)
    
    
    tile_set_elem = ET.SubElement(map_elem, "tileset", tile_set_bg_attrib)
    image_elem    = ET.SubElement(tile_set_elem, "image", image_bg_attrib) 
    if os.path.exists(MERGED_TILES):
        add_animation( 66, 253, 256, ANIM_DURATION, tile_set_elem) # flag
        add_animation(143, 269, 272, ANIM_DURATION, tile_set_elem) # server
        add_animation(148, 257, 260, ANIM_DURATION, tile_set_elem) # trash compactor
        add_animation(196, 261, 262, ANIM_DURATION, tile_set_elem) # fan
        add_animation(197, 263, 264, ANIM_DURATION, tile_set_elem) # fan
        add_animation(200, 265, 266, ANIM_DURATION, tile_set_elem) # fan
        add_animation(201, 267, 268, ANIM_DURATION, tile_set_elem) # fan
        add_animation(204, 273, 276, ANIM_DURATION, tile_set_elem) # water
        
    
    tile_set_elem = ET.SubElement(map_elem, "tileset", tile_set_sprites_attrib)
    image_elem    = ET.SubElement(tile_set_elem, "image", image_sprites_attrib)
    add_animation( 0,  0, 15, ANIM_DURATION, tile_set_elem) # player
    add_animation(49, 49, 52, ANIM_DURATION, tile_set_elem) # hover bot
    add_animation(53, 53, 56, ANIM_DURATION, tile_set_elem) # roller bot
    add_animation(57, 57, 72, ANIM_DURATION, tile_set_elem) # evil bot
    
    tile_set_elem   = ET.SubElement(map_elem, "tileset", tile_set_secrets_attrib)
    image_elem    = ET.SubElement(tile_set_elem, "image", image_secrets_attrib) 
    
    tile_set_elem = ET.SubElement(map_elem, "tileset", tile_set_keys_attrib)
    image_elem    = ET.SubElement(tile_set_elem, "image", image_keys_attrib) 
    
    layer_elem    = ET.SubElement(map_elem, "layer", layer_attrib)
    data_elem     = ET.SubElement(layer_elem, "data", data_attrib)
    
    data_elem.text = ",".join(map(str, map_tiles))
    
    add_object_groups(1, "Player (1)", map_elem, level_data, 0, 1, 1)
    add_object_groups(2, "Robots (27)", map_elem, level_data, 1, 28, 1)
    add_object_groups(3, "Do not edit (4)", map_elem, level_data, 28, 32, 0)
    add_object_groups(4, "Doors and Transport (16)", map_elem, level_data, 32, 48, 1)
    add_object_groups(5, "Hidden Objects (16)", map_elem, level_data, 48, 64, 1)
    
    return(map_elem)

def add_object_groups(id, name, map_elem, level_data, unit_id_start, unit_id_end, visible):
    # slice the dict
    d = dict(list(level_data.items())[5:13]) # only object relevant lists from dict
    d = {key: value[unit_id_start:unit_id_end] for key, value in d.items()}

    obj_grp_attrib = {
        "id"     : str(id),
        "name"   : str(name),
        "visible": str(visible)
    } 
    obj_grp_elem =  ET.SubElement(map_elem, "objectgroup", obj_grp_attrib)

    for i in range(len(d["Unit type"])):
        unit_type_key = d["Unit type"][i]
        unit_name = unit_types.get(unit_type_key, str(i))  
        labels = ["A", "B", "C", "D", "H"]
        
        # Default GID
        gid = unit_tiles.get(unit_type_key, 0)
        # "Key" SPADE, HEART, STAR
        if unit_type_key == 128:
            a_value = d["A"][i]  # 0 = SPADE, 1 = HEART, 2 = STAR
            key_gid_map = {
                0: 501,  # Tile ID SPADE
                1: 502,  # Tile ID HEART
                2: 503   # Tile ID STAR
            }
            gid = key_gid_map.get(a_value, gid)
            
        if unit_type_key == 10:
            a_value = d["A"][i] 
            door_o_gid_map = {
                0: 82,  # Tile ID Horizontal Door
                1: 73,  # Tile ID Vertical Door
            }
            gid = door_o_gid_map.get(a_value, gid)    
            
        if unit_type_key == 10:
            c_value = d["C"][i] 
            door_k_gid_map = {
                1: 501,  # Tile ID SPADE
                2: 502,  # Tile ID HEART
                3: 503   # Tile ID STAR
            }
            gid = door_k_gid_map.get(c_value, gid)
        
        obj_attrib = {
                "id"    : str(unit_id_start+i),
                "name"  : unit_name,
               #"gid"   : str(unit_tiles.get(d["Unit type"][i], 0)),
                "gid"   : str(gid),
                "x"     : str(d["X"][i]*24),
                # for some reason it has to be +24
                "y"     : str(d["Y"][i]*24+24),
                "width" : "24",
                "height": "24"
        }

        obj_elem = ET.SubElement(obj_grp_elem, "object", obj_attrib)

        propties_elem = ET.SubElement(obj_elem, "properties")
        
        prop_attrib = {
            "name" : "Unit type",
            "value": str(d["Unit type"][i]),
        }
        prop_elem = ET.SubElement(propties_elem, "property", prop_attrib)
               
        prop_attrib = {
            "name" : "X",
            "value": str(d["X"][i]),
        }
        prop_elem = ET.SubElement(propties_elem, "property", prop_attrib)
        
        prop_attrib = {
            "name" : "Y",
            "value": str(d["Y"][i]),
        }
        prop_elem = ET.SubElement(propties_elem, "property", prop_attrib)
        
        attrib_names = unit_attributes.get(unit_type_key, labels)
        
        for j, label in enumerate(labels):
            prop_attrib = {
            "name" : attrib_names[j],
            "value": str(d[label][i]),
            }
            ET.SubElement(propties_elem, "property", prop_attrib) 

def add_animation(id, start_frame, end_frame, duration, tile_set_elem):
    tile_attrib = {
        "id":str(id)
    }
    tile_elem =  ET.SubElement(tile_set_elem, "tile", tile_attrib)
    anim_elem =  ET.SubElement(tile_elem, "animation")
    
    for tile_id in range(start_frame, end_frame + 1):
        frame_attrib = {
            "tileid"  : str(tile_id),
            "duration": str(duration)
        }
        frame_elem = ET.SubElement(anim_elem, "frame", frame_attrib)
        
    #ET.SubElement(tile_elem, "animation")
    #ET.SubElement(tile_set_elem, "tile")
    
#def save_tmx_file(map_elem):
#    tree = ET.ElementTree(map_elem)
#    tree.write(output_file, encoding="UTF-8", xml_declaration=True)

############# Argument parser START
parser = argparse.ArgumentParser(prog = 'lvltiled', 
         description = "Convert level to Tiled TMX.")

#filename is required
parser.add_argument('filename',
                    type = str,
                    help = 'filename of the level to be converted; e.g. level-a')

args = parser.parse_args()
############# Argument parser END


level_data = load_map(args.filename)

map_elem = generate_tmx_file(level_data, args.filename)

rough_string = ET.tostring(map_elem, 'utf-8')
reparsed = xml.dom.minidom.parseString(rough_string)
pretty_xml = reparsed.toprettyxml(indent="  ")
print(pretty_xml)
