# :JCraft - Guía Rápida de Referencia

## 📋 Tipos de Datos

```jcraft
bloques entero = 42;              // int
coordenada decimal = 3.14;        // float
texto cadena = "Hola";            // string
glifo caracter = 'A';             // char
redstone booleano = verdadero;    // boolean
inventario<bloques> lista = [1, 2, 3];  // list
mapa<texto, bloques> dict = {};   // dictionary
```

## 🔄 Estructuras de Control

### If-Else
```jcraft
observador (condicion):
    // código
comparador (otra_condicion):
    // código
dispensador:
    // código
fin
```

### While
```jcraft
spawner (condicion):
    // código
romper
```

### For
```jcraft
bloques i = 0;
cultivar (i = 0; i < 10; i = i + 1):
    // código
cosechar
```

### Do-While
```jcraft
creeper:
    // código
boom (condicion)
```

### Switch
```jcraft
portal (variable):
    caso "valor1":
        // código
    caso "valor2":
        // código
    defecto:
        // código
salir_portal
```

## 🎯 Funciones

```jcraft
// Con retorno
mesa_crafteo bloques suma(bloques a, bloques b):
    craftear a + b;
fin

// Sin retorno
mesa_crafteo vacío mensaje():
    letrero("Hola");
fin

// Main (obligatorio)
mesa_crafteo vacío main():
    // tu código aquí
fin
```

## 🔢 Operadores

### Aritméticos
```jcraft
+ - * / %
+= -= *= /= %=
```

### Comparación
```jcraft
== != < > <= >=
```

### Lógicos
```jcraft
y    // AND
o    // OR
no   // NOT
```

## 📥📤 Entrada/Salida

```jcraft
letrero("Texto");           // Imprimir
texto entrada = cofre();    // Leer entrada
```

## 🔄 Conversiones

```jcraft
to_bloques("123")      // → bloques
to_coordenada("3.14")  // → coordenada
to_texto(42)           // → texto
to_glifo("A")          // → glifo
```

## 📦 Colecciones

### Listas
```jcraft
inventario<bloques> nums = [1, 2, 3];
bloques primero = nums[0];
nums[1] = 10;
```

### Diccionarios
```jcraft
mapa<texto, bloques> items = {};
items["oro"] = 10;
bloques cantidad = items["oro"];
```

## ⚠️ Reglas Importantes

1. ✅ Siempre termina con `;`
2. ✅ Bloques terminan con `fin`
3. ✅ Declara variables con tipo
4. ✅ `main()` es obligatorio
5. ✅ Solo un `main()` por programa
6. ✅ `"texto"` para strings, `'c'` para chars

## 🎮 Palabras Clave Minecraft

| JCraft | Tradicional |
|--------|-------------|
| `observador` | if |
| `comparador` | else if |
| `dispensador` | else |
| `spawner` | while |
| `cultivar` | for |
| `creeper/boom` | do-while |
| `portal` | switch |
| `mesa_crafteo` | function |
| `craftear` | return |
| `letrero` | print |
| `cofre` | input |

## 📝 Ejemplo Completo

```jcraft
mesa_crafteo bloques factorial(bloques n):
    observador (n <= 1):
        craftear 1;
    fin
    craftear n * factorial(n - 1);
fin

mesa_crafteo vacío main():
    letrero("Ingresa un número:");
    texto entrada = cofre();
    bloques num = to_bloques(entrada);
    
    bloques resultado = factorial(num);
    letrero("Factorial: " + to_texto(resultado));
fin
```

---
💡 **Tip**: Usa el menú "Insertar Código" del IDE para acceder a más de 50 ejemplos.
