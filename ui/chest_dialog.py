from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRect


class ChestWidget(QWidget):
    """Custom widget that draws a Minecraft-style chest"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 280)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # Pixelated style
        
        # Define colors (Minecraft chest browns and grays)
        dark_brown = QColor(89, 63, 38)      # Dark borders
        medium_brown = QColor(139, 97, 60)   # Medium wood
        light_brown = QColor(170, 123, 77)   # Light wood
        gray = QColor(140, 140, 140)         # Lock/latch metal
        dark_gray = QColor(80, 80, 80)       # Lock shadow
        
        # Main chest body - top half
        painter.fillRect(50, 40, 300, 100, medium_brown)
        
        # Main chest body - bottom half
        painter.fillRect(50, 140, 300, 100, light_brown)
        
        # Dark borders
        painter.setPen(QPen(dark_brown, 8))
        painter.drawRect(50, 40, 300, 100)   # Top half border
        painter.drawRect(50, 140, 300, 100)  # Bottom half border
        
        # Draw wood planks texture (horizontal lines)
        painter.setPen(QPen(dark_brown, 2))
        for i in range(5):
            y = 60 + i * 20
            painter.drawLine(60, y, 340, y)
        for i in range(5):
            y = 160 + i * 20
            painter.drawLine(60, y, 340, y)
        
        # Draw vertical wood grain
        painter.setPen(QPen(dark_brown, 1))
        for i in range(15):
            x = 70 + i * 20
            painter.drawLine(x, 45, x, 135)
            painter.drawLine(x, 145, x, 235)
        
        # Lock/Latch in the middle (where chest opens)
        lock_x = 185
        lock_y = 120
        
        # Lock shadow
        painter.fillRect(lock_x + 2, lock_y + 2, 30, 40, dark_gray)
        
        # Lock body
        painter.fillRect(lock_x, lock_y, 30, 40, gray)
        
        # Lock border
        painter.setPen(QPen(dark_brown, 2))
        painter.drawRect(lock_x, lock_y, 30, 40)
        
        # Lock keyhole
        painter.fillRect(lock_x + 11, lock_y + 15, 8, 12, dark_gray)
        
        # Outer frame (darker)
        painter.setPen(QPen(dark_brown, 12))
        painter.drawRect(46, 36, 308, 208)


class ChestDialog(QDialog):
    """Custom Minecraft-style chest dialog for input"""
    def __init__(self, prompt: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cofre - JCraft")
        self.setModal(True)
        self.setFixedSize(450, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Prompt label
        self.prompt_label = QLabel(prompt if prompt else "Ingrese un valor:")
        self.prompt_label.setAlignment(Qt.AlignCenter)
        self.prompt_label.setStyleSheet("""
            QLabel {
                color: #E8EEF2;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                background: rgba(89, 63, 38, 0.3);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.prompt_label)
        
        # Chest widget
        self.chest_widget = ChestWidget(self)
        layout.addWidget(self.chest_widget, alignment=Qt.AlignCenter)
        
        # Input field (styled like a Minecraft text field)
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Escribe aquí...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: #3A2819;
                border: 3px solid #593F26;
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                color: #E8EEF2;
                selection-background-color: #8B6139;
                selection-color: #FFF;
            }
            QLineEdit:focus {
                border: 3px solid #AA7B4D;
            }
        """)
        layout.addWidget(self.input_field)
        
        # OK Button (Minecraft style)
        self.ok_button = QPushButton("ABRIR COFRE", self)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: #8B6139;
                border: 3px solid #593F26;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
                color: #FFF;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: #AA7B4D;
                border: 3px solid #6B4F36;
            }
            QPushButton:pressed {
                background: #6B4F36;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        
        # Dialog background
        self.setStyleSheet("""
            QDialog {
                background: #1A1410;
            }
        """)
        
        # Focus on input field
        self.input_field.setFocus()
        
        # Allow Enter key to submit
        self.input_field.returnPressed.connect(self.accept)
    
    def get_input(self) -> str:
        """Get the text entered by the user"""
        return self.input_field.text()


def show_chest_dialog(prompt: str = "", parent=None) -> str:
    """
    Show a Minecraft-style chest dialog and return the user input.
    
    Args:
        prompt: The message to display to the user
        parent: Parent widget
    
    Returns:
        The text entered by the user, or empty string if cancelled
    """
    dialog = ChestDialog(prompt, parent)
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_input()
    return ""
