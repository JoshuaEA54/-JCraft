from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QStatusBar, QSplitter, QInputDialog, QMenu
)
from .style import STYLE_QSS
from .background import Background
from .editor_panel import EditorPanel
from .output_panel import OutputPanel
from .fonts import load_pixel_font_family
from .snippets import get_snippet_menu_structure

# language tooling
from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import run_source

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

        # Inicializar con la estructura básica de main
        template_inicial = """mesa_crafteo vacío main():
    
fin
"""
        self.editor_panel.set_text(template_inicial)

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

        # Menú Insertar con snippets
        menu_insert = mb.addMenu("Insertar")
        self._build_snippet_menu(menu_insert)

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
        """Crear nuevo archivo con estructura básica de main"""
        template = """mesa_crafteo vacío main():
    
fin
"""
        self.editor_panel.set_text(template)
        self.output_panel.clear()

    def _wire_stubs(self):
        self.output_panel.btn_compile.clicked.connect(self._on_compile)
        self.output_panel.btn_run.clicked.connect(self._on_run)

    def _on_compile(self):
        """Run lexer + parser and display tokens and AST in the output panel."""
        self.output_panel.clear()
        src = self.editor_panel.text()
        try:
            toks = tokenize(src)
            # show tokens
            self.output_panel.append("--- TOKENS ---")
            for t in toks:
                self.output_panel.append(repr(t))

            # parse
            p = Parser(toks)
            prog = p.parse()
            self.output_panel.append("\n--- AST ---")
            self.output_panel.append(repr(prog))
            self.output_panel.append("\n[OK] Compilación terminada sin errores.")
        except Exception as e:
            self.output_panel.append(f"[ERROR] {type(e).__name__}: {e}")

    def _on_run(self):
        """Execute the source via the interpreter and show results."""
        self.output_panel.clear()
        self.output_panel.append("--- EJECUCIÓN ---")
        src = self.editor_panel.text()
        
        # Callback para cofre() que muestra primero el prompt en OUTPUT y luego el diálogo
        def input_callback(prompt: str) -> str:
            # Mostrar el prompt en la consola de salida
            self.output_panel.append(prompt)
            
            # Crear diálogo con estilo para que todo sea visible (texto negro, botones negros)
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Entrada - cofre()")
            dialog.setLabelText(prompt)
            dialog.setStyleSheet("""
                QLabel { 
                    color: black; 
                }
                QLineEdit { 
                    color: black; 
                    background-color: white; 
                }
                QPushButton { 
                    color: black; 
                    background-color: #e0e0e0;
                    border: 1px solid #999;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
            
            if dialog.exec():
                text = dialog.textValue()
                return text
            return ""  # si cancela, devuelve vacío
        
        try:
            results = run_source(src, input_callback=input_callback, debug=False)
            if results:
                for r in results:
                    self.output_panel.append(str(r))
            else:
                self.output_panel.append("(sin salida)")
            self.output_panel.append("\n[OK] Ejecución terminada.")
        except Exception as e:
            self.output_panel.append(f"[ERROR] {type(e).__name__}: {e}")

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

    def _build_snippet_menu(self, parent_menu):
        """Construye el menú de snippets organizados por categorías"""
        snippets = get_snippet_menu_structure()
        
        for category, items in snippets.items():
            # Crear submenú para cada categoría
            category_menu = QMenu(category, parent_menu)
            
            for snippet_name in items.keys():
                # Crear acción para cada snippet
                action = QAction(snippet_name, self)
                # Conectar con lambda que captura category y snippet_name
                action.triggered.connect(
                    lambda checked=False, cat=category, name=snippet_name: 
                    self._insert_snippet(cat, name)
                )
                category_menu.addAction(action)
            
            parent_menu.addMenu(category_menu)
    
    def _insert_snippet(self, category: str, snippet_name: str):
        """Inserta un snippet en el editor, automáticamente dentro del main si existe"""
        from .snippets import get_snippet
        
        code = get_snippet(category, snippet_name)
        if not code:
            return
            
        current_text = self.editor_panel.text()
        
        # Si el snippet es para definir función (va ANTES de main)
        if "ANTES de main" in code or "mesa_crafteo" in code:
            # Insertar antes del main
            if "mesa_crafteo vacío main():" in current_text:
                # Buscar la posición del main
                main_pos = current_text.find("mesa_crafteo vacío main():")
                new_text = current_text[:main_pos] + code + "\n\n" + current_text[main_pos:]
            else:
                # No hay main, insertar al final
                new_text = current_text + "\n\n" + code
        else:
            # Es código normal, insertarlo DENTRO del main
            if "mesa_crafteo vacío main():" in current_text and "fin" in current_text:
                # Buscar la línea después de "mesa_crafteo vacío main():"
                lines = current_text.split('\n')
                new_lines = []
                dentro_main = False
                insertado = False
                
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    
                    # Si encontramos el main y aún no hemos insertado
                    if "mesa_crafteo vacío main():" in line and not insertado:
                        dentro_main = True
                        # Insertar el código después del main, con indentación
                        snippet_lines = code.split('\n')
                        for snippet_line in snippet_lines:
                            if snippet_line.strip():  # Si la línea no está vacía
                                new_lines.append("    " + snippet_line)
                            else:
                                new_lines.append(snippet_line)
                        insertado = True
                
                new_text = '\n'.join(new_lines)
            else:
                # No hay estructura de main válida, insertar normalmente
                if current_text.strip():
                    new_text = current_text + "\n\n" + code
                else:
                    new_text = code
        
        self.editor_panel.set_text(new_text)
        self.statusBar().showMessage(f"Snippet insertado: {snippet_name}", 3000)

    def run(self):
        self.show()
