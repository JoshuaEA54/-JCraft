from PySide6.QtWidgets import QFrame, QVBoxLayout, QPlainTextEdit
from PySide6.QtGui import QFont

class EditorPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setProperty("class", "Card")
        self.setFrameStyle(QFrame.NoFrame)

        self._font_family_mono = "Consolas"
        self._font_family_pixel = None
        self._use_pixel = False
        self._font_size = 12

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.editor = QPlainTextEdit(self)
        # Sin placeholder - el texto inicial se establece en main_window
        layout.addWidget(self.editor)
        self.apply_font()

    def set_pixel_family(self, family: str | None):
        self._font_family_pixel = family

    def toggle_pixel_font(self, use_pixel: bool):
        self._use_pixel = use_pixel
        self.apply_font()

    def zoom(self, delta: int):
        self._font_size = max(8, min(40, self._font_size + delta))
        self.apply_font()

    def reset_zoom(self):
        self._font_size = 12
        self.apply_font()

    def apply_font(self):
        fam = self._font_family_pixel if (self._use_pixel and self._font_family_pixel) else self._font_family_mono
        self.editor.setStyleSheet(
            f'QPlainTextEdit {{ font-family: "{fam}"; font-size: {self._font_size}pt; }}'
        )
        self.editor.setFont(QFont(fam, self._font_size))

    def text(self) -> str:
        return self.editor.toPlainText()

    def set_text(self, text: str):
        self.editor.setPlainText(text)
