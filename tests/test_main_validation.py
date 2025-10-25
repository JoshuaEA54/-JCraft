"""
Tests adicionales para validaciones estrictas de main
"""

from lang.lexer import Lexer
from lang.parser import Parser
from lang.type_checker import TypeChecker


def test_no_main():
    """Test: Detecta ausencia de main"""
    code = """
    mesa_crafteo bloques sumar(bloques a, bloques b):
        craftear a + b;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 1: Sin función main")
    if not is_valid and any('main' in error and 'no encontrada' in error for error in checker.errors):
        print("✅ PASÓ - Detectó ausencia de main:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
        return True
    else:
        print("❌ FALLÓ - No detectó la ausencia de main\n")
        return False


def test_multiple_main():
    """Test: Detecta múltiples funciones main"""
    code = """
    mesa_crafteo vacío main():
        letrero "Primera main";
    fin
    
    mesa_crafteo vacío main():
        letrero "Segunda main";
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 2: Múltiples funciones main")
    if not is_valid and any('main' in error and ('múltiples' in error or 'veces' in error) for error in checker.errors):
        print("✅ PASÓ - Detectó main duplicado:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
        return True
    else:
        print("❌ FALLÓ - No detectó main duplicado")
        if checker.errors:
            print("Errores encontrados:")
            for error in checker.errors:
                print(f"   → {error}")
        print()
        return False


def test_main_with_params():
    """Test: Detecta main con parámetros"""
    code = """
    mesa_crafteo vacío main(bloques argc):
        letrero argc;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 3: Main con parámetros")
    if not is_valid and any('main' in error and 'parámetro' in error for error in checker.errors):
        print("✅ PASÓ - Detectó main con parámetros:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
        return True
    else:
        print("❌ FALLÓ - No detectó main con parámetros\n")
        return False


def test_main_wrong_return_type():
    """Test: Detecta main con tipo de retorno incorrecto"""
    code = """
    mesa_crafteo bloques main():
        craftear 0;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 4: Main con tipo de retorno incorrecto")
    if not is_valid and any('main' in error and 'vacío' in error for error in checker.errors):
        print("✅ PASÓ - Detectó tipo de retorno incorrecto:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
        return True
    else:
        print("❌ FALLÓ - No detectó tipo de retorno incorrecto\n")
        return False


def test_valid_main():
    """Test: Acepta main válido"""
    code = """
    mesa_crafteo vacío main():
        letrero "Hola mundo";
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 5: Main válido")
    if is_valid:
        print("✅ PASÓ - Acepta main válido\n")
        return True
    else:
        print("❌ FALLÓ - Rechazó main válido:")
        checker.print_errors()
        print()
        return False


def test_duplicate_function():
    """Test: Detecta funciones duplicadas (no solo main)"""
    code = """
    mesa_crafteo bloques sumar(bloques a, bloques b):
        craftear a + b;
    fin
    
    mesa_crafteo bloques sumar(bloques x, bloques z):
        craftear x + z;
    fin
    
    mesa_crafteo vacío main():
        bloques total = sumar(1, 2);
        letrero total;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 6: Función duplicada (sumar)")
    if not is_valid and any('sumar' in error and 'múltiples' in error for error in checker.errors):
        print("✅ PASÓ - Detectó función duplicada:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
        return True
    else:
        print("❌ FALLÓ - No detectó función duplicada")
        if checker.errors:
            for error in checker.errors:
                print(f"   → {error}")
        print()
        return False


if __name__ == "__main__":
    print("="*60)
    print("TESTS DE VALIDACIONES ESTRICTAS DE MAIN")
    print("="*60)
    print()
    
    results = []
    results.append(test_no_main())
    results.append(test_multiple_main())
    results.append(test_main_with_params())
    results.append(test_main_wrong_return_type())
    results.append(test_valid_main())
    results.append(test_duplicate_function())
    
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTADOS: {passed}/{total} tests pasados")
    
    if passed == total:
        print("✅ TODAS LAS VALIDACIONES DE MAIN IMPLEMENTADAS")
    else:
        print(f"⚠️ {total - passed} test(s) fallaron")
    print("="*60)
