"""
Tests del sistema de validación de tipos estático
"""

from lang.lexer import Lexer
from lang.parser import Parser
from lang.type_checker import TypeChecker
from lang.interpreter import InterpreterError
import sys


def test_type_check_valid_program():
    """Test: Programa válido sin errores de tipo"""
    code = """
    mesa_crafteo bloques sumar(bloques a, bloques b):
        craftear a + b;
    fin
    
    mesa_crafteo vacío main():
        bloques x = 10;
        bloques z = 20;
        bloques suma = sumar(x, z);
        letrero suma;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 1: Programa válido")
    if is_valid:
        print("✅ PASÓ - No hay errores de tipo\n")
    else:
        print("❌ FALLÓ - Se detectaron errores:")
        checker.print_errors()
        print()


def test_type_check_incompatible_assignment():
    """Test: Detecta asignación de tipo incompatible"""
    code = """
    mesa_crafteo vacío main():
        bloques x = 10;
        x = "texto";
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 2: Asignación incompatible")
    if not is_valid and len(checker.errors) > 0:
        print("✅ PASÓ - Detectó error de tipo:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_wrong_return_type():
    """Test: Detecta tipo de retorno incorrecto"""
    code = """
    mesa_crafteo bloques obtener_numero():
        craftear "texto";
    fin
    
    mesa_crafteo vacío main():
        bloques x = obtener_numero();
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 3: Tipo de retorno incorrecto")
    if not is_valid:
        print("✅ PASÓ - Detectó error de tipo:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_invalid_operation():
    """Test: Detecta operación inválida entre tipos"""
    code = """
    mesa_crafteo vacío main():
        bloques x = 10;
        texto s = "hola";
        bloques suma = x * s;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 4: Operación inválida (bloques * texto)")
    if not is_valid:
        print("✅ PASÓ - Detectó error de tipo:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_condition_not_boolean():
    """Test: Detecta condición no booleana"""
    code = """
    mesa_crafteo vacío main():
        bloques x = 10;
        observador (x):
            letrero "Esto está mal";
        fin
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 5: Condición no booleana")
    if not is_valid:
        print("✅ PASÓ - Detectó error de tipo:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_list_inconsistent_types():
    """Test: Detecta lista con tipos inconsistentes"""
    code = """
    mesa_crafteo vacío main():
        inventario<bloques> nums = [1, 2, "tres", 4];
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 6: Lista con tipos inconsistentes")
    if not is_valid:
        print("✅ PASÓ - Detectó error de tipo:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_undeclared_variable():
    """Test: Detecta variable no declarada"""
    code = """
    mesa_crafteo vacío main():
        bloques x = y + 10;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 7: Variable no declarada")
    if not is_valid:
        print("✅ PASÓ - Detectó error:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_valid_collections():
    """Test: Programa válido con colecciones"""
    code = """
    mesa_crafteo vacío main():
        inventario<bloques> nums = [1, 2, 3];
        mapa<texto,bloques> stats = {"vida": 100, "mana": 50};
        
        bloques primero = nums[0];
        bloques vida = stats["vida"];
        
        nums[0] = 42;
        stats["mana"] = 75;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 8: Colecciones válidas")
    if is_valid:
        print("✅ PASÓ - No hay errores de tipo\n")
    else:
        print("❌ FALLÓ - Se detectaron errores:")
        checker.print_errors()
        print()


def test_type_check_main_validation():
    """Test: Detecta main con firma incorrecta"""
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
    
    print("Test 9: Main con tipo de retorno incorrecto")
    if not is_valid:
        print("✅ PASÓ - Detectó error:")
        for error in checker.errors:
            print(f"   → {error}")
        print()
    else:
        print("❌ FALLÓ - No detectó el error\n")


def test_type_check_number_promotion():
    """Test: Promoción de bloques a coordenada"""
    code = """
    mesa_crafteo vacío main():
        bloques x = 10;
        coordenada z = 3.14;
        coordenada suma = x + z;
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 10: Promoción bloques → coordenada")
    if is_valid:
        print("✅ PASÓ - Acepta promoción de tipos\n")
    else:
        print("❌ FALLÓ - No debería haber errores:")
        checker.print_errors()
        print()


def test_type_check_integration():
    """Test de integración: Programa complejo"""
    code = """
    mesa_crafteo bloques factorial(bloques n):
        observador (n <= 1):
            craftear 1;
        fin
        craftear n * factorial(n - 1);
    fin
    
    mesa_crafteo vacío main():
        bloques num = 5;
        bloques fact = factorial(num);
        letrero "Factorial de " + to_texto(num) + " es " + to_texto(fact);
    fin
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    checker = TypeChecker()
    is_valid = checker.check(ast)
    
    print("Test 11: Programa complejo (factorial recursivo)")
    if is_valid:
        print("✅ PASÓ - No hay errores de tipo\n")
    else:
        print("❌ FALLÓ - Se detectaron errores:")
        checker.print_errors()
        print()


if __name__ == "__main__":
    print("="*60)
    print("TESTS DEL SISTEMA DE TIPOS ESTÁTICO")
    print("="*60)
    print()
    
    test_type_check_valid_program()
    test_type_check_incompatible_assignment()
    test_type_check_wrong_return_type()
    test_type_check_invalid_operation()
    test_type_check_condition_not_boolean()
    test_type_check_list_inconsistent_types()
    test_type_check_undeclared_variable()
    test_type_check_valid_collections()
    test_type_check_main_validation()
    test_type_check_number_promotion()
    test_type_check_integration()
    
    print("="*60)
    print("TESTS COMPLETADOS")
    print("="*60)
