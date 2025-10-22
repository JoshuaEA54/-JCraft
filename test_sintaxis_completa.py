"""
Test completo de la sintaxis de JCraft según la especificación
"""
from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import run_source

def test_sintaxis():
    print("=" * 60)
    print("VERIFICACIÓN DE SINTAXIS SEGÚN ESPECIFICACIÓN JCRAFT")
    print("=" * 60)
    
    # 1. PALABRAS RESERVADAS - Verificar que todas estén en el lexer
    print("\n1. Palabras reservadas:")
    from lang.lexer import KEYWORDS
    especificadas = {
        'cultivar', 'cosechar', 'observador', 'comparador', 'dispensador',
        'creeper', 'boom', 'portal', 'caso', 'defecto', 'salir_portal',
        'spawner', 'romper', 'mesa_crafteo', 'craftear', 'letrero', 'cofre',
        'verdadero', 'falso', 'nulo', 'bloques', 'coordenada', 'texto',
        'redstone', 'glifo', 'inventario', 'mapa', 'vacío', 'y', 'o', 'no',
        'fin'
    }
    
    # Añadir 'continuar' que falta en la spec pero está implementado
    implementadas = KEYWORDS
    
    faltantes = especificadas - implementadas
    extras = implementadas - especificadas
    
    if faltantes:
        print(f"   ❌ FALTAN: {faltantes}")
    if extras:
        print(f"   ⚠️  EXTRAS (no en spec): {extras}")
    if not faltantes and not extras:
        print("   ✅ Todas las palabras reservadas coinciden")
    
    # 2. SINTAXIS DE CONTROL - FOR
    print("\n2. Sintaxis FOR (cultivar...cosechar):")
    codigo_for = '''
    mesa_crafteo vacío main():
        cultivar (i = 0; i < 5; i = i + 1):
            letrero "Parcela " + i;
        cosechar
    fin
    '''
    try:
        tokens = tokenize(codigo_for)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis FOR correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. SINTAXIS IF/ELSE IF/ELSE
    print("\n3. Sintaxis IF/ELSE IF/ELSE (observador/comparador/dispensador):")
    codigo_if = '''
    mesa_crafteo vacío main():
        texto pico = "diamante";
        observador (pico == "diamante"):
            letrero "Tienes el mejor pico";
        comparador (pico == "hierro"):
            letrero "Buen pico intermedio";
        dispensador:
            letrero "Mejor actualiza tu herramienta";
        fin
    fin
    '''
    try:
        tokens = tokenize(codigo_if)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis IF correcta (requiere 'fin' al final)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. SINTAXIS DO-WHILE
    print("\n4. Sintaxis DO-WHILE (creeper...boom):")
    codigo_dowhile = '''
    mesa_crafteo vacío main():
        bloques contador = 0;
        creeper:
            letrero "Iteración";
            contador = contador + 1;
        boom (contador < 3);
    fin
    '''
    try:
        tokens = tokenize(codigo_dowhile)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis DO-WHILE correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. SINTAXIS SWITCH
    print("\n5. Sintaxis SWITCH (portal...caso...defecto...salir_portal):")
    codigo_switch = '''
    mesa_crafteo vacío main():
        texto bioma = "jungla";
        portal (bioma):
            caso "jungla":
                letrero "Estás rodeado de árboles gigantes";
            caso "desierto":
                letrero "Prepárate para el calor y husks";
            defecto:
                letrero "Bioma no identificado";
        salir_portal
    fin
    '''
    try:
        tokens = tokenize(codigo_switch)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis SWITCH correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. SINTAXIS WHILE
    print("\n6. Sintaxis WHILE (spawner...romper):")
    codigo_while = '''
    mesa_crafteo vacío main():
        bloques vidas = 3;
        spawner (vidas > 0):
            letrero "Tienes vidas";
            vidas = vidas - 1;
        romper
    fin
    '''
    try:
        tokens = tokenize(codigo_while)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis WHILE correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. FUNCIONES
    print("\n7. Sintaxis FUNCIONES (mesa_crafteo...craftear...fin):")
    codigo_func = '''
    mesa_crafteo bloques sumar(bloques a, bloques b):
        craftear a + b;
    fin
    
    mesa_crafteo vacío saludar(texto quien):
        letrero "Hola, " + quien;
    fin
    
    mesa_crafteo vacío main():
        bloques resultado = sumar(5, 3);
        letrero resultado;
        saludar("Alex");
    fin
    '''
    try:
        tokens = tokenize(codigo_func)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis FUNCIONES correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 8. ENTRADA/SALIDA
    print("\n8. Sintaxis ENTRADA/SALIDA (letrero/cofre):")
    codigo_io = '''
    mesa_crafteo vacío main():
        letrero "Ingresa tu nombre:";
    fin
    '''
    try:
        tokens = tokenize(codigo_io)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis I/O correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 9. TIPOS DE DATOS
    print("\n9. Declaración de TIPOS:")
    codigo_tipos = '''
    mesa_crafteo vacío main():
        bloques entero = 42;
        coordenada flotante = 3.14;
        texto cadena = "Hola";
        redstone booleano = verdadero;
        glifo caracter = 'A';
    fin
    '''
    try:
        tokens = tokenize(codigo_tipos)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis TIPOS correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 10. OPERADORES
    print("\n10. OPERADORES:")
    codigo_ops = '''
    mesa_crafteo vacío main():
        bloques a = 10;
        bloques b = 5;
        bloques suma = a + b;
        bloques resta = a - b;
        bloques mult = a * b;
        bloques div = a / b;
        bloques mod = a % b;
        redstone igual = a == b;
        redstone diferente = a != b;
        redstone menor = a < b;
        redstone mayor = a > b;
        redstone menorigual = a <= b;
        redstone mayorigual = a >= b;
        redstone and_logico = verdadero y falso;
        redstone or_logico = verdadero o falso;
        redstone not_logico = no verdadero;
    fin
    '''
    try:
        tokens = tokenize(codigo_ops)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis OPERADORES correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 11. COMENTARIOS
    print("\n11. COMENTARIOS:")
    codigo_comentarios = '''
    # Comentario de línea
    mesa_crafteo vacío main():
        bloques x = 10; # comentario al final
        /* Comentario
           multilínea */
        letrero x;
    fin
    '''
    try:
        tokens = tokenize(codigo_comentarios)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis COMENTARIOS correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 12. BREAK Y CONTINUE
    print("\n12. BREAK y CONTINUE (romper/continuar):")
    codigo_break = '''
    mesa_crafteo vacío main():
        bloques i = 0;
        spawner (i < 10):
            observador (i == 5):
                romper();
            fin
            letrero i;
            i = i + 1;
        romper
    fin
    '''
    try:
        tokens = tokenize(codigo_break)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ✅ Sintaxis BREAK correcta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 13. MAIN OBLIGATORIO
    print("\n13. MAIN obligatorio:")
    codigo_sin_main = '''
    mesa_crafteo bloques suma(bloques a, bloques b):
        craftear a + b;
    fin
    '''
    try:
        tokens = tokenize(codigo_sin_main)
        parser = Parser(tokens)
        ast = parser.parse()
        print("   ⚠️  Parser acepta código sin main (validación pendiente)")
    except Exception as e:
        print(f"   ✅ Rechaza código sin main: {e}")
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_sintaxis()
