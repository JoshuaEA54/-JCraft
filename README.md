# :JCraft - Lenguaje de Programación Inspirado en Minecraft

:JCraft es un lenguaje de programación educativo con sintaxis temática de Minecraft, diseñado para hacer la programación más divertida y accesible.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎮 Características

- **Sintaxis temática de Minecraft**: Usa términos del juego para conceptos de programación
- **Type checking estático**: Detecta errores antes de ejecutar
- **IDE integrado**: Editor con syntax highlighting y ejecución en tiempo real
- **Sistema de snippets**: Más de 50 ejemplos listos para usar
- **Soporte UTF-8**: Funciona perfectamente con español y otros idiomas
- **Mensajes de error claros**: Con número de línea y columna

## 🚀 Instalación

### Requisitos
- Python 3.13+
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/JoshuaEA54/-JCraft.git
cd -JCraft

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar el IDE
python main.py
```

## 📖 Sintaxis Básica

### Tipos de Datos

| Tipo JCraft | Equivalente | Ejemplo |
|-------------|-------------|---------|
| `bloques` | int | `bloques vida = 100;` |
| `coordenada` | float | `coordenada x = 10.5;` |
| `texto` | string | `texto nombre = "Steve";` |
| `glifo` | char | `glifo letra = 'A';` |
| `redstone` | boolean | `redstone activo = verdadero;` |
| `inventario<T>` | array/list | `inventario<bloques> nums = [1, 2, 3];` |
| `mapa<K,V>` | dictionary | `mapa<texto, bloques> items = {};` |
| `vacío` | void | `mesa_crafteo vacío main()` |

### Estructura de un Programa

```jcraft
# Todo programa necesita una función main
mesa_crafteo vacío main():
    letrero("¡Hola Minecraft!");
fin
```

### Funciones

```jcraft
# Función con retorno
mesa_crafteo bloques sumar(bloques a, bloques b):
    craftear a + b;
fin

# Función sin retorno
mesa_crafteo vacío saludar(texto nombre):
    letrero("Hola " + nombre);
fin

mesa_crafteo vacío main():
    bloques resultado = sumar(5, 3);
    letrero("Resultado: " + to_texto(resultado));
    saludar("Alex");
fin
```

### Estructuras de Control

#### If / Else (observador / comparador / dispensador)

```jcraft
mesa_crafteo vacío main():
    bloques vida = 80;
    
    observador (vida > 50):
        letrero("Tienes buena salud");
    comparador (vida > 20):
        letrero("Cuidado, poca vida");
    dispensador:
        letrero("¡Estás en peligro!");
    fin
fin
```

#### Bucle While (spawner / romper)

```jcraft
mesa_crafteo vacío main():
    bloques i = 1;
    
    spawner (i <= 5):
        letrero("Iteración: " + to_texto(i));
        i = i + 1;
    romper
fin
```

#### Bucle For (cultivar / cosechar)

```jcraft
mesa_crafteo vacío main():
    bloques i = 0;
    
    cultivar (i = 1; i <= 5; i = i + 1):
        letrero("Número: " + to_texto(i));
    cosechar
fin
```

#### Do-While (creeper / boom)

```jcraft
mesa_crafteo vacío main():
    bloques contador = 0;
    
    creeper:
        letrero("Contador: " + to_texto(contador));
        contador = contador + 1;
    boom (contador < 3)
fin
```

#### Switch (portal / caso / defecto / salir_portal)

```jcraft
mesa_crafteo vacío main():
    texto opcion = cofre();
    
    portal (opcion):
        caso "1":
            letrero("Opción 1 seleccionada");
        caso "2":
            letrero("Opción 2 seleccionada");
        defecto:
            letrero("Opción no válida");
    salir_portal
fin
```

### Operadores

#### Aritméticos
- `+` Suma
- `-` Resta
- `*` Multiplicación
- `/` División
- `%` Módulo

#### Comparación
- `==` Igual
- `!=` Diferente
- `<` Menor que
- `>` Mayor que
- `<=` Menor o igual
- `>=` Mayor o igual

#### Lógicos
- `y` AND
- `o` OR
- `no` NOT

#### Asignación Compuesta
- `+=` Sumar y asignar
- `-=` Restar y asignar
- `*=` Multiplicar y asignar
- `/=` Dividir y asignar
- `%=` Módulo y asignar

### Funciones Built-in

```jcraft
# Imprimir en consola
letrero("Hola mundo");

# Leer entrada del usuario
texto entrada = cofre();

# Conversiones de tipo
bloques num = to_bloques("123");
coordenada decimal = to_coordenada("3.14");
texto cadena = to_texto(42);
glifo caracter = to_glifo("A");
```

### Colecciones

#### Listas (inventario)

```jcraft
mesa_crafteo vacío main():
    # Crear lista
    inventario<bloques> numeros = [1, 2, 3, 4, 5];
    
    # Acceder elemento
    bloques primero = numeros[0];
    
    # Modificar elemento
    numeros[2] = 100;
    
    letrero("Primer elemento: " + to_texto(primero));
fin
```

#### Diccionarios (mapa)

```jcraft
mesa_crafteo vacío main():
    # Crear mapa vacío
    mapa<texto, bloques> recursos = {};
    
    # Agregar elementos
    recursos["oro"] = 10;
    recursos["hierro"] = 25;
    
    # Acceder elemento
    bloques oro = recursos["oro"];
    
    letrero("Oro disponible: " + to_texto(oro));
fin
```

## 🎯 Ejemplos Completos

### Calculadora Simple

```jcraft
mesa_crafteo bloques sumar(bloques a, bloques b):
    craftear a + b;
fin

mesa_crafteo bloques restar(bloques a, bloques b):
    craftear a - b;
fin

mesa_crafteo vacío main():
    letrero("=== Calculadora ===");
    
    letrero("Primer número:");
    texto entrada1 = cofre();
    bloques num1 = to_bloques(entrada1);
    
    letrero("Segundo número:");
    texto entrada2 = cofre();
    bloques num2 = to_bloques(entrada2);
    
    bloques suma = sumar(num1, num2);
    bloques resta = restar(num1, num2);
    
    letrero("Suma: " + to_texto(suma));
    letrero("Resta: " + to_texto(resta));
fin
```

### Factorial Recursivo

```jcraft
mesa_crafteo bloques factorial(bloques n):
    observador (n <= 1):
        craftear 1;
    fin
    craftear n * factorial(n - 1);
fin

mesa_crafteo vacío main():
    bloques resultado = factorial(5);
    letrero("Factorial de 5: " + to_texto(resultado));
fin
```

## 🛠️ Uso del IDE

1. **Crear nuevo archivo**: El IDE abre con una plantilla de `main()` automáticamente
2. **Insertar snippets**: Usa el menú "Insertar Código" para agregar ejemplos
3. **Ejecutar código**: Haz clic en "▶ Ejecutar" o presiona F5
4. **Ver errores**: Los errores se muestran en el panel inferior con línea y columna

### Atajos de Teclado

- `F5` - Ejecutar código
- `Ctrl+N` - Nuevo archivo
- `Ctrl+O` - Abrir archivo
- `Ctrl+S` - Guardar archivo
- `Ctrl+Shift+S` - Guardar como

## 📚 Estructura del Proyecto

```
-JCraft/
├── lang/
│   ├── lexer.py          # Analizador léxico
│   ├── parser.py         # Analizador sintáctico
│   ├── type_checker.py   # Verificador de tipos
│   └── interpreter.py    # Intérprete
├── ui/
│   ├── main_window.py    # Ventana principal del IDE
│   ├── editor_panel.py   # Editor de código
│   ├── output_panel.py   # Panel de salida
│   ├── snippets.py       # Snippets de código
│   ├── style.py          # Estilos visuales
│   └── fonts.py          # Configuración de fuentes
├── assets/               # Recursos (fuentes)
├── main.py              # Punto de entrada
└── README.md            # Este archivo
```

## 🐛 Solución de Problemas

### Error: "No module named 'PySide6'"
```bash
# Asegúrate de activar el entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Variable no declarada"
Todas las variables deben declararse con su tipo antes de usarse:
```jcraft
# ❌ Incorrecto
i = 0;

# ✅ Correcto
bloques i = 0;
```

### Error: "Tipo de caso incompatible"
Usa comillas dobles `"..."` para strings, no comillas simples:
```jcraft
# ❌ Incorrecto (glifo)
portal (entrada):
    caso '1':  # Esto es un glifo, no texto
    
# ✅ Correcto (texto)
portal (entrada):
    caso "1":  # Esto es texto
```

## 🎓 Palabras Reservadas

### Estructuras de Control
- `observador` - if
- `comparador` - else if
- `dispensador` - else
- `spawner` - while
- `romper` - end while
- `cultivar` - for
- `cosechar` - end for
- `creeper` - do
- `boom` - while (do-while)
- `portal` - switch
- `caso` - case
- `defecto` - default
- `salir_portal` - break switch

### Funciones
- `mesa_crafteo` - function declaration
- `craftear` - return

### Otros
- `fin` - end block
- `letrero` - print
- `cofre` - input
- `verdadero` - true
- `falso` - false
- `nulo` - null
- `y` - and
- `o` - or
- `no` - not

## 📝 Reglas del Lenguaje

1. **Función main obligatoria**: Todo programa debe tener una función `main()` que retorne `vacío`
2. **Main único**: Solo puede haber una función `main()`
3. **Punto y coma**: Todas las declaraciones y sentencias terminan con `;`
4. **Bloques con fin**: Todos los bloques terminan con `fin`
5. **Tipos explícitos**: Todas las variables deben declararse con su tipo
6. **Strings vs Chars**: 
   - `"texto"` con comillas dobles → tipo `texto`
   - `'c'` con comillas simples → tipo `glifo`

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Autores

- **JoshuaEA54** - *Desarrollador* - [JoshuaEA54](https://github.com/JoshuaEA54)
- **JazminGamboaChacon** - *Desarrollador* - [JazminGamboaChacon](https://github.com/JazminGamboaChacon)

## 🙏 Agradecimientos

- Inspirado en la sintaxis y temática de Minecraft
- Desarrollado como proyecto educativo para el curso de Paradigmas de Programación

## 📞 Contacto

- GitHub: [@JoshuaEA54](https://github.com/JoshuaEA54)
- GitHub: [@JazminGamboaChacon](https://github.com/JazminGamboaChacon)

---

⛏️ **¡Feliz programación en el mundo de Minecraft!** ⛏️