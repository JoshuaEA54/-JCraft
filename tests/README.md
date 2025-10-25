# Tests de :JCraft

Esta carpeta contiene tests automatizados para verificar todas las características del lenguaje :JCraft.

## 📁 Archivos de Test

| Archivo | Descripción |
|---------|-------------|
| `test_aritmetica.jcraft` | Operadores aritméticos (+, -, *, /, %) |
| `test_logicos.jcraft` | Operadores lógicos (y, o, no) |
| `test_loops.jcraft` | Estructuras de repetición (for, while, do-while) |
| `test_funciones.jcraft` | Declaración de funciones y recursividad |
| `test_listas.jcraft` | Manejo de listas (inventario) |
| `test_mapas.jcraft` | Manejo de diccionarios (mapa) |
| `test_conversiones.jcraft` | Conversiones entre tipos |
| `test_menu.jcraft` | Switch/case (portal) |

## 🚀 Ejecutar Tests

### Todos los tests
```bash
python run_all_tests.py
```

### Test individual
```bash
python tests/test_runner.py
# Luego abre y ejecuta cualquier archivo .jcraft individual
```

## ✅ Resultados Esperados

Todos los tests deben pasar con el mensaje:
```
🎉 ¡Todos los tests pasaron exitosamente!
```

## 📝 Crear Nuevos Tests

Para crear un nuevo test:

1. Crea un archivo `test_nombre.jcraft` en esta carpeta
2. Incluye un mensaje de inicio y fin:
   ```jcraft
   mesa_crafteo vacío main():
       letrero("=== Test: Nombre ===");
       
       // tu código de test aquí
       
       letrero("✓ Test completado");
   fin
   ```
3. Ejecuta `run_all_tests.py` para verificarlo

## 🎯 Cobertura

Los tests actuales cubren:
- ✅ Todos los tipos de datos
- ✅ Todas las estructuras de control
- ✅ Funciones y recursividad
- ✅ Operadores aritméticos y lógicos
- ✅ Colecciones (listas y mapas)
- ✅ Conversiones de tipo
- ✅ Entrada/salida básica
