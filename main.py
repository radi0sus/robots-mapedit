#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from tilemap_editor import TileMapEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TileMapEditor()
    editor.show()
    sys.exit(app.exec_())
