from lang.interpreter import run_source
src = """
mesa_crafteo vacío main():
  bloques vidas = 3;
  letrero "Vidas: " + vidas;
fin
"""
out = run_source(src, input_callback=lambda p: "entrada_demo", debug=True)
print("RESULTS:", out)
