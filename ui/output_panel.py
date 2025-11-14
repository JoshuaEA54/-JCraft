from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtGui import QFont

class OutputPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setProperty("class", "Card")
        self.setFrameStyle(QFrame.NoFrame)

        self._font_family = "Consolas"
        self._font_size = 12

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        self.title = QLabel("OUTPUT", self)
        self.title.setObjectName("titleOutput")

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)

        row = QHBoxLayout()
        row.addStretch(1)
        self.btn_compile = QPushButton("COMPILAR", self)
        self.btn_compile.setObjectName("btnPrimary")
        self.btn_run = QPushButton("EJECUTAR", self)
        self.btn_run.setObjectName("btnPrimary")
        self.btn_stop = QPushButton("DETENER", self)
        self.btn_stop.setVisible(False)  # Oculto por defecto
        
        # Estilo rojo para el botón DETENER (inline, específico de este componente)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: #E74C3C;
                color: #2A0A08;
                border-radius: 10px;
                padding: 10px 16px;
                border: 1px solid rgba(0,0,0,0.25);
                font-weight: 600;
            }
            QPushButton:hover {
                background: #F25A4A;
            }
            QPushButton:pressed {
                background: #D43F2F;
            }
        """)
        
        row.addWidget(self.btn_compile)
        row.addSpacing(8)
        row.addWidget(self.btn_run)
        row.addWidget(self.btn_stop)  # En el mismo lugar que btn_run

        lay.addWidget(self.title)
        lay.addWidget(self.output, 1)
        lay.addLayout(row)
        self.apply_font()

    def set_font_family(self, family: str):
        self._font_family = family
        self.apply_font()

    def set_font_size(self, size: int):
        self._font_size = max(8, min(40, size))
        self.apply_font()

    def apply_font(self):
        self.output.setStyleSheet(
            f'QTextEdit {{ font-family: "{self._font_family}"; font-size: {self._font_size}pt; }}'
        )
        self.output.setFont(QFont(self._font_family, self._font_size))

    def clear(self): self.output.clear()
    def append(self, text: str): self.output.append(text)
