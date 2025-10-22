"""Test script para verificar que cofre() funciona con input interactivo"""
from lang.interpreter import run_source

src = """
mesa_crafteo vacío main():
  texto nombre = cofre("¿Cuál es tu nombre? ");
  letrero "Hola " + nombre;
fin
"""

# Simular input del usuario (en consola)
def mock_input(prompt):
    print(f"[PROMPT] {prompt}")
    return input("> ")

results = run_source(src, input_callback=mock_input, debug=False)
print("\n--- RESULTADOS ---")
for r in results:
    print(r)
