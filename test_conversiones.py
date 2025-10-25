"""
Test de conversiones de tipo: to_bloques, to_coordenada, to_texto, to_redstone, to_glifo
"""
from lang.lexer import tokenize
from lang.parser import Parser
from lang.interpreter import Interpreter

def test_conversiones_basicas():
    print("=" * 60)
    print("TEST 1: Conversiones básicas de tipo")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        texto s = "15";
        bloques n = to_bloques(s);
        coordenada f = to_coordenada("3.14");
        redstone r = to_redstone("verdadero");
        glifo g = to_glifo("#");
        
        letrero "Texto: " + s;
        letrero "Bloques: " + n;
        letrero "Coordenada: " + f;
        letrero "Redstone: " + r;
        letrero "Glifo: " + g;
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
    print("  Texto: 15")
    print("  Bloques: 15")
    print("  Coordenada: 3.14")
    print("  Redstone: True")
    print("  Glifo: #")

def test_to_bloques():
    print("\n" + "=" * 60)
    print("TEST 2: to_bloques - Conversión a enteros")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        bloques a = to_bloques("42");
        bloques b = to_bloques(3.14);
        bloques c = to_bloques(verdadero);
        bloques d = to_bloques(falso);
        
        letrero "De texto '42': " + a;
        letrero "De float 3.14: " + b;
        letrero "De verdadero: " + c;
        letrero "De falso: " + d;
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

def test_to_coordenada():
    print("\n" + "=" * 60)
    print("TEST 3: to_coordenada - Conversión a flotantes")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        coordenada a = to_coordenada("2.5");
        coordenada b = to_coordenada(10);
        coordenada c = to_coordenada("100");
        
        letrero "De texto '2.5': " + a;
        letrero "De entero 10: " + b;
        letrero "De texto '100': " + c;
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

def test_to_texto():
    print("\n" + "=" * 60)
    print("TEST 4: to_texto - Conversión a cadenas")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        texto a = to_texto(42);
        texto b = to_texto(3.14);
        texto c = to_texto(verdadero);
        texto d = to_texto(falso);
        inventario<bloques> lista = [1, 2, 3];
        texto e = to_texto(lista);
        
        letrero "De bloques 42: '" + a + "'";
        letrero "De coordenada 3.14: '" + b + "'";
        letrero "De verdadero: '" + c + "'";
        letrero "De falso: '" + d + "'";
        letrero "De lista: '" + e + "'";
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

def test_to_redstone():
    print("\n" + "=" * 60)
    print("TEST 5: to_redstone - Conversión a booleanos")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        redstone a = to_redstone("verdadero");
        redstone b = to_redstone("falso");
        redstone c = to_redstone("true");
        redstone d = to_redstone("false");
        redstone e = to_redstone("1");
        redstone f = to_redstone("0");
        redstone g = to_redstone(1);
        redstone h = to_redstone(0);
        
        letrero "De 'verdadero': " + a;
        letrero "De 'falso': " + b;
        letrero "De 'true': " + c;
        letrero "De 'false': " + d;
        letrero "De '1': " + e;
        letrero "De '0': " + f;
        letrero "De número 1: " + g;
        letrero "De número 0: " + h;
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

def test_to_glifo():
    print("\n" + "=" * 60)
    print("TEST 6: to_glifo - Conversión a caracteres")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        glifo a = to_glifo("A");
        glifo b = to_glifo("#");
        glifo c = to_glifo("5");
        
        letrero "Carácter A: " + a;
        letrero "Carácter #: " + b;
        letrero "Carácter 5: " + c;
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

def test_conversiones_con_entrada():
    print("\n" + "=" * 60)
    print("TEST 7: Conversiones con cofre() - Entrada de usuario")
    print("=" * 60)
    
    codigo = '''
    mesa_crafteo vacío main():
        letrero "Conversión automática de entrada";
        bloques edad = to_bloques("25");
        coordenada altura = to_coordenada("1.75");
        
        letrero "Edad (bloques): " + edad;
        letrero "Altura (coordenada): " + altura;
        letrero "Tipo de dato preservado";
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

def test_errores_conversion():
    print("\n" + "=" * 60)
    print("TEST 8: Manejo de errores en conversiones")
    print("=" * 60)
    
    # Test to_bloques con texto inválido
    print("\n8.1: to_bloques con texto inválido")
    codigo = '''
    mesa_crafteo vacío main():
        bloques n = to_bloques("hola");
    fin
    '''
    
    try:
        tokens = tokenize(codigo)
        parser = Parser(tokens)
        ast = parser.parse()
        interp = Interpreter()
        interp.run(ast)
        print("  ❌ No se generó error (esperado)")
    except Exception as e:
        print(f"  ✅ Error capturado: {e}")
    
    # Test to_glifo con cadena larga
    print("\n8.2: to_glifo con cadena larga")
    codigo = '''
    mesa_crafteo vacío main():
        glifo g = to_glifo("ABC");
    fin
    '''
    
    try:
        tokens = tokenize(codigo)
        parser = Parser(tokens)
        ast = parser.parse()
        interp = Interpreter()
        interp.run(ast)
        print("  ❌ No se generó error (esperado)")
    except Exception as e:
        print(f"  ✅ Error capturado: {e}")

if __name__ == "__main__":
    test_conversiones_basicas()
    test_to_bloques()
    test_to_coordenada()
    test_to_texto()
    test_to_redstone()
    test_to_glifo()
    test_conversiones_con_entrada()
    test_errores_conversion()
    
    print("\n" + "=" * 60)
    print("TODOS LOS TESTS DE CONVERSIONES COMPLETADOS ✅")
    print("=" * 60)
