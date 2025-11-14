from pathlib import Path
from PySide6.QtCore import Qt, QSize, QThread, Signal, QObject
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
from .chest_dialog import show_chest_dialog

# language tooling
from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import run_source
from lang.format import format_jcraft_code

ASSETS = Path("assets")
BACKGROUND_PATH = ASSETS / "jcraft_bg.png"
ICON_PATHS = [ASSETS / "jcraft_logo.ico", ASSETS / "jcraft_logo.png"]


class InterpreterWorker(QObject):
    """Worker para ejecutar el intérprete en un hilo separado"""
    output_ready = Signal(str)  # Señal para enviar outputs en tiempo real
    finished = Signal()  # Señal cuando termina la ejecución
    error = Signal(str)  # Señal para errores
    
    def __init__(self, source_code: str, input_callback, print_ast: bool = False):
        super().__init__()
        self.source_code = source_code
        self.input_callback = input_callback
        self.print_ast = print_ast
    
    def run(self):
        """Ejecuta el código en el hilo separado"""
        try:
            # Callback para recibir outputs en tiempo real
            def output_callback(output: str):
                self.output_ready.emit(output)
            
            # Ejecutar el código
            results = run_source(
                self.source_code, 
                input_callback=self.input_callback, 
                debug=False, 
                print_ast=self.print_ast,
                output_callback=output_callback
            )
            
            # Si hay resultados que no se enviaron por el callback, enviarlos ahora
            # (esto normalmente no debería pasar porque todos los letreros ya se enviaron)
            if not results:
                self.output_ready.emit("(sin salida)")
            
            self.finished.emit()
        except Exception as e:
            # Manejar errores
            error_message = str(e)
            if "\n" in error_message:
                error_lines = ["[ERROR]"] + [line for line in error_message.split("\n") if line.strip()]
                self.error.emit("\n".join(error_lines))
            else:
                self.error.emit(f"[ERROR] {type(e).__name__}: {error_message}")
            self.finished.emit()


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
        
        # Threading para ejecución
        self.worker_thread = None
        self.worker = None
        self.is_running = False  # Flag para saber si hay ejecución en curso

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
        act_format = QAction("Formatear", self)
        act_format.setShortcut("Ctrl+Shift+F")
        act_format.triggered.connect(self._on_format)
        menu_opt.addAction(act_format)

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
            
            # Imprimir AST en consola de VSCode
            print("\n" + "="*60)
            print("ÁRBOL SINTÁCTICO ABSTRACTO (AST)")
            print("="*60)
            print(prog)
            print("="*60 + "\n")
            
            self.output_panel.append("\n--- AST ---")
            self.output_panel.append(repr(prog))
            self.output_panel.append("\n[OK] Compilación terminada sin errores.")
        except Exception as e:
            self.output_panel.append(f"[ERROR] {type(e).__name__}: {e}")

    def _on_run(self):
        """Execute the source via the interpreter and show results."""
        # Si ya hay una ejecución en curso, no iniciar otra
        if self.is_running:
            self.output_panel.append("[ADVERTENCIA] Ya hay una ejecución en curso")
            return
        
        self.is_running = True
        self.output_panel.clear()
        self.output_panel.append("--- EJECUCIÓN ---")
        src = self.editor_panel.text()
        
        # Callback for cofre() that shows the Minecraft chest dialog
        def input_callback(prompt: str) -> str:
            # Show the prompt in the output console
            if prompt:
                self.output_panel.append(prompt)
            
            # Show the Minecraft-style chest dialog
            text = show_chest_dialog(prompt, self)
            return text
        
        # Crear el worker y el thread
        self.worker = InterpreterWorker(src, input_callback, print_ast=True)
        self.worker_thread = QThread()
        
        # Mover el worker al thread
        self.worker.moveToThread(self.worker_thread)
        
        # Conectar señales
        self.worker_thread.started.connect(self.worker.run)
        self.worker.output_ready.connect(self._on_output_ready)
        self.worker.error.connect(self._on_execution_error)
        self.worker.finished.connect(self._on_execution_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Iniciar el thread
        self.worker_thread.start()
    
    def _on_output_ready(self, output: str):
        """Callback cuando hay output disponible del intérprete"""
        self.output_panel.append(output)
    
    def _on_execution_error(self, error_msg: str):
        """Callback cuando hay un error en la ejecución"""
        self.output_panel.append(error_msg)
    
    def _on_execution_finished(self):
        """Callback cuando termina la ejecución"""
        self.output_panel.append("\n[OK] Ejecución terminada.")
        self.is_running = False  # Marcar que ya no hay ejecución en curso

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

    def _on_format(self):
        """Formatea el código del editor aplicando indentación y estructura correcta"""
        try:
            current_code = self.editor_panel.text()
            
            if not current_code.strip():
                self.statusBar().showMessage("No hay código para formatear", 3000)
                return
            
            formatted_code = format_jcraft_code(current_code)
            
            self.editor_panel.set_text(formatted_code)
            
            self.statusBar().showMessage("✓ Código formateado correctamente", 3000)
            
        except Exception as e:
            self.statusBar().showMessage(f"Error al formatear: {e}", 5000)
            self.output_panel.clear()
            self.output_panel.append(f"[ERROR] No se pudo formatear el código: {e}")

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
        
        # Si el snippet es un EJEMPLO COMPLETO (ya tiene su propio main), reemplazar todo
        if "mesa_crafteo vacío main():" in code and category == "Ejemplos":
            self.editor_panel.set_text(code)
            self.statusBar().showMessage(f"Ejemplo insertado: {snippet_name}", 3000)
            return
        
        # Verificar si el snippet tiene separación ###MAIN###
        if "###MAIN###" in code:
            parts = code.split("###MAIN###")
            code_antes_main = parts[0].strip()
            code_dentro_main = parts[1].strip() if len(parts) > 1 else ""
            
            # Buscar la posición del main UNA SOLA VEZ
            if "mesa_crafteo vacío main():" not in current_text:
                # No hay main, crear estructura básica
                current_text = code_antes_main + "\n\nmesa_crafteo vacío main():\n    \nfin\n"
            
            # Buscar la posición exacta del main
            main_index = current_text.find("mesa_crafteo vacío main():")
            
            if main_index != -1:
                # Dividir el texto en: antes_del_main, main, después_del_main
                antes_del_main = current_text[:main_index]
                desde_main = current_text[main_index:]
                
                # Insertar la definición de función ANTES del main
                nuevo_antes = antes_del_main + code_antes_main + "\n\n"
                
                # Ahora procesar la parte dentro del main
                lineas_main = desde_main.split('\n')
                nuevas_lineas = []
                insertado = False
                
                for i, linea in enumerate(lineas_main):
                    nuevas_lineas.append(linea)
                    
                    # Insertar después de la primera línea del main (la declaración)
                    if i == 0 and "mesa_crafteo vacío main():" in linea and code_dentro_main and not insertado:
                        # Agregar el código dentro del main con indentación
                        for snippet_line in code_dentro_main.split('\n'):
                            if snippet_line.strip():
                                nuevas_lineas.append("    " + snippet_line)
                            else:
                                nuevas_lineas.append(snippet_line)
                        insertado = True
                
                nuevo_main = '\n'.join(nuevas_lineas)
                new_text = nuevo_antes + nuevo_main
            else:
                new_text = current_text
        else:
            # Lógica original para snippets sin separación
            # Detectar si el snippet es una definición de función (no main)
            es_definicion_funcion = (
                code.strip().startswith("mesa_crafteo") and 
                "mesa_crafteo vacío main():" not in code
            )
            
            # Si el snippet es para definir función (va ANTES de main)
            if es_definicion_funcion or "ANTES de main" in code:
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
                    insertado = False
                    
                    for line in lines:
                        new_lines.append(line)
                        
                        # Si encontramos el main y aún no hemos insertado
                        if "mesa_crafteo vacío main():" in line and not insertado:
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
