"""
Test completo del formateador :JCraft
Casos de prueba para todas las estructuras sintácticas
"""

from lang.format import format_jcraft_code


def test_case(name: str, input_code: str, description: str = ""):
    """Ejecuta un caso de test y muestra el resultado"""
    print("=" * 70)
    print(f"TEST: {name}")
    if description:
        print(f"Descripción: {description}")
    print("=" * 70)
    print("\nENTRADA:")
    print(input_code)
    print("\nSALIDA FORMATEADA:")
    result = format_jcraft_code(input_code)
    print(result)
    print()
    return result


# ============================================================================
# CASO 1: boom con diferentes espacios antes del paréntesis
# ============================================================================
test_case(
    "1. boom con espacios variables",
    'bloques x = 0; creeper: letrero("test"); x = x + 1; boom(x < 3);',
    "boom sin espacios"
)

test_case(
    "1b. boom con 1 espacio",
    'bloques x = 0; creeper: letrero("test"); x = x + 1; boom (x < 3);',
    "boom con 1 espacio"
)

test_case(
    "1c. boom con múltiples espacios",
    'bloques x = 0; creeper: letrero("test"); x = x + 1; boom   (x < 3);',
    "boom con 3 espacios"
)

# ============================================================================
# CASO 2: observador con espacios variables
# ============================================================================
test_case(
    "2. observador sin espacios",
    'observador(x > 5): letrero("mayor"); fin',
    "observador sin espacio antes de paréntesis"
)

test_case(
    "2b. observador con espacio",
    'observador (x > 5): letrero("mayor"); fin',
    "observador con 1 espacio"
)

test_case(
    "2c. observador con múltiples espacios",
    'observador   (x > 5): letrero("mayor"); fin',
    "observador con múltiples espacios"
)

# ============================================================================
# CASO 3: comparador/dispensador (alternativas condicionales)
# ============================================================================
test_case(
    "3. comparador/dispensador con espacios",
    'observador (x > 5): letrero("mayor"); comparador(x == 5): letrero("igual"); dispensador: letrero("menor"); fin',
    "comparador sin espacio, dispensador sin paréntesis"
)

test_case(
    "3b. comparador con espacios",
    'observador (x > 5): letrero("mayor"); comparador  (x == 5): letrero("igual"); dispensador: letrero("menor"); fin',
    "comparador con múltiples espacios"
)

# ============================================================================
# CASO 4: spawner (while) con espacios
# ============================================================================
test_case(
    "4. spawner sin espacios",
    'bloques i = 0; spawner(i < 5): letrero(to_texto(i)); i = i + 1; romper',
    "spawner sin espacio"
)

test_case(
    "4b. spawner con espacios",
    'bloques i = 0; spawner  (i < 5): letrero(to_texto(i)); i = i + 1; romper',
    "spawner con espacios"
)

# ============================================================================
# CASO 5: cultivar (for) con espacios
# ============================================================================
test_case(
    "5. cultivar sin espacios",
    'cultivar(i = 0; i < 5; i = i + 1): letrero(to_texto(i)); cosechar',
    "cultivar sin espacio"
)

test_case(
    "5b. cultivar con espacios",
    'cultivar  (i = 0; i < 5; i = i + 1): letrero(to_texto(i)); cosechar',
    "cultivar con espacios"
)

# ============================================================================
# CASO 6: portal (switch) con espacios
# ============================================================================
test_case(
    "6. portal sin espacios",
    'bloques x = 2; portal(x): caso 1: letrero("uno"); romper caso 2: letrero("dos"); romper defecto: letrero("otro"); romper salir_portal',
    "portal sin espacio"
)

test_case(
    "6b. portal con espacios",
    'bloques x = 2; portal  (x): caso 1: letrero("uno"); romper caso 2: letrero("dos"); romper defecto: letrero("otro"); romper salir_portal',
    "portal con espacios"
)

# ============================================================================
# CASO 7: creeper (do-while) completo
# ============================================================================
test_case(
    "7. creeper completo",
    'bloques k = 1; creeper: letrero("DO-WHILE: " + to_texto(k)); k = k + 1; boom(k <= 3);',
    "creeper con boom sin espacios"
)

test_case(
    "7b. creeper con boom espaciado",
    'bloques k = 1; creeper: letrero("DO-WHILE: " + to_texto(k)); k = k + 1; boom  (k <= 3);',
    "creeper con boom con espacios"
)

# ============================================================================
# CASO 8: Mapas y diccionarios
# ============================================================================
test_case(
    "8. mapa con diccionario",
    'mapa<texto,bloques> cofres = {"oro": 5, "diamante": 3, "esmeralda": 1}; letrero("Cofres: " + to_texto(length(cofres)));',
    "mapa con diccionario - los ':' internos no deben separarse"
)

# ============================================================================
# CASO 9: Inventarios (listas)
# ============================================================================
test_case(
    "9. inventario con lista",
    'inventario<texto> items = ["espada", "pico", "antorcha"]; inventario<bloques> numeros = [1, 2, 3, 4, 5];',
    "inventario con listas"
)

# ============================================================================
# CASO 10: Strings con comillas simples y dobles
# ============================================================================
test_case(
    "10. strings mixtos",
    '''letrero("Texto con comillas dobles"); letrero('Texto con comillas simples'); letrero("Texto con 'comillas' internas");''',
    "strings con comillas dobles y simples"
)

# ============================================================================
# CASO 11: mesa_crafteo (funciones) con diferentes estructuras
# ============================================================================
test_case(
    "11. mesa_crafteo simple",
    'mesa_crafteo bloques suma(bloques a, bloques b): craftear a + b; fin',
    "función simple con craftear"
)

test_case(
    "11b. mesa_crafteo con cuerpo",
    'mesa_crafteo bloques factorial(bloques n): observador(n <= 1): craftear 1; fin craftear n * factorial(n - 1); fin',
    "función recursiva con observador"
)

# ============================================================================
# CASO 12: Ejemplo completo con múltiples estructuras anidadas
# ============================================================================
test_case(
    "12. ejemplo completo",
    '''mesa_crafteo vacío main(): bloques x = 10; observador  (x > 5): letrero("x es mayor que 5"); comparador(x == 10): letrero("x es exactamente 10"); dispensador: letrero("x es menor o igual a 5"); fin bloques i = 0; spawner  (i < 3): letrero("Iteración: " + to_texto(i)); i = i + 1; romper bloques j = 0; creeper: letrero("Do-while: " + to_texto(j)); j = j + 1; boom  (j < 2); mapa<texto,bloques> items = {"oro": 5, "diamante": 3}; inventario<texto> nombres = ["Steve", "Alex"]; fin''',
    "Programa completo con todas las estructuras"
)

# ============================================================================
# CASO 13: Comentarios
# ============================================================================
test_case(
    "13. comentarios",
    '''# Este es un comentario
bloques x = 5; # comentario al final
letrero("hola"); # otro comentario''',
    "comentarios deben ser preservados"
)

# ============================================================================
# CASO 14: Casos especiales de closers
# ============================================================================
test_case(
    "14. todos los closers",
    '''mesa_crafteo vacío test(): observador(true): letrero("observador"); fin spawner(true): romper cultivar(i=0;i<1;i=i+1): cosechar portal(1): caso 1: romper salir_portal fin''',
    "todos los tipos de closers: fin, romper, cosechar, salir_portal"
)

# ============================================================================
# CASO 15: Operadores compuestos
# ============================================================================
test_case(
    "15. operadores compuestos",
    'bloques x = 10; x += 5; x -= 3; x *= 2; x /= 4; x %= 3;',
    "operadores compuestos +=, -=, *=, /=, %="
)

# ============================================================================
# CASO 16: Llamadas a funciones con múltiples argumentos
# ============================================================================
test_case(
    "16. funciones con argumentos",
    'letrero(to_texto(suma(5, 3))); push(inventario, "item"); tiene(mapa, "clave");',
    "llamadas a funciones con argumentos - los paréntesis internos no deben separar"
)

# ============================================================================
# CASO 17: Expresiones complejas
# ============================================================================
test_case(
    "17. expresiones complejas",
    'bloques resultado = (x + y) * (z - w) / 2; observador((a > b) y (c < d)): letrero("complejo"); fin',
    "expresiones con múltiples paréntesis anidados"
)

# ============================================================================
# CASO 18: Acceso a índices y propiedades
# ============================================================================
test_case(
    "18. acceso a elementos",
    'bloques valor = lista[0]; mapa["clave"] = 100; letrero(cofres["oro"]);',
    "acceso a elementos de inventarios y mapas"
)

# ============================================================================
# RESUMEN
# ============================================================================
print("=" * 70)
print("RESUMEN DE TESTS EJECUTADOS")
print("=" * 70)
print("✓ 18 casos de test completados")
print("Estructuras probadas:")
print("  - boom con espacios variables")
print("  - observador/comparador/dispensador con espacios")
print("  - spawner con espacios")
print("  - cultivar con espacios")
print("  - portal con espacios")
print("  - creeper/boom completo")
print("  - mapas y diccionarios")
print("  - inventarios/listas")
print("  - strings con comillas simples y dobles")
print("  - mesa_crafteo (funciones)")
print("  - ejemplo completo anidado")
print("  - comentarios")
print("  - todos los closers")
print("  - operadores compuestos")
print("  - funciones con argumentos")
print("  - expresiones complejas")
print("  - acceso a índices")
print("=" * 70)
