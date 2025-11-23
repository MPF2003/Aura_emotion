# main.py
from interface import AuraInterface
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AuraInterface()
    gui.show()
    sys.exit(app.exec())
