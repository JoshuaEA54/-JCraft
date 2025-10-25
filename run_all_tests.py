"""
Test Runner para :JCraft
Ejecuta todos los archivos de test y reporta resultados
"""
from lang.interpreter import run_source
import os
from pathlib import Path

def run_test_file(filepath):
    """Ejecuta un archivo de test y retorna el resultado"""
    print(f"\n{'='*60}")
    print(f"Ejecutando: {filepath}")
    print('='*60)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Ejecutar sin debug para salida limpia
        output = run_source(code, input_callback=lambda p: "test_input", debug=False)
        
        print("\n".join(output))
        print(f"✓ {filepath} - PASÓ")
        return True
    except Exception as e:
        print(f"✗ {filepath} - FALLÓ")
        print(f"Error: {e}")
        return False

def main():
    """Ejecuta todos los tests en la carpeta tests/"""
    tests_dir = Path("tests")
    
    if not tests_dir.exists():
        print("No se encontró la carpeta 'tests/'")
        return
    
    # Encontrar todos los archivos .jcraft en tests/
    test_files = sorted(tests_dir.glob("test_*.jcraft"))
    
    if not test_files:
        print("No se encontraron archivos de test")
        return
    
    print(f"\n{'#'*60}")
    print(f"# :JCraft Test Suite - {len(test_files)} tests encontrados")
    print(f"{'#'*60}")
    
    results = []
    for test_file in test_files:
        result = run_test_file(test_file)
        results.append((test_file.name, result))
    
    # Resumen
    print(f"\n{'='*60}")
    print("RESUMEN DE TESTS")
    print('='*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status:12} - {name}")
    
    print(f"\n{passed}/{len(results)} tests pasaron")
    
    if failed == 0:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
    else:
        print(f"⚠️  {failed} test(s) fallaron")

if __name__ == "__main__":
    main()
