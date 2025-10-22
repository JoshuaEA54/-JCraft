"""Test de break (romper) y continue (continuar) en bucles"""
from lang.interpreter import run_source

# Test 1: romper() en while (spawner)
print("=== Test romper() en while ===")
src_break_while = '''
mesa_crafteo vacío main():
  bloques i = 0;
  spawner (i < 10):
    letrero "i = " + i;
    i = i + 1;
    observador (i == 3):
      romper();
    fin
  romper
fin
'''
print(run_source(src_break_while, debug=False))

# Test 2: continuar() en while (spawner)
print("\n=== Test continuar() en while ===")
src_continue_while = '''
mesa_crafteo vacío main():
  bloques j = 0;
  spawner (j < 5):
    j = j + 1;
    observador (j == 2):
      continuar();
    fin
    letrero "j = " + j;
  romper
fin
'''
print(run_source(src_continue_while, debug=False))

# Test 3: romper() en for (cultivar)
print("\n=== Test romper() en for ===")
src_break_for = '''
mesa_crafteo vacío main():
  cultivar (bloques k = 0; k < 10; k = k + 1):
    observador (k == 4):
      romper();
    fin
    letrero "k = " + k;
  cosechar
fin
'''
print(run_source(src_break_for, debug=False))

# Test 4: continuar() en for (cultivar)
print("\n=== Test continuar() en for ===")
src_continue_for = '''
mesa_crafteo vacío main():
  cultivar (bloques m = 0; m < 5; m = m + 1):
    observador (m == 2):
      continuar();
    fin
    letrero "m = " + m;
  cosechar
fin
'''
print(run_source(src_continue_for, debug=False))

# Test 5: romper() en do-while (creeper)
print("\n=== Test romper() en do-while ===")
src_break_dowhile = '''
mesa_crafteo vacío main():
  bloques n = 0;
  creeper:
    letrero "n = " + n;
    n = n + 1;
    observador (n == 3):
      romper();
    fin
  boom (n < 10);
fin
'''
print(run_source(src_break_dowhile, debug=False))

# Test 6: romper() en switch (portal)
print("\n=== Test romper() en switch ===")
src_break_switch = '''
mesa_crafteo vacío main():
  bloques dia = 2;
  portal (dia):
    caso 1:
      letrero "Lunes";
      romper();
    caso 2:
      letrero "Martes";
      romper();
    caso 3:
      letrero "Miércoles";
      romper();
    defecto:
      letrero "Otro día";
  salir_portal
fin
'''
print(run_source(src_break_switch, debug=False))
