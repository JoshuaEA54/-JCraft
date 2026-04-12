"""
error_translator.py
===================
Converts raw technical error messages from the :JCraft pipeline into
child-friendly Spanish sentences.

Public API
----------
    humanize(exc: Exception) -> str
        Translate the message of an exception.

    humanize_line(line: str) -> str
        Translate a single raw error line (used for multi-line TypeChecker output).
"""

import re

# ---------------------------------------------------------------------------
# Token-type → Spanish name
# ---------------------------------------------------------------------------

_TOKEN_NAMES: dict[str, str] = {
    "SEMI":    "punto y coma (;)",
    "COLON":   "dos puntos (:)",
    "COMMA":   "coma (,)",
    "LPAREN":  "paréntesis de apertura '('",
    "RPAREN":  "paréntesis de cierre ')'",
    "LBRACK":  "corchete de apertura '['",
    "RBRACK":  "corchete de cierre ']'",
    "LBRACE":  "llave de apertura '{'",
    "RBRACE":  "llave de cierre '}'",
    "KEYWORD": "palabra reservada",
    "IDENT":   "nombre de variable o función",
    "INT":     "número entero",
    "FLOAT":   "número decimal",
    "STRING":  "texto entre comillas",
    "CHAR":    "carácter entre comillas simples",
    "BOOL":    "verdadero o falso",
    "OP":      "operador",
    "EOF":     "el final del código",
    "LT":      "símbolo '<'",
    "GT":      "símbolo '>'",
}


def _tok(name: str) -> str:
    """Return the Spanish name for a token type, or the raw name if unknown."""
    return _TOKEN_NAMES.get(name.upper(), f"'{name}'")


# ---------------------------------------------------------------------------
# Rules: list of (compiled_pattern, handler(match) -> str)
# Order matters — more specific patterns must come first.
# ---------------------------------------------------------------------------

def _rules() -> list[tuple[re.Pattern, object]]:
    R = re.compile

    return [
        # ── Parser: specific token expectations ────────────────────────────

        # Expected SEMI but got X at line:col
        (R(r"Expected SEMI but got .+ at (\d+):\d+", re.I),
         lambda m: f"Falta un punto y coma (;) al final de la instrucción en la línea {m.group(1)}"),

        # Expected SEMI but got EOF
        (R(r"Expected SEMI but got EOF", re.I),
         lambda m: "Falta un punto y coma (;) al final de la última instrucción"),

        # Expected COLON but got X at line:col
        (R(r"Expected COLON but got .+ at (\d+):\d+", re.I),
         lambda m: f"Faltan los dos puntos (:) en la línea {m.group(1)}"),

        # Expected LPAREN but got X at line:col
        (R(r"Expected LPAREN but got .+ at (\d+):\d+", re.I),
         lambda m: f"Falta un paréntesis de apertura '(' en la línea {m.group(1)}"),

        # Expected RPAREN but got X at line:col
        (R(r"Expected RPAREN but got .+ at (\d+):\d+", re.I),
         lambda m: f"Falta cerrar el paréntesis ')' en la línea {m.group(1)}"),

        # Expected LBRACK but got X at line:col
        (R(r"Expected LBRACK but got .+ at (\d+):\d+", re.I),
         lambda m: f"Falta un corchete de apertura '[' en la línea {m.group(1)}"),

        # Expected RBRACK but got X at line:col
        (R(r"Expected RBRACK but got .+ at (\d+):\d+", re.I),
         lambda m: f"Falta cerrar el corchete ']' en la línea {m.group(1)}"),

        # Expected '=' after variable declaration at line:col
        (R(r"Expected '=' after variable declaration at (\d+):\d+", re.I),
         lambda m: f"Falta el signo '=' para asignar el valor de la variable en la línea {m.group(1)}"),

        # Expected type keyword but got X at line:col
        (R(r"Expected type keyword but got .+ at (\d+):\d+", re.I),
         lambda m: f"Se esperaba un tipo de dato (bloques, texto, coordenada…) en la línea {m.group(1)}"),

        # Expected type but got EOF
        (R(r"Expected type but got EOF", re.I),
         lambda m: "Se esperaba un tipo de dato pero el código terminó de forma inesperada"),

        # Generic: Expected X but got Y at line:col  (catch-all parser expectation)
        (R(r"Expected (\w+) but got (\w+) at (\d+):\d+", re.I),
         lambda m: f"Error en la línea {m.group(3)}: se esperaba {_tok(m.group(1))} "
                   f"pero se encontró {_tok(m.group(2))}"),

        # Expected X but got EOF
        (R(r"Expected .+ but got EOF", re.I),
         lambda m: "El código termina de forma inesperada. ¿Falta cerrar un bloque con 'fin'?"),

        # ── Parser: block structure ─────────────────────────────────────────

        (R(r"Unterminated creeper block", re.I),
         lambda m: "Falta el 'boom' para cerrar el bloque 'creeper'"),

        (R(r"Unterminated portal block", re.I),
         lambda m: "Falta 'salir_portal' para cerrar el bloque 'portal'"),

        (R(r"Unterminated if-like block", re.I),
         lambda m: "Falta 'fin' para cerrar el bloque"),

        (R(r"Expected 'fin' to close", re.I),
         lambda m: "Falta la palabra 'fin' para cerrar el bloque"),

        (R(r"Unterminated caso block", re.I),
         lambda m: "Falta cerrar el bloque 'caso'"),

        (R(r"Unterminated defecto block", re.I),
         lambda m: "Falta cerrar el bloque 'defecto'"),

        (R(r"Unterminated block, expected (.+)", re.I),
         lambda m: f"Falta la palabra {m.group(1).strip()} para cerrar el bloque"),

        (R(r"'(.+)' without preceding 'observador' at (\d+):\d+", re.I),
         lambda m: f"'{m.group(1)}' en la línea {m.group(2)} necesita un 'observador' antes"),

        (R(r"Expected 'caso' or 'defecto'.+at (\d+):\d+", re.I),
         lambda m: f"Se esperaba 'caso' o 'defecto' dentro del bloque 'portal' en la línea {m.group(1)}"),

        # ── Parser: unexpected tokens ───────────────────────────────────────

        (R(r"Unexpected token .+ at top-level", re.I),
         lambda m: "Esta instrucción no puede estar fuera de una función"),

        (R(r"Unexpected statement starting with .+ at (\d+):\d+", re.I),
         lambda m: f"Instrucción desconocida en la línea {m.group(1)}"),

        (R(r"Unexpected EOF in expression", re.I),
         lambda m: "El código termina de forma inesperada dentro de una expresión"),

        (R(r"Unexpected token in expression", re.I),
         lambda m: "Expresión incorrecta: símbolo inesperado"),

        # ── Lexer ───────────────────────────────────────────────────────────

        (R(r"Unexpected token (.+) at (\d+):\d+", re.I),
         lambda m: f"Símbolo desconocido {m.group(1)} en la línea {m.group(2)}"),

        # ── Interpreter: main / functions ───────────────────────────────────

        (R(r"main function not found", re.I),
         lambda m: "No se encontró la función 'main'. "
                   "El programa debe tener: mesa_crafteo vacío main():"),

        (R(r"main must not have parameters", re.I),
         lambda m: "La función 'main' no puede tener parámetros"),

        (R(r"Function (.+) not defined", re.I),
         lambda m: f"La función '{m.group(1).strip()}' no está definida"),

        (R(r"Function '(.+)' not declared", re.I),
         lambda m: f"La función '{m.group(1)}' no está declarada"),

        (R(r"Function '(.+)' declared multiple times", re.I),
         lambda m: f"La función '{m.group(1)}' está definida más de una vez"),

        (R(r"Function '(.+)' expects (\d+) arguments?, received (\d+)", re.I),
         lambda m: f"La función '{m.group(1)}' necesita {m.group(2)} "
                   f"argumento(s), pero recibió {m.group(3)}"),

        (R(r"Function (.+) expects (\d+) args?, got (\d+)", re.I),
         lambda m: f"La función '{m.group(1).strip()}' necesita {m.group(2)} "
                   f"argumento(s), pero recibió {m.group(3)}"),

        # ── Interpreter: variables ──────────────────────────────────────────

        (R(r"Variable '(.+)' already declared in this scope", re.I),
         lambda m: f"La variable '{m.group(1)}' ya fue declarada antes en este bloque"),

        (R(r"Variable (\S+) not defined", re.I),
         lambda m: f"La variable '{m.group(1)}' no está declarada"),

        (R(r"Variable '(.+)' no declarada", re.I),
         lambda m: f"La variable '{m.group(1)}' no está declarada"),

        # ── Interpreter: loops ──────────────────────────────────────────────

        (R(r"[Ww]hile loop exceeded .+ iterations"),
         lambda m: "El ciclo 'spawner' se repitió demasiadas veces. "
                   "Revisa que la condición pueda volverse falsa"),

        (R(r"[Ff]or loop .+ exceeded .+ iterations"),
         lambda m: "El ciclo 'cultivar' se repitió demasiadas veces"),

        (R(r"[Ff]or loop range too large"),
         lambda m: "El rango del ciclo 'cultivar' es demasiado grande"),

        (R(r"[Dd]o-while loop exceeded .+ iterations"),
         lambda m: "El ciclo 'creeper' se repitió demasiadas veces. "
                   "Revisa que la condición pueda volverse falsa"),

        # ── Interpreter: built-ins ──────────────────────────────────────────

        (R(r"pop on empty list", re.I),
         lambda m: "No se puede usar 'pop' en una lista vacía"),

        (R(r"push expects a list as first argument", re.I),
         lambda m: "'push' necesita una lista (inventario) como primer argumento"),

        (R(r"length expects a list or map", re.I),
         lambda m: "'length' solo funciona con listas (inventario) o mapas (mapa)"),

        (R(r"tiene expects a map as first argument", re.I),
         lambda m: "'tiene' necesita un mapa (mapa) como primer argumento"),

        (R(r"Index .+error.+", re.I),
         lambda m: "Error al acceder a una posición de la lista o mapa"),

        # ── Type checker ────────────────────────────────────────────────────

        (R(r"Variable '(.+)': tipo declarado '(.+)' incompatible con tipo de inicialización '(.+)'"),
         lambda m: f"La variable '{m.group(1)}' es de tipo '{m.group(2)}' "
                   f"pero se le asigna un valor de tipo '{m.group(3)}'"),

        (R(r"Asignación a '(.+)': tipo '(.+)' incompatible con tipo de variable '(.+)'"),
         lambda m: f"No se puede asignar un valor de tipo '{m.group(2)}' "
                   f"a la variable '{m.group(1)}' que es de tipo '{m.group(3)}'"),

        (R(r"Condition in '(.+)' must be 'redstone', not '(.+)'", re.I),
         lambda m: f"La condición de '{m.group(1)}' debe ser verdadero/falso (redstone), "
                   f"no '{m.group(2)}'"),

        (R(r"Operator '(.+)' requires numeric types, not '(.+)' and '(.+)'", re.I),
         lambda m: f"El operador '{m.group(1)}' solo funciona con números, "
                   f"no con '{m.group(2)}' ni '{m.group(3)}'"),

        (R(r"Operator '(.+)' not supported for types '(.+)' and '(.+)'", re.I),
         lambda m: f"No se puede usar el operador '{m.group(1)}' "
                   f"con valores de tipo '{m.group(2)}' y '{m.group(3)}'"),

        (R(r"Operator '(.+)' requires 'redstone' types, not '(.+)' and '(.+)'", re.I),
         lambda m: f"El operador '{m.group(1)}' solo funciona con verdadero/falso (redstone), "
                   f"no con '{m.group(2)}' ni '{m.group(3)}'"),

        (R(r"Return type '(.+)' incompatible with declared type '(.+)'", re.I),
         lambda m: f"La función devuelve '{m.group(1)}' pero debería devolver '{m.group(2)}'"),

        (R(r"Function '(.+)' must return a value of type '(.+)'", re.I),
         lambda m: f"La función '{m.group(1)}' debe devolver un valor de tipo '{m.group(2)}'"),

        (R(r"'craftear' outside of a function", re.I),
         lambda m: "'craftear' solo puede usarse dentro de una función"),

        (R(r"Function 'main' .+ must return 'vacío'", re.I),
         lambda m: "La función 'main' debe ser de tipo 'vacío'"),

        (R(r"main must return 'vacío', not '(.+)'", re.I),
         lambda m: f"La función 'main' debe ser de tipo 'vacío', no '{m.group(1)}'"),

        (R(r"Function 'main' not found", re.I),
         lambda m: "No se encontró la función 'main'. "
                   "El programa debe tener: mesa_crafteo vacío main():"),

        (R(r"Inventario index must be 'bloques'", re.I),
         lambda m: "El índice de un inventario debe ser un número entero (bloques)"),

        (R(r"Cannot index type '(.+)'", re.I),
         lambda m: f"No se puede acceder por índice a un valor de tipo '{m.group(1)}'"),

        (R(r"List with inconsistent element types: '(.+)' and '(.+)'", re.I),
         lambda m: f"La lista tiene elementos de tipos distintos: '{m.group(1)}' y '{m.group(2)}'"),

        (R(r"Map with inconsistent key types: '(.+)' and '(.+)'", re.I),
         lambda m: f"El mapa tiene claves de tipos distintos: '{m.group(1)}' y '{m.group(2)}'"),

        (R(r"Map with inconsistent value types: '(.+)' and '(.+)'", re.I),
         lambda m: f"El mapa tiene valores de tipos distintos: '{m.group(1)}' y '{m.group(2)}'"),

        # ── Conversion built-ins ────────────────────────────────────────────

        (R(r"No se puede convertir '(.+)' a bloques", re.I),
         lambda m: f"No se puede convertir '{m.group(1)}' a número entero (bloques)"),

        (R(r"No se puede convertir '(.+)' a coordenada", re.I),
         lambda m: f"No se puede convertir '{m.group(1)}' a número decimal (coordenada)"),

        (R(r"El valor '(.+)' no es un glifo válido", re.I),
         lambda m: f"'{m.group(1)}' no es un carácter válido (glifo debe ser un solo carácter)"),
    ]


# Build rules once at module load
_RULES = _rules()


# ---------------------------------------------------------------------------
# Core translation
# ---------------------------------------------------------------------------

def _translate(msg: str) -> str:
    """Try each rule; return the first Spanish translation that matches."""
    for pattern, handler in _RULES:
        m = pattern.search(msg)
        if m:
            return handler(m)
    # Fallback: return original (untranslated is better than silence)
    return msg


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def humanize(exc: Exception) -> str:
    """Translate the message of a :JCraft pipeline exception to Spanish."""
    return _translate(str(exc))


def humanize_line(line: str) -> str:
    """Translate a single raw error line (for multi-line TypeChecker output)."""
    return _translate(line)
