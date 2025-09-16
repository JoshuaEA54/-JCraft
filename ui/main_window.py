from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QStatusBar, QSplitter
)
from .style import STYLE_QSS
from .background import Background
from .editor_panel import EditorPanel
from .output_panel import OutputPanel
from .fonts import load_pixel_font_family

ASSETS = Path("assets")
BACKGROUND_PATH = ASSETS / "jcraft_bg.png"
ICON_PATHS = [ASSETS / "jcraft_logo.ico", ASSETS / "jcraft_logo.png"]

class MainWindow(QMainWindow):
    def __init__(self, title=":JCraft IDE"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(900, 620)
        self.setMinimumSize(QSize(760, 560))

        for p in ICON_PATHS:
            if p.exists():
                self.setWindowIcon(QIcon(str(p)))
                break

        self.pixel_family = load_pixel_font_family()

        self._build_ui()
        self._build_menu()
        self._wire_stubs()

    def _build_ui(self):
        self.setStyleSheet(STYLE_QSS)

        center = QWidget(self)
        center.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(center)

        base = QVBoxLayout(center)
        base.setContentsMargins(14, 10, 14, 12)
        base.setSpacing(10)

        self.background = Background(center)
        if BACKGROUND_PATH.exists():
            self.background.set_image(BACKGROUND_PATH)
        self.background.lower()
        self.background.setGeometry(center.rect())

        splitter = QSplitter(Qt.Horizontal, center)
        self.editor_panel = EditorPanel(splitter)
        self.output_panel = OutputPanel(splitter)

        if self.pixel_family:
            self.editor_panel.set_pixel_family(self.pixel_family)
            self.editor_panel.toggle_pixel_font(True)
            self.output_panel.set_font_family(self.pixel_family)

        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        base.addWidget(splitter, 1)

        self.setMenuBar(QMenuBar(self))
        self.setStatusBar(QStatusBar(self))

        def _on_resize():
            self.background.setGeometry(self.centralWidget().rect())
        self.centralWidget().resizeEvent = lambda e: (_on_resize(), QWidget.resizeEvent(self.centralWidget(), e))

    def _build_menu(self):
        mb = self.menuBar()

        act_new = QAction("Nuevo", self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self._on_new)
        mb.addAction(act_new)

        menu_view = mb.addMenu("Ver")
        act_zoom_in   = QAction("Aumentar fuente", self);  act_zoom_in.setShortcut("Ctrl++")
        act_zoom_out  = QAction("Disminuir fuente", self); act_zoom_out.setShortcut("Ctrl+-")
        act_zoom_reset= QAction("Restablecer fuente", self); act_zoom_reset.setShortcut("Ctrl+0")
        act_pixel     = QAction("Usar fuente Pixel (si disponible)", self, checkable=True)
        act_pixel.setChecked(self.pixel_family is not None)

        act_zoom_in.triggered.connect(self._zoom_in)
        act_zoom_out.triggered.connect(self._zoom_out)
        act_zoom_reset.triggered.connect(self._zoom_reset)
        act_pixel.triggered.connect(self._toggle_pixel)

        menu_view.addAction(act_zoom_in)
        menu_view.addAction(act_zoom_out)
        menu_view.addAction(act_zoom_reset)
        menu_view.addSeparator()
        menu_view.addAction(act_pixel)

        menu_opt = mb.addMenu("Opciones")
        menu_opt.addAction(QAction("Formatear (stub)", self))

        act_exit = QAction("Salir", self)
        act_exit.triggered.connect(self.close)
        mb.addAction(act_exit)

        self.output_panel.btn_compile.setShortcut("F9")
        self.output_panel.btn_run.setShortcut("Ctrl+Return")

    def _on_new(self):
        self.editor_panel.set_text("")
        self.output_panel.clear()

    def _wire_stubs(self):
        self.output_panel.btn_compile.clicked.connect(self._on_compile)
        self.output_panel.btn_run.clicked.connect(self._on_run)

    def _on_compile(self):
        self.output_panel.clear()
        self.output_panel.append("[stub] Compilar aún no implementado.")

    def _on_run(self):
        self.output_panel.append("[stub] Ejecutar aún no implementado.")

    def _zoom_in(self):
        self.editor_panel.zoom(+1)
        self.output_panel.set_font_size(self.editor_panel._font_size)

    def _zoom_out(self):
        self.editor_panel.zoom(-1)
        self.output_panel.set_font_size(self.editor_panel._font_size)

    def _zoom_reset(self):
        self.editor_panel.reset_zoom()
        self.output_panel.set_font_size(self.editor_panel._font_size)

    def _toggle_pixel(self, checked: bool):
        self.editor_panel.toggle_pixel_font(checked)
        fam = self.editor_panel._font_family_pixel if checked and self.editor_panel._font_family_pixel else "Consolas"
        self.output_panel.set_font_family(fam)

    def run(self):
        self.show()
