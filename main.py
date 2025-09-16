import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    win = MainWindow(title=":JCraft IDE")
    win.run()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
