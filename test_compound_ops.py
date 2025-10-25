"""
Test de operadores de asignación compuestos (+=, -=, *=, /=, %=)
"""

from lang.lexer import Lexer
from lang.parser import Parser
from lang.interpreter import Interpreter


def test_basic_compound_ops():
    """Test operadores compuestos básicos con variables simples"""
    code = """
    mesa_crafteo bloques main():
        bloques x = 10;
        letrero x;
        
        x += 5;
        letrero x;
        
        x -= 3;
        letrero x;
        
        x *= 2;
        letrero x;
        
        x /= 4;
        letrero x;
        
        x %= 5;
        letrero x;
        
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    # Esperamos: 10, 15, 12, 24, 6.0, 1.0 (división retorna float)
    expected = ['10', '15', '12', '24', '6.0', '1.0']
    print("✅ test_basic_compound_ops - Output:", result)
    assert result == expected, f"Expected {expected}, got {result}"


def test_compound_with_texto():
    """Test += con concatenación de texto"""
    code = """
    mesa_crafteo bloques main():
        texto s = "Hola";
        letrero s;
        
        s += " Mundo";
        letrero s;
        
        s += "!";
        letrero s;
        
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    expected = ["Hola", "Hola Mundo", "Hola Mundo!"]
    print("✅ test_compound_with_texto - Output:", result)
    assert result == expected, f"Expected {expected}, got {result}"


def test_compound_with_coordenada():
    """Test operadores compuestos con flotantes"""
    code = """
    mesa_crafteo bloques main():
        coordenada pi = 3.14;
        letrero pi;
        
        pi *= 2.0;
        letrero pi;
        
        pi += 1.0;
        letrero pi;
        
        pi /= 7.28;
        letrero pi;
        
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    print("✅ test_compound_with_coordenada - Output:", result)
    assert len(result) == 4
    assert abs(float(result[0]) - 3.14) < 0.01
    assert abs(float(result[1]) - 6.28) < 0.01
    assert abs(float(result[2]) - 7.28) < 0.01
    assert abs(float(result[3]) - 1.0) < 0.01


def test_compound_in_loop():
    """Test operadores compuestos en bucles"""
    code = """
    mesa_crafteo bloques main():
        bloques suma = 0;
        bloques i = 1;
        
        spawner (i <= 5):
            suma += i;
            i += 1;
        romper
        
        letrero suma;
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    # suma = 1 + 2 + 3 + 4 + 5 = 15
    expected = ['15']
    print("✅ test_compound_in_loop - Output:", result)
    assert result == expected, f"Expected {expected}, got {result}"


def test_compound_with_index():
    """Test operadores compuestos con indexación"""
    code = """
    mesa_crafteo bloques main():
        inventario<bloques> nums = [10, 20, 30];
        
        letrero nums[0];
        nums[0] += 5;
        letrero nums[0];
        
        nums[1] *= 2;
        letrero nums[1];
        
        nums[2] -= 10;
        letrero nums[2];
        
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    expected = ['10', '15', '40', '20']
    print("✅ test_compound_with_index - Output:", result)
    assert result == expected, f"Expected {expected}, got {result}"


def test_compound_complex_expr():
    """Test operadores compuestos con expresiones complejas"""
    code = """
    mesa_crafteo bloques main():
        bloques x = 5;
        bloques z = 3;
        
        x += z * 2;
        letrero x;
        
        z *= x - 5;
        letrero z;
        
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    # x = 5 + (3 * 2) = 11
    # z = 3 * (11 - 5) = 18
    expected = ['11', '18']
    print("✅ test_compound_complex_expr - Output:", result)
    assert result == expected, f"Expected {expected}, got {result}"


def test_all_operators():
    """Test todos los operadores compuestos en secuencia"""
    code = """
    mesa_crafteo bloques main():
        bloques val = 100;
        letrero "Inicial:";
        letrero val;
        
        val += 50;
        letrero "Después de +=50:";
        letrero val;
        
        val -= 30;
        letrero "Después de -=30:";
        letrero val;
        
        val *= 2;
        letrero "Después de *=2:";
        letrero val;
        
        val /= 3;
        letrero "Después de /=3:";
        letrero val;
        
        val %= 30;
        letrero "Después de %=30:";
        letrero val;
        
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    result = interp.run(ast)
    
    # 100, +50=150, -30=120, *2=240, /3=80, %30=20 (división y módulo retornan float)
    expected = [
        "Inicial:", '100',
        "Después de +=50:", '150',
        "Después de -=30:", '120',
        "Después de *=2:", '240',
        "Después de /=3:", '80.0',
        "Después de %=30:", '20.0'
    ]
    print("✅ test_all_operators - Output:", result)
    assert result == expected, f"Expected {expected}, got {result}"


if __name__ == "__main__":
    print("🧪 Ejecutando tests de operadores compuestos...\n")
    
    test_basic_compound_ops()
    test_compound_with_texto()
    test_compound_with_coordenada()
    test_compound_in_loop()
    test_compound_with_index()
    test_compound_complex_expr()
    test_all_operators()
    
    print("\n" + "="*60)
    print("✅ TODOS LOS TESTS DE OPERADORES COMPUESTOS PASARON")
    print("="*60)
    print("\nOperadores implementados:")
    print("  ✅ += (suma/concatenación)")
    print("  ✅ -= (resta)")
    print("  ✅ *= (multiplicación)")
    print("  ✅ /= (división)")
    print("  ✅ %= (módulo)")
    print("\nFunciona con:")
    print("  ✅ Variables simples")
    print("  ✅ Variables indexadas (listas/mapas)")
    print("  ✅ Texto (concatenación con +=)")
    print("  ✅ Números enteros y flotantes")
    print("  ✅ Expresiones complejas")
