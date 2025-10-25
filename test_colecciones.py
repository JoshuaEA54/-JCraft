"""
Test de tipos compuestos: inventario<T> y mapa<K,V>
"""
from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import Interpreter

def test_listas():
    print("=" * 60)
    print("TEST 1: Listas (inventario<T>)")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        inventario<bloques> xs = [1, 2, 3];
        letrero "Lista completa: " + xs;
        letrero "Primer elemento: " + xs[0];
        letrero "Segundo elemento: " + xs[1];
        letrero "Tercer elemento: " + xs[2];
        xs[1] = 42;
        letrero "Elemento modificado: " + xs[1];
        letrero "Lista modificada: " + xs;
    fin
    '''
    
    tokens = tokenize(codigo)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter(debug=True)
    try:
        interp.run(ast)
    except Exception as e:
        print(f"\n❌ Error durante ejecución: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nSalida:")
    print(f"Total de líneas: {len(interp.results)}")
    for i, line in enumerate(interp.results):
        print(f"  [{i}] {repr(line)}")

def test_mapas():
    print("\n" + "=" * 60)
    print("TEST 2: Mapas (mapa<K,V>)")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        mapa<texto,bloques> m = {"vida": 10, "mana": 5};
        letrero "Mapa completo: " + m;
        letrero "Vida: " + m["vida"];
        letrero "Mana: " + m["mana"];
        m["mana"] = 7;
        letrero "Mana actualizado: " + m["mana"];
        m["energia"] = 100;
        letrero "Nueva clave energia: " + m["energia"];
        letrero "Mapa final: " + m;
    fin
    '''
    
    tokens = tokenize(codigo)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)
    
    print("\nSalida:")
    for line in interp.results:
        print(f"  {line}")

def test_funciones_colecciones():
    print("\n" + "=" * 60)
    print("TEST 3: Funciones de colecciones (length, push, pop, tiene)")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        inventario<bloques> nums = [10, 20, 30];
        letrero "Lista inicial: " + nums;
        letrero "Longitud: " + length(nums);
        
        push(nums, 40);
        letrero "Después de push(40): " + nums;
        letrero "Nueva longitud: " + length(nums);
        
        bloques ultimo = pop(nums);
        letrero "Pop retorna: " + ultimo;
        letrero "Lista después de pop: " + nums;
        
        mapa<texto,bloques> stats = {"fuerza": 10, "defensa": 8};
        letrero "Stats: " + stats;
        letrero "Tiene 'fuerza': " + tiene(stats, "fuerza");
        letrero "Tiene 'magia': " + tiene(stats, "magia");
    fin
    '''
    
    tokens = tokenize(codigo)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)
    
    print("\nSalida:")
    for line in interp.results:
        print(f"  {line}")

def test_listas_anidadas():
    print("\n" + "=" * 60)
    print("TEST 4: Listas anidadas (matriz)")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        inventario<inventario<bloques>> matriz = [[1, 2], [3, 4]];
        letrero "Matriz: " + matriz;
        letrero "Primera fila: " + matriz[0];
        letrero "Elemento [0][0]: " + matriz[0][0];
        letrero "Elemento [1][1]: " + matriz[1][1];
        matriz[0][1] = 99;
        letrero "Después de modificar [0][1]: " + matriz;
    fin
    '''
    
    tokens = tokenize(codigo)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)
    
    print("\nSalida:")
    for line in interp.results:
        print(f"  {line}")

def test_ejemplo_completo():
    print("\n" + "=" * 60)
    print("TEST 5: Ejemplo completo del spec")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        inventario<bloques> xs = [1, 2, 3];
        mapa<texto,bloques> m = {"vida": 10, "mana": 5};
        letrero "Primer elemento: " + xs[0];
        xs[1] = 42;
        letrero "Elemento modificado: " + xs[1];
        m["mana"] = 7;
        letrero "Mana: " + m["mana"];
    fin
    '''
    
    tokens = tokenize(codigo)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)
    
    print("\nSalida:")
    for line in interp.results:
        print(f"  {line}")
    
    print("\n✅ Salida esperada:")
    print("  Primer elemento: 1")
    print("  Elemento modificado: 42")
    print("  Mana: 7")

if __name__ == "__main__":
    test_listas()
    test_mapas()
    test_funciones_colecciones()
    # test_listas_anidadas()  # TODO: Soportar genéricos anidados
    test_ejemplo_completo()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETADOS (genéricos anidados pendientes)")
    print("=" * 60)
