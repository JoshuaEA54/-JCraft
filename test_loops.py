"""Test de bucles: spawner (while), cultivar (for), creeper (do-while), portal (switch)"""
from lang.interpreter import run_source

# Test 1: spawner (while)
print("=== Test spawner (while) ===")
src_while = '''
mesa_crafteo vacío main():
  bloques i = 0;
  spawner (i < 3):
    letrero "i = " + i;
    i = i + 1;
  romper
fin
'''
print(run_source(src_while, debug=False))

# Test 2: cultivar (for)
print("\n=== Test cultivar (for) ===")
src_for = '''
mesa_crafteo vacío main():
  cultivar (bloques j = 0; j < 3; j = j + 1):
    letrero "j = " + j;
  cosechar
fin
'''
print(run_source(src_for, debug=False))

# Test 3: creeper (do-while)
print("\n=== Test creeper (do-while) ===")
src_dowhile = '''
mesa_crafteo vacío main():
  bloques k = 0;
  creeper:
    letrero "k = " + k;
    k = k + 1;
  boom (k < 3);
fin
'''
print(run_source(src_dowhile, debug=False))

# Test 4: portal (switch-case)
print("\n=== Test portal (switch-case) ===")
src_switch = '''
mesa_crafteo vacío main():
  bloques dia = 2;
  portal (dia):
    caso 1:
      letrero "Lunes";
    caso 2:
      letrero "Martes";
    caso 3:
      letrero "Miércoles";
    defecto:
      letrero "Otro día";
  salir_portal
fin
'''
print(run_source(src_switch, debug=False))
