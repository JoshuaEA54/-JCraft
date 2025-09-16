from pathlib import Path
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap

class Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel(self)
        self.label.setScaledContents(True)

    def set_image(self, path: Path):
        pm = QPixmap(str(path))
        if not pm.isNull():
            self.label.setPixmap(pm)

    def resizeEvent(self, e):
        self.label.setGeometry(self.rect())
        super().resizeEvent(e)
