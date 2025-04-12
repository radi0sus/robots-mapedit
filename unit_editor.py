# unit_editor.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QSpinBox, QComboBox, QGroupBox, QScrollArea, QWidget, QTabWidget
)
from PyQt5.QtCore import Qt
from constants import PLAYER_COLOR, ROBOT_COLOR, DOOR_COLOR, ITEM_COLOR

class UnitTypeInfo:
    """Information about unit types and their properties"""
    
    UNIT_TYPES = {
        #There seem to be special units?
       # 0: "Reserved",
       #93: "Reserved",
        #####
        1: "Player",
        2: "Hoverbot left/right movement",
        3: "Hoverbot up/down movement", 
        4: "Hoverbot /chase attack mode",
        7: "Tranporter Pad",
        9: "Evilbot",
        10: "Doors",
        16: "Trash Compactor",
        17: "Rollerbot up/down movement",
        18: "Rollerbot left/right movement",
        19: "Lift / Elevator",
        22: "Water Raft",
        128: "Key",
        129: "Time Bomb",
        130: "EMP",
        131: "Pistol",
        132: "Charged Plasma Gun",
        133: "Medkit",
        134: "Magnet"
    }
    
    # Property labels based on unit type
    PROPERTIES = {
        # Player
        1: {
            "A": "Unused",
            "B": "Unused",
            "C": "Unused",
            "D": "Unused",
            "H": "Unused"
        },
        # Robots (2,3,4,9,17,18)
        2: {
            "A": "Unused",
            "B": "Unused",
            "C": "Unused",
            "D": "Unused",
            "H": "Health"
        },
         # Transporter Pad (7)
        7: {
            "A": "Activation (0=always active 1=only active when all robots are dead)",
            "B": "Destination (0=completes level 1=send to coordinates)",
            "C": "X-coordinate",
            "D": "Y-coordinate",
            "H": "Unused"
        },
        # Doors (10)
        10: {
            "A": "Orientation (0=horitzonal 1=vertical)",
            "B": "Current State (0=opening-A 1=opening-B 2=OPEN / 3=closing-A 4=closing-B 5-CLOSED)",
            "C": "Locking (0=unlocked / 1=locked spade 2=locked heart 3=locked star)",
            "D": "Unused",
            "H": "Unused"
        },
        # Trash Compactor (16)
        16: {
            "A": "Unused",
            "B": "Unused",
            "C": "Unused",
            "D": "Unused",
            "H": "Unused"
        },
        # Lift / Elevator (19)
        19: {
            "A": "Current State (0=opening-A 1=opening-B 2=OPEN / 3=closing-A 4=closing-B 5-CLOSED)",
            "B": "Which floor corresponds to this unit?",
            "C": "Max number of levels (number should be between 2 and 5)",
            "D": "Unused",
            "H": "Unused"
        },
        # Water Raft (22)
        22: {
            "A": "Current direction (0=left 1=right)",
            "B": "Left-most coordinate",
            "C": "Right-most coordinate",
            "D": "Unused",
            "H": "Unused"
        },
        # Key (128)
        128: {
            "A": "0=SPADE, 1=HEART, 2=STAR",
            "B": "Unused",
            "C": "Extend search area horizontal (between 0 and 127)",
            "D": "Extend search area vertical (between 0 and 63)",
            "H": "Unused"
        },
        # Weapons/Items (129-134)
        129: {
            "A": "Quantity (between 1 and 255)",
            "B": "Unused",
            "C": "Extend search area horizontal (between 0 and 127)",
            "D": "Extend search area vertical (between 0 and 63)",
            "H": "Unused"
        }
    }
    
    @staticmethod
    def get_type_name(type_id):
        """Get name for a unit type ID"""
        return UnitTypeInfo.UNIT_TYPES.get(type_id, f"Unknown ({type_id})")
    
    @staticmethod
    def get_property_label(type_id, prop):
        """Get label for a property based on unit type"""
        # First check for exact type match
        if type_id in UnitTypeInfo.PROPERTIES:
            return UnitTypeInfo.PROPERTIES[type_id].get(prop, prop)
        
        # Then check for type range
        if 2 <= type_id <= 4 or type_id == 9 or 17 <= type_id <= 18:  # Robots
            return UnitTypeInfo.PROPERTIES[2].get(prop, prop)
        elif type_id == 7:  # Transporter Pad
            return UnitTypeInfo.PROPERTIES[7].get(prop, prop)
        elif type_id == 10:  # Doors
            return UnitTypeInfo.PROPERTIES[10].get(prop, prop)
        elif type_id == 16:  # Trash Compactor
            return UnitTypeInfo.PROPERTIES[16].get(prop, prop)
        elif type_id == 19:  # Elevator
            return UnitTypeInfo.PROPERTIES[19].get(prop, prop)
        elif type_id == 22:  # Water Raft
            return UnitTypeInfo.PROPERTIES[22].get(prop, prop)
        elif 128 <= type_id <= 134:  # Items
            if type_id == 128:  # Key
                return UnitTypeInfo.PROPERTIES[128].get(prop, prop)
            else:  # Weapons and other items
                return UnitTypeInfo.PROPERTIES[129].get(prop, prop)
        
        # Default
        return prop
    
    @staticmethod
    def get_unit_color(unit_id, unit_type):
        """Get color for a unit based on its ID and type"""
        if unit_type == 1:  # Player
            return PLAYER_COLOR
        elif 3 <= unit_id <= 3 + 26:  # Robots
            return ROBOT_COLOR
        elif 34 <= unit_id <= 34 + 15:  # Doors
            return DOOR_COLOR
        elif 50 <= unit_id <= 50 + 15:  # Items
            return ITEM_COLOR
        return "gray"  # Default


#    @staticmethod
#    def get_unit_color(unit_id, unit_type):
#        """Get color for a unit based on its ID and type"""
#        if unit_type == 1:  # Player
#            return PLAYER_COLOR
#        elif 2 <= unit_type <= 4 or unit_type == 9 or 17 <= unit_type <= 18:  # Robots
#            return ROBOT_COLOR
#        elif unit_type == 7 or unit_type == 10 or unit_type == 16 or unit_type == 19 or unit_type == 22:  # Doors
#            return DOOR_COLOR
#        elif 128 <= unit_type <= 134:  # Items
#            return ITEM_COLOR
#        return "gray"  # Default

class UnitEditor(QDialog):
    """Dialog for adding and editing units"""
    
    def __init__(self, parent, map_data):
        super().__init__(parent)
        self.parent = parent
        self.map_data = map_data
        self.unit_positions = map_data.unit_positions
        self.current_unit_id = None
        
        self.setWindowTitle("Unit Editor")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
        self.populate_unit_list()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create tabs
        self.tabs = QTabWidget()
        self.unit_tab = QWidget()
        self.add_tab = QWidget()
        
        self.tabs.addTab(self.unit_tab, "Edit Units")
        self.tabs.addTab(self.add_tab, "Add Unit")
        
        # Initialize both tabs
        self.init_unit_tab()
        self.init_add_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def init_unit_tab(self):
        """Initialize the unit editing tab"""
        layout = QVBoxLayout()
        
        # Unit list
        self.unit_scroll = QScrollArea()
        self.unit_scroll.setWidgetResizable(True)
        self.unit_list_widget = QWidget()
        self.unit_list_layout = QVBoxLayout(self.unit_list_widget)
        self.unit_scroll.setWidget(self.unit_list_widget)
        
        # Unit editor panel
        self.unit_editor_widget = QGroupBox("Unit Properties")
        unit_editor_layout = QGridLayout()
        
        # Position
        unit_editor_layout.addWidget(QLabel("X:"), 0, 0)
        self.unit_x_spin = QSpinBox()
        self.unit_x_spin.setRange(0, 127)
        unit_editor_layout.addWidget(self.unit_x_spin, 0, 1)
        
        unit_editor_layout.addWidget(QLabel("Y:"), 0, 2)
        self.unit_y_spin = QSpinBox()
        self.unit_y_spin.setRange(0, 63)
        unit_editor_layout.addWidget(self.unit_y_spin, 0, 3)
        
        # Type
        unit_editor_layout.addWidget(QLabel("Type:"), 1, 0)
        self.unit_type_combo = QComboBox()
        for type_id, type_name in UnitTypeInfo.UNIT_TYPES.items():
            self.unit_type_combo.addItem(f"{type_name} ({type_id})", type_id)
        self.unit_type_combo.currentIndexChanged.connect(self.on_unit_type_changed)
        unit_editor_layout.addWidget(self.unit_type_combo, 1, 1, 1, 3)
        
        # Properties
        labels = ["A:", "B:", "C:", "D:", "Health:"]
        self.prop_labels = []
        self.prop_spins = []
        
        for i, label_text in enumerate(labels):
            row = i + 2
            label = QLabel(label_text)
            self.prop_labels.append(label)
            unit_editor_layout.addWidget(label, row, 0)
            
            spin = QSpinBox()
            spin.setRange(0, 255)
            self.prop_spins.append(spin)
            unit_editor_layout.addWidget(spin, row, 1, 1, 3)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_unit)
        self.delete_button = QPushButton("Delete Unit")
        self.delete_button.clicked.connect(self.delete_unit)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        
        self.unit_editor_widget.setLayout(unit_editor_layout)
        self.unit_editor_widget.setEnabled(False)
        
        # Add widgets to layout
        layout.addWidget(self.unit_scroll)
        layout.addWidget(self.unit_editor_widget)
        layout.addLayout(button_layout)
        
        self.unit_tab.setLayout(layout)
    
    def init_add_tab(self):
        """Initialize the add unit tab"""
        layout = QVBoxLayout()
        
        group = QGroupBox("New Unit")
        group_layout = QGridLayout()
        
        # Unit ID
        group_layout.addWidget(QLabel("Unit ID:"), 0, 0)
        self.new_id_spin = QSpinBox()
        self.new_id_spin.setRange(0, 63)
        group_layout.addWidget(self.new_id_spin, 0, 1)
        
        # Position
        group_layout.addWidget(QLabel("X:"), 1, 0)
        self.new_x_spin = QSpinBox()
        self.new_x_spin.setRange(0, 127)
        group_layout.addWidget(self.new_x_spin, 1, 1)
        
        group_layout.addWidget(QLabel("Y:"), 2, 0)
        self.new_y_spin = QSpinBox()
        self.new_y_spin.setRange(0, 63)
        group_layout.addWidget(self.new_y_spin, 2, 1)

               
        # Type
        group_layout.addWidget(QLabel("Type:"), 3, 0)
        self.new_type_combo = QComboBox()
        for type_id, type_name in UnitTypeInfo.UNIT_TYPES.items():
            self.new_type_combo.addItem(f"{type_name} ({type_id})", type_id)
        self.new_type_combo.currentIndexChanged.connect(self.on_unit_type_changed) # added
        group_layout.addWidget(self.new_type_combo, 3, 1)
        
        # Properties
        labels = ["A:", "B:", "C:", "D:", "Health:"]
        self.new_prop_labels = []  #added
        self.new_prop_spins = []
        
        for i, label_text in enumerate(labels):
            row = i + 4
            #group_layout.addWidget(QLabel(label_text), row, 0) # commented
            label = QLabel(label_text) # added
            self.new_prop_labels.append(label) # added
            group_layout.addWidget(label, row, 0) # added
            
            spin = QSpinBox()
            spin.setRange(0, 255)
            self.new_prop_spins.append(spin)
            group_layout.addWidget(spin, row, 1)
        
        # Add unit button
        self.add_unit_button = QPushButton("Add Unit")
        self.add_unit_button.clicked.connect(self.add_unit)
        
        group.setLayout(group_layout)
        
        # Add widgets to layout
        layout.addWidget(group)
        layout.addWidget(self.add_unit_button)
        layout.addStretch()
        
        self.add_tab.setLayout(layout)
    
    def populate_unit_list(self):
        """Fill the unit list with current units"""
        # Clear existing items
        while self.unit_list_layout.count():
            item = self.unit_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Add each unit as a selectable button
        for unit_id in sorted(self.unit_positions.keys()):
            x, y, unit_type, a, b, c, d, h = self.unit_positions[unit_id]
            type_name = UnitTypeInfo.get_type_name(unit_type)
            
            unit_button = QPushButton(f"Unit ID {unit_id}: {type_name} ({unit_type}) at ({x},{y})")
            unit_button.setStyleSheet(f"text-align: left; border: 1px solid {UnitTypeInfo.get_unit_color(unit_id, unit_type)};")
            unit_button.clicked.connect(lambda checked, uid=unit_id: self.select_unit(uid))
            
            self.unit_list_layout.addWidget(unit_button)
        
        # Add stretch to push all items to the top
        self.unit_list_layout.addStretch()
    
    def select_unit(self, unit_id):
        """Select a unit and show its properties"""
        if unit_id in self.unit_positions:
            self.current_unit_id = unit_id
            x, y, unit_type, a, b, c, d, h = self.unit_positions[unit_id]
            
            # Populate form fields
            self.unit_x_spin.setValue(x)
            self.unit_y_spin.setValue(y)
            
            # Find and select the type in the combo box
            for i in range(self.unit_type_combo.count()):
                if self.unit_type_combo.itemData(i) == unit_type:
                    self.unit_type_combo.setCurrentIndex(i)
                    break
            
            # Update property labels based on unit type
            self.update_property_labels(unit_type)
            
            # Set property values
            props = [a, b, c, d, h]
            for i, spin in enumerate(self.prop_spins):
                spin.setValue(props[i])
            
            # Enable the editor panel
            self.unit_editor_widget.setEnabled(True)
    
#   def on_unit_type_changed(self):
#        """Update property labels when unit type changes"""
#        type_id = self.unit_type_combo.currentData()
#        self.update_property_labels(type_id)
    def on_unit_type_changed(self):
        """Update property labels when unit type changes"""
        # Determine which tab is active
        current_tab_index = self.tabs.currentIndex()
        
        if current_tab_index == 0:  # Edit Units tab
            type_id = self.unit_type_combo.currentData()
            self.update_property_labels(type_id)
        else:  # Add Unit tab
            type_id = self.new_type_combo.currentData()
            self.update_property_labels(type_id)
            
    def update_property_labels(self, type_id):
        """Update property labels based on unit type"""
        props = ["A", "B", "C", "D", "H"]
        
        current_tab_index = self.tabs.currentIndex() # added
        
        #for i, prop in enumerate(props):
        #    label = UnitTypeInfo.get_property_label(type_id, prop)
        #    self.prop_labels[i].setText(f"{label}:")
        # all added from here
        if current_tab_index == 0: # Edit Units tab
            for i, prop in enumerate(props):
                label = UnitTypeInfo.get_property_label(type_id, prop)
                self.prop_labels[i].setText(f"{label}:")

        else:  # Add Unit tab
            for i, prop in enumerate(props):
                label = UnitTypeInfo.get_property_label(type_id, prop)
                self.new_prop_labels[i].setText(f"{label}:")

                
    def save_unit(self):
        """Save changes to the current unit"""
        if self.current_unit_id is None:
            return
        
        # Get updated values
        x = self.unit_x_spin.value()
        y = self.unit_y_spin.value()
        unit_type = self.unit_type_combo.currentData()
        
        # Get properties
        a = self.prop_spins[0].value()
        b = self.prop_spins[1].value()
        c = self.prop_spins[2].value()
        d = self.prop_spins[3].value()
        h = self.prop_spins[4].value()
        
        # Update unit data
        self.unit_positions[self.current_unit_id] = (x, y, unit_type, a, b, c, d, h)
        
        # Special case for player (unit 0)
        if unit_type == 1:  # Player
            # Always assign player to unit 0
            self.unit_positions[0] = (x, y, unit_type, a, b, c, d, h)
        
        # Refresh the unit list
        self.populate_unit_list()
        
        # Update the map display
        self.parent.update_map_display()
    
    def delete_unit(self):
        """Delete the current unit"""
        if self.current_unit_id is None:
            return
        
        # Don't allow deleting unit 0 (player)
        if self.current_unit_id == 0:
            return
        
        # Remove the unit
        if self.current_unit_id in self.unit_positions:
            del self.unit_positions[self.current_unit_id]
        
        # Clear current selection
        self.current_unit_id = None
        self.unit_editor_widget.setEnabled(False)
        
        # Refresh the unit list
        self.populate_unit_list()
        
        # Update the map display
        self.parent.update_map_display()
    
    def add_unit(self):
        """Add a new unit with the specified properties"""
        # Get values from the form
        unit_id = self.new_id_spin.value()
        x = self.new_x_spin.value()
        y = self.new_y_spin.value()
        unit_type = self.new_type_combo.currentData()
        
        # Get properties
        a = self.new_prop_spins[0].value()
        b = self.new_prop_spins[1].value()
        c = self.new_prop_spins[2].value()
        d = self.new_prop_spins[3].value()
        h = self.new_prop_spins[4].value()
        
        # Add the unit
        self.unit_positions[unit_id] = (x, y, unit_type, a, b, c, d, h)
        
        # Special case for player (type 1)
        if unit_type == 1:  # Player
            # Always assign player to unit 0
            self.unit_positions[0] = (x, y, unit_type, a, b, c, d, h)
        
        # Refresh the unit list and switch to the edit tab
        self.populate_unit_list()
        self.tabs.setCurrentIndex(0)  # Switch to edit tab
        
        # Update the map display
        self.parent.update_map_display()
