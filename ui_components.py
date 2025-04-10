from PyQt5.QtWidgets import QLabel, QScrollArea
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt

from constants import TILE_SIZE, GRID_COLOR, SELECTION_COLOR
from constants import PLAYER_COLOR, ROBOT_COLOR, DOOR_COLOR, ITEM_COLOR

class TilesetPaletteWidget(QLabel):
    """Widget showing the available tiles that can be selected"""
    
    def __init__(self, cols=16, parent=None):
        super().__init__(parent)
        self.cols = cols
        self.selected_tile = 0
        self.tile_size = TILE_SIZE
        self.tiles = []
    
    def update_palette(self, tiles):
        """Update the palette with new tiles"""
        self.tiles = tiles
        rows = max(1, (len(tiles) + self.cols - 1) // self.cols)  # Ceiling division
        
        # Create image to draw on
        image = QImage(self.cols * self.tile_size, rows * self.tile_size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        
        # Draw all tiles
        for i, tile in enumerate(self.tiles):
            if i >= self.cols * rows:
                break
                
            x = (i % self.cols) * self.tile_size
            y = (i // self.cols) * self.tile_size
            
            # Draw tile
            painter.drawPixmap(x, y, tile)
            
            # Draw selection box around selected tile
            if i == self.selected_tile:
                painter.setPen(QColor(SELECTION_COLOR))
                painter.drawRect(x, y, self.tile_size - 1, self.tile_size - 1)
        
        painter.end()
        
        # Update widget
        self.setPixmap(QPixmap.fromImage(image))
        self.setFixedSize(self.cols * self.tile_size, rows * self.tile_size)
    
    def set_selected_tile(self, index):
        """Set the selected tile by index"""
        if 0 <= index < len(self.tiles):
            self.selected_tile = index
            self.update_palette(self.tiles)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks to select tiles"""
        x = event.pos().x() // self.tile_size
        y = event.pos().y() // self.tile_size
        index = y * self.cols + x
        
        if 0 <= index < len(self.tiles):
            self.selected_tile = index
            self.update_palette(self.tiles)
            
            # Notify parent of selection change
            if hasattr(self.parent(), "on_tile_selected"):
                self.parent().on_tile_selected(index)


class MapCanvasWidget(QLabel):
    """Widget showing the map with tiles and units"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_editor = parent  
        self.tile_size = TILE_SIZE
        self.window_x = 0  # View window position
        self.window_y = 0
        self.window_width = 0
        self.window_height = 0
        self.setMouseTracking(True)
        self.show_unit_overlay = True
        
    # Add the new helper methods here, right after __init__
    def draw_filled_rectangle_with_border(self, painter, x, y, width, height, fill_color, border_color, alpha=128):
        """Draw a rectangle with semi-transparent fill and border"""
        # Set up semi-transparent fill color
        fill = QColor(fill_color)
        fill.setAlpha(alpha)
        
        # Fill the rectangle
        painter.fillRect(x, y, width, height, fill)
        
        # Draw the border
        painter.setPen(QColor(border_color))
        painter.drawRect(x, y, width, height)

    def draw_filled_ellipse_with_border(self, painter, x, y, width, height, fill_color, border_color, alpha=128):
        """Draw an ellipse with semi-transparent fill and border"""
        # Save current brush and pen
        old_brush = painter.brush()
        old_pen = painter.pen()
        
        # Set up semi-transparent fill
        fill = QColor(fill_color)
        fill.setAlpha(alpha)
        painter.setBrush(fill)
        
        # Set up border
        painter.setPen(QColor(border_color))
        
        # Draw the ellipse
        painter.drawEllipse(x, y, width, height)
        
        # Restore original brush and pen
        painter.setBrush(old_brush)
        painter.setPen(old_pen)
    
    def draw_centered_text(self, painter, x, y, width, height, text, text_color=Qt.white, font_size_adjustment=0):
        """Draw text centered in the given rectangle with the specified styling
        
        Args:
            painter: QPainter object
            x, y: Top-left corner of the rectangle to center text in
            width, height: Dimensions of the rectangle
            text: Text to display
            text_color: Color for the text (default: white)
            font_size_adjustment: Adjustment to font size (default: -2)
        """
        # Save original font
        original_font = painter.font()
        
        # Create a smaller font
        smaller_font = QFont(original_font)
        if font_size_adjustment != 0:
            smaller_font.setPointSize(max(6, original_font.pointSize() + font_size_adjustment))
        
        # Apply the font
        painter.setFont(smaller_font)
        
        # Set text color
        painter.setPen(text_color)
        
        # Calculate centered position
        text_width = painter.fontMetrics().horizontalAdvance(text)
        text_height = painter.fontMetrics().height()
        
        text_x = x + (width - text_width) / 2
        text_y = y + (height + text_height) / 2 - 2  # -2 for visual adjustment
        
        # Draw the text
        painter.drawText(int(text_x), int(text_y), text)
        
        # Restore original font
        painter.setFont(original_font)
    
    def contextMenuEvent(self, event):
        """Show context menu when right-clicking on the map"""
        # Get map coordinates from screen position
        x = event.pos().x() // self.tile_size + self.window_x
        y = event.pos().y() // self.tile_size + self.window_y
        
        from PyQt5.QtWidgets import QMenu, QAction
        
        # Create context menu
        menu = QMenu(self)
        add_unit_action = QAction(f"Add Unit at ({x},{y})", self)
        add_unit_action.triggered.connect(lambda: self.place_unit_at(x, y))
        menu.addAction(add_unit_action)
        
        # Show menu
        menu.exec_(event.globalPos())

    def place_unit_at(self, x, y):
        """Open unit editor to place a unit at specific coordinates"""
        from unit_editor import UnitEditor
        
        editor = UnitEditor(self.parent_editor, self.parent_editor.map_data)
        
        # Set coordinates in Add Unit tab
        editor.new_x_spin.setValue(x)
        editor.new_y_spin.setValue(y)
        
        # Switch to Add Unit tab
        editor.tabs.setCurrentIndex(1)
        
        # Show the dialog
        editor.exec_()
        
        # Update the map display
        self.parent_editor.update_map_display()    
    
    def update_canvas(self, map_data, tile_manager, unit_positions, anim_state, show_animations, show_unit_overlay):
        """Redraw the map with current tiles and units"""
        # Set the size based on the visible window
        width = self.window_width
        height = self.window_height
        
        self.setFixedSize(width * self.tile_size, height * self.tile_size)
        image = QImage(width * self.tile_size, height * self.tile_size, QImage.Format_ARGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        
        # Draw tiles
        for y in range(height):
            map_y = y + self.window_y
            if map_y >= len(map_data):
                continue

            for x in range(width):
                map_x = x + self.window_x
                if map_x >= len(map_data[0]):
                    continue

                # Get tile ID at this position
                tile_id = map_data[map_y][map_x]
                if tile_id != -1:
                    # Get the pixmap for this tile (considering animation)
                    pixmap = tile_manager.get_tile_pixmap(tile_id, anim_state, show_animations)
                    if pixmap:
                        painter.drawPixmap(x * self.tile_size, y * self.tile_size, pixmap)
        
        # Draw grid
        painter.setPen(QColor(*GRID_COLOR))
        for x in range(width + 1):
            painter.drawLine(x * self.tile_size, 0, x * self.tile_size, height * self.tile_size)
        for y in range(height + 1):
            painter.drawLine(0, y * self.tile_size, width * self.tile_size, y * self.tile_size)
        
        # Draw units
        self._draw_units(painter, unit_positions)
        
        painter.end()
        self.setPixmap(QPixmap.fromImage(image))
    
    def _draw_units(self, painter, unit_positions):
        """Draw an overlay showing unit positions"""
        if not self.show_unit_overlay:
            return
        for unit_id, (x, y, unit_type, a, b, c, d, h) in unit_positions.items():
            # Adjust for the view window position
            screen_x = (x - self.window_x) * self.tile_size
            screen_y = (y - self.window_y) * self.tile_size
            
            # Skip if outside current view
            if (screen_x < 0 or screen_y < 0 or 
                screen_x >= self.window_width * self.tile_size or 
                screen_y >= self.window_height * self.tile_size):
                continue
            
            # Different styles for different unit types
            if unit_type == 1:  # Player
                fill_color = QColor(PLAYER_COLOR)  
                fill_color.setAlpha(128)
                painter.fillRect(screen_x + 2, screen_y + 2, 
                                self.tile_size - 4, self.tile_size - 4, fill_color)
                self.draw_centered_text(
                painter,
                screen_x, screen_y,
                self.tile_size, self.tile_size, f"P{unit_id}-{unit_type}") 
                #painter.drawText(screen_x + 5 + 17, screen_y + 16, f"P{unit_id}-{unit_type}")
            elif 3 <= unit_id <= 27:  # Robots
                #painter.setPen(QColor(ROBOT_COLOR))
                fill_color = QColor(ROBOT_COLOR)  
                fill_color.setAlpha(128)
                painter.fillRect(screen_x + 2, screen_y + 2, 
                                self.tile_size - 4, self.tile_size - 4, fill_color)
                self.draw_centered_text(
                painter,
                screen_x, screen_y,
                self.tile_size, self.tile_size, f"R{unit_id}-{unit_type}") 
                #painter.drawText(screen_x + 5 + 17, screen_y + 16, f"R{unit_id-3}-{unit_type}")
            elif 32 <= unit_id <= 47:  # Doors
                #painter.setPen(QColor(DOOR_COLOR))
                fill_color = QColor(DOOR_COLOR)  
                fill_color.setAlpha(128)
                painter.fillRect(screen_x + 2, screen_y + 2, 
                                self.tile_size - 4, self.tile_size - 4, fill_color)
                self.draw_centered_text(
                painter,
                screen_x, screen_y,
                self.tile_size, self.tile_size, f"D{unit_id}-{unit_type}-{c}") 
            elif 48 <= unit_id <= 63:  # Items
                #painter.setPen(QColor(ITEM_COLOR))
                #painter.drawEllipse(screen_x + 4, screen_y + 4, 
                #                  self.tile_size - 8, self.tile_size - 8)
                fill_color = QColor(ITEM_COLOR)  
                fill_color.setAlpha(128)
                painter.fillRect(screen_x + 2, screen_y + 2, 
                                self.tile_size - 4, self.tile_size - 4, fill_color)
                if unit_type == 128:
                # if key
                     self.draw_centered_text(
                    painter,
                    screen_x, screen_y,
                    self.tile_size, self.tile_size, f"I{unit_id}-{unit_type}-{a}")
                elif 128 < unit_type <= 134:
                # if weapon or item
                    self.draw_centered_text(
                    painter,
                    screen_x, screen_y,
                    self.tile_size, self.tile_size, f"I{unit_id}-{unit_type}-{a}")
                else:
                    self.draw_centered_text(
                    painter,
                    screen_x, screen_y,
                    self.tile_size, self.tile_size, f"I{unit_id}-{unit_type}")
                
                                
                #painter.drawText(screen_x + 5, screen_y + 16, f"I{unit_id-51}-{unit_type}")
    
    #def mousePressEvent(self, event):
    #    """Handle mouse press for painting tiles"""
    #    if hasattr(self.parent(), "handle_canvas_click"):
    #        self.parent().handle_canvas_click(event)
    #def mousePressEvent(self, event):
    #    """Handle mouse press for painting tiles"""
    #    #if hasattr(self.parent(), "handle_canvas_click"):
    #    #    self.parent().handle_canvas_click(event)
    #    # Add direct call to make sure it's invoked
    #    if hasattr(self.parent_editor, "handle_canvas_click"):
    #        self.parent_editor.handle_canvas_click(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for drag painting and position display"""
        #if hasattr(self.parent(), "handle_canvas_move"):
        #    self.parent().handle_canvas_move(event)
        if hasattr(self.parent_editor, "handle_canvas_move"):
            self.parent_editor.handle_canvas_move(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for painting tiles and picking"""
        if event.button() == Qt.RightButton:
            # Middle button: pick tile at this position
            x = event.pos().x() // self.tile_size + self.window_x
            y = event.pos().y() // self.tile_size + self.window_y
            
            # Pick the tile at this location
            if 0 <= x < 128 and 0 <= y < 64:
                tile_id = self.parent_editor.map_data.get_tile(x, y)
                if tile_id != -1:
                    # Set as selected tile in palette
                    self.parent_editor.palette.set_selected_tile(tile_id)
        else:
            # Let parent handle left button for tile placement
            if hasattr(self.parent_editor, "handle_canvas_click"):
                self.parent_editor.handle_canvas_click(event)
                
   # def mouseMoveEvent(self, event):
   #     """Handle mouse movement for drag painting and position display"""
   #     if hasattr(self.parent_editor, "handle_canvas_move"):
   #         self.parent_editor.handle_canvas_move(event)
