"""
tests/test_error_translator.py
================================
Cada test provoca un error real en el pipeline de :JCraft y verifica que
humanize() devuelva un mensaje en español con las palabras clave esperadas.
"""

import sys
import os
import pytest

# Make sure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import run_source
from lang.error_translator import humanize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compile_error(src: str) -> str:
    """Compile src, expect an exception, return its humanized message."""
    with pytest.raises(Exception) as exc_info:
        toks = tokenize(src)
        Parser(toks).parse()
    return humanize(exc_info.value)


def _run_error(src: str) -> str:
    """Run src, expect an exception, return its humanized message."""
    with pytest.raises(Exception) as exc_info:
        run_source(src)
    return humanize(exc_info.value)


def _contains(msg: str, *words: str):
    """Assert that msg contains every word (case-insensitive)."""
    lower = msg.lower()
    for word in words:
        assert word.lower() in lower, (
            f"Expected '{word}' in translated message, got:\n  {msg}"
        )


# ---------------------------------------------------------------------------
# Parser errors
# ---------------------------------------------------------------------------

def test_missing_semicolon():
    src = "mesa_crafteo vacío main():\n  bloques x = 5\nfin"
    msg = _compile_error(src)
    _contains(msg, "punto y coma", "línea")


def test_missing_colon():
    # Missing ':' after the function signature
    src = "mesa_crafteo vacío main()\n  bloques x = 5;\nfin"
    msg = _compile_error(src)
    _contains(msg, "dos puntos")


def test_missing_fin():
    src = "mesa_crafteo vacío main():\n  bloques x = 5;\n"
    msg = _compile_error(src)
    _contains(msg, "fin")


def test_missing_boom():
    src = "mesa_crafteo vacío main():\n  creeper:\n    letrero \"x\";\n"
    msg = _compile_error(src)
    _contains(msg, "boom", "creeper")


def test_missing_salir_portal():
    # The inner 'caso' block hits EOF before 'portal' can — error correctly names 'caso'
    src = (
        "mesa_crafteo vacío main():\n"
        "  portal (1):\n"
        "    caso 1:\n"
        "      letrero \"x\";\n"
    )
    msg = _compile_error(src)
    _contains(msg, "caso")


def test_comparador_without_observador():
    src = "mesa_crafteo vacío main():\n  comparador (verdadero):\n  fin\nfin"
    msg = _compile_error(src)
    _contains(msg, "comparador", "observador")


def test_unexpected_token_top_level():
    # A statement outside any function
    src = "letrero \"hola\";"
    msg = _compile_error(src)
    _contains(msg, "fuera de una función")


def test_reserved_word_as_var():
    src = "mesa_crafteo vacío main():\n  bloques fin = 3;\nfin"
    msg = _compile_error(src)
    # Parser already emits a Spanish message; just check it surfaces
    _contains(msg, "reservada")


# ---------------------------------------------------------------------------
# Lexer errors
# ---------------------------------------------------------------------------

def test_unexpected_symbol():
    src = "mesa_crafteo vacío main():\n  @ = 5;\nfin"
    msg = _compile_error(src)
    _contains(msg, "línea")


# ---------------------------------------------------------------------------
# Interpreter / runtime errors
# ---------------------------------------------------------------------------

def test_no_main():
    src = "bloques x = 5;"
    msg = _run_error(src)
    _contains(msg, "main")


def test_undeclared_variable():
    src = "mesa_crafteo vacío main():\n  letrero x;\nfin"
    msg = _run_error(src)
    _contains(msg, "variable", "x")


def test_undeclared_function():
    src = "mesa_crafteo vacío main():\n  miFuncion();\nfin"
    msg = _run_error(src)
    _contains(msg, "función", "miFuncion")


def test_wrong_arg_count():
    src = (
        "mesa_crafteo vacío saludar(texto nombre):\n"
        "  letrero nombre;\n"
        "fin\n"
        "mesa_crafteo vacío main():\n"
        "  saludar(\"Juan\", \"extra\");\n"
        "fin"
    )
    msg = _run_error(src)
    _contains(msg, "argumento")


def test_loop_limit():
    # spawner blocks are closed by 'romper', not 'fin'
    src = (
        "mesa_crafteo vacío main():\n"
        "  spawner (verdadero):\n"
        "    letrero \"loop\";\n"
        "  romper\n"
        "fin"
    )
    msg = _run_error(src)
    _contains(msg, "spawner", "veces")


# ---------------------------------------------------------------------------
# Type checker errors
# ---------------------------------------------------------------------------

def test_type_mismatch_assign():
    src = (
        "mesa_crafteo vacío main():\n"
        "  bloques x = \"hola\";\n"
        "fin"
    )
    msg = _run_error(src)
    _contains(msg, "tipo")


def test_condition_not_bool():
    src = (
        "mesa_crafteo vacío main():\n"
        "  observador (42):\n"
        "    letrero \"si\";\n"
        "  fin\n"
        "fin"
    )
    msg = _run_error(src)
    _contains(msg, "condición", "redstone")
