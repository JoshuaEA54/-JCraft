from PySide6.QtWidgets import QFrame, QVBoxLayout, QPlainTextEdit, QWidget
from PySide6.QtGui import QFont, QPainter, QColor, QTextFormat
from PySide6.QtCore import Qt, QRect, QSize


class LineNumberArea(QWidget):
    """Widget para mostrar los números de línea"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        # Hacer el widget transparente
        self.setAttribute(Qt.WA_TranslucentBackground)

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class JCraftTextEdit(QPlainTextEdit):
    """QPlainTextEdit extendido con números de línea"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        # Conectar señales para actualizar números de línea
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        """Calcula el ancho necesario para el área de números de línea"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Actualiza el margen izquierdo para el área de números de línea"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Actualiza el área de números de línea cuando el contenido cambia"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Ajusta el tamaño del área de números de línea cuando se redimensiona el editor"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), 
                                                 self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """Dibuja los números de línea"""
        painter = QPainter(self.line_number_area)
        # Fondo transparente para que se vea el fondo del Card
        painter.fillRect(event.rect(), Qt.transparent)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Usar la misma fuente que el editor
        painter.setFont(self.font())
        # Color blanco (#E8EEF2) consistente con el resto del UI
        painter.setPen(QColor(232, 238, 242))

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                               self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


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

        self.editor = JCraftTextEdit(self)
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
