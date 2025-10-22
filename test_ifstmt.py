from lang.interpreter import run_source

src = '''
mesa_crafteo vacío main():
  bloques x = -1;
  observador (x > 0):
    letrero "positivo";
  comparador (x == 0):
    letrero "cero";
  dispensador:
    letrero "negativo";
  fin
fin
'''

print(run_source(src, input_callback=lambda p: '', debug=True))
