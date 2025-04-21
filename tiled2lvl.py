import xml.etree.ElementTree as ET
import ast
import argparse
import sys



tree = ET.parse('test.tmx')
rob_lvl = tree.getroot()
rob_lvl_propties = rob_lvl.find("properties")


def tmx_to_level_dict(tmx_file):

    level_dict = {}

    for prop in rob_lvl_propties.iter("property"):
        if prop.get("name") != "File Name":
            level_dict.update({prop.get("name"):ast.literal_eval(prop.get("value"))})
        else:
            level_dict.update({prop.get("name"):prop.get("value")})
            
    tile_list = list(map(int, rob_lvl.find("layer").find("data").text.strip().split(',')))
    tile_list = [tile -1 for tile in tile_list]
    level_dict.update({"Map Data":tile_list})
    
    # check number of units in each category
    player_group   = rob_lvl.find(".//objectgroup[@name='Player']")
    robots_group   = rob_lvl.find(".//objectgroup[@name='Robots']")
    not_edit_group = rob_lvl.find(".//objectgroup[@name='Do not edit']")
    doors_group    = rob_lvl.find(".//objectgroup[@name='Doors and Transport']")
    hidden_group   = rob_lvl.find(".//objectgroup[@name='Hidden Objects']")
    
    size_player_group   = len(player_group.findall("object"))
    size_robots_group   = len(robots_group.findall("object"))
    size_not_edit_group = len(not_edit_group.findall("object"))
    size_doors_group    = len(doors_group.findall("object"))
    size_hidden_group   = len(hidden_group.findall("object"))
    
    if size_player_group != 1:
        print(f"\nWarning! Player count is {size_player_group}, must be 1.")
    else:
        print(f"Player count: {size_player_group}")
    if size_robots_group != 27:
        print(f"\nWarning! Robots count is {size_robots_group}, must be 27.")
    else:
        print(f"Robots count: {size_robots_group}")
    if size_not_edit_group != 4:
        print(f"\nWarning! 'Not edit' count is {size_not_edit_group}, must be 4.")
    else:
        print(f"'Not edit' count: {size_not_edit_group}")
    if size_doors_group != 16:
        print(f"\nWarning! Doors and transport count is {size_doors_group}, must be 16.")
    else:
        print(f"Doors and transport count: {size_doors_group}")
    if size_hidden_group != 16:
        print(f"\nWarning! Hidden objects count is {size_hidden_group}, must be 16.")
    else:
        print(f"Hidden objects count: {size_hidden_group}")
    
    Unit_type = [int(prop.attrib["value"])
                  for prop in rob_lvl.findall(".//property[@name='Unit type']")]
    X_coords  = [int(obj.attrib["x"]) for obj in rob_lvl.findall(".//object")]
    Y_coords  = [int(obj.attrib["y"]) for obj in rob_lvl.findall(".//object")]
    
    X_coords = [x // 24 if x != 0 else 0 for x in X_coords]
    Y_coords = [(y - 24) // 24 if y != 0 else 0 for y in Y_coords]
    
    Unit_type = [int(prop.attrib["value"])
                  for prop in rob_lvl.findall(".//property[@name='Unit type']")]
    
    A_values = []
    B_values = []
    C_values = []
    D_values = []
    H_values = []
    
    for obj in rob_lvl.findall(".//object"):
        props = obj.find("properties")
        prop_list = props.findall("property")
        A_values.append(int(prop_list[3].attrib["value"]))  # A
        B_values.append(int(prop_list[4].attrib["value"]))  # B
        C_values.append(int(prop_list[5].attrib["value"]))  # C
        D_values.append(int(prop_list[6].attrib["value"]))  # D
        H_values.append(int(prop_list[7].attrib["value"]))  # H
        
    level_dict.update({"Unit type":Unit_type})
    level_dict.update({"Y":Y_coords})
    level_dict.update({"X":X_coords})
    level_dict.update({"A":A_values})
    level_dict.update({"B":B_values})
    level_dict.update({"C":C_values})
    level_dict.update({"D":D_values})
    level_dict.update({"H":H_values})
    
    return level_dict

def load_tiled_map(filename = "level-a.tmx"):
    try:
        with open(filename, 'r') as f:
            level_data = f.read()
        return level_data
        
    except IOError as e:
        print(f"Error loading binary map file '{filename}': {e} . Exit.")
        sys.exit(1)

def save_robots_lvl(level_dict):
    filename = level_dict["File Name"]
    
    binary_data = bytes(
    level_dict['Header bytes'] +
    level_dict['Unit type'] +
    level_dict['X'] +
    level_dict['Y'] +
    level_dict['A'] +
    level_dict['B'] +
    level_dict['C'] +
    level_dict['D'] +
    level_dict['H'] +
    level_dict['Fill bytes'] +
    level_dict['Map Data']
    )
    
    #print(len(level_dict['Header bytes'])) 
    #print(len(level_dict['Unit type']))
    #print(len(level_dict['X']))
    #print(len(level_dict['Y']))
    #print(len(level_dict['A']))
    #print(len(level_dict['B']))
    #print(len(level_dict['C']))
    #print(len(level_dict['D']))
    #print(len(level_dict['H']))
    #print(len(level_dict['Fill bytes']))
    #print(len(level_dict['Map Data']))
    
    if len(binary_data) != level_dict["File Size"]:
        print(f"Warning! Calculated file size: {len(binary_data)} "
              f"is different from expected file size: {level_dict['File Size']}! Exit.")
        sys.exit(1)
    else:
        print(f"File size: {len(binary_data)}")
        
    try:
        with open(f"{filename}.lvl", "wb") as f:
            level_data = f.write(binary_data)
        print(f"{filename}.lvl saved.")
    except IOError as e:
        print(f"Error writing binary map file '{filename}'.lvl: {e} . Exit.")
        sys.exit(1)

############# Argument parser START
parser = argparse.ArgumentParser(prog = 'tiled2lvl', 
         description = "Convert Tiled TMX to level.")

#filename is required
parser.add_argument('filename',
                    type = str,
                    help = 'filename of the level to be converted; e.g. level-a.tmx')

args = parser.parse_args()
############# Argument parser END

tmx_map_data = load_tiled_map(args.filename)
level_dict = tmx_to_level_dict(tmx_map_data)
save_robots_lvl(level_dict)
