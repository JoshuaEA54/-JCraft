"""
Snippets de código para JCraft
Fragmentos de código de ejemplo para insertar en el editor
"""

SNIPPETS = {
    "Tipos de Datos": {
        "bloques (entero)": 'bloques x = 0;',
        "coordenada (flotante)": 'coordenada x = 0.0;',
        "texto (cadena)": 'texto x = "";',
        "redstone (booleano)": 'redstone x = verdadero;',
        "glifo (caracter)": "glifo x = 'A';",
        "inventario (vector)": 'inventario<bloques> x = [];',
        "mapa (diccionario)": 'mapa<texto, bloques> x = {};',
    },
    
    "Sintaxis - Control": {
        "observador (if)": '''observador (condicion):
        # código
    fin''',
        
        "observador-dispensador (if else)": '''observador (condicion):
        # código
    dispensador:
        # código alternativo
    fin''',
        
        "observador-comparador-dispensador (if else-if else)": '''observador (condicion):
        # código
    comparador (otra_condicion):
        # código alternativo
    dispensador:
        # código alternativo
    fin''',
        
        "spawner (while)": '''spawner (condicion):
        # código
    romper''',
        
        "creeper-boom (do-while)": '''creeper:
        # código
    boom (condicion);''',
        
        "cultivar-cosechar (for)": '''cultivar (i = 0; i < 10; i = i + 1):
        # código
    cosechar''',
        
        "portal-caso (switch)": '''portal (variable):
        caso valor1:
            # código
        caso valor2:
            # código
        defecto:
            # código por defecto
    salir_portal''',
        
        "romper() - break": 'romper();',
        
        "continuar() - continue": 'continuar();',
    },
    
    "Sintaxis - Funciones": {
        "mesa_crafteo con retorno": '''mesa_crafteo tipo nombreFuncion(tipo param):
    # código
    craftear valor;
fin''',
        
        "mesa_crafteo vacío (sin retorno)": '''mesa_crafteo vacío nombreFuncion(tipo param):
    # código
fin''',
        
        "craftear (return)": 'craftear valor;',
        
        "Llamada a función": 'nombreFuncion(argumentos);',
    },
    
    "Sintaxis - Operaciones": {
        "letrero() - print": 'letrero("mensaje");',
        "cofre() - input": 'texto x = cofre("mensaje");',
        "to_bloques() - conversión a entero": 'bloques x = to_bloques(valor);',
        "to_coordenada() - conversión a flotante": 'coordenada x = to_coordenada(valor);',
        "to_texto() - conversión a string": 'texto x = to_texto(valor);',
        "to_glifo() - conversión a char": 'glifo x = to_glifo(valor);',
        "to_redstone() - conversión a bool": 'redstone x = to_redstone(valor);',
    },
    
    "Operadores - Aritméticos": {
        "+ (suma/concatenación)": 'x + y',
        "- (resta)": 'x - y',
        "* (multiplicación)": 'x * y',
        "/ (división)": 'x / y',
        "% (módulo/resto)": 'x % y',
    },
    
    "Operadores - Lógicos": {
        "y (AND lógico)": 'a y b',
        "o (OR lógico)": 'a o b',
        "no (negación)": 'no a',
    },
    
    "Operadores - Relacionales": {
        "== (igualdad)": 'x == y',
        "!= (diferente)": 'x != y',
        "< (menor que)": 'x < y',
        "> (mayor que)": 'x > y',
        "<= (menor o igual)": 'x <= y',
        ">= (mayor o igual)": 'x >= y',
    },
    
    "Palabras Reservadas": {
        "verdadero": 'verdadero',
        "falso": 'falso',
        "vacío": 'vacío',
        "observador": 'observador',
        "dispensador": 'dispensador',
        "comparador": 'comparador',
        "spawner": 'spawner',
        "creeper": 'creeper',
        "boom": 'boom',
        "cultivar": 'cultivar',
        "cosechar": 'cosechar',
        "portal": 'portal',
        "caso": 'caso',
        "defecto": 'defecto',
        "salir_portal": 'salir_portal',
        "mesa_crafteo": 'mesa_crafteo',
        "craftear": 'craftear',
        "romper": 'romper',
        "continuar": 'continuar',
        "fin": 'fin',
        "letrero": 'letrero',
        "cofre": 'cofre',
    },
    
    "Semántica": {
        "Descripción de bloques": "Tipo entero (int) - Representa números enteros como vida, cantidad de items, niveles, etc.",
        "Descripción de coordenada": "Tipo flotante (float) - Representa coordenadas o números decimales como posiciones X, Y, Z.",
        "Descripción de texto": "Tipo cadena (string) - Representa texto como nombres, mensajes, descripciones.",
        "Descripción de redstone": "Tipo booleano (bool) - Representa valores de verdadero o falso, como estados on/off.",
        "Descripción de glifo": "Tipo caracter (char) - Representa un único carácter como letras o símbolos.",
        "Descripción de inventario": "Tipo vector/lista - Colección ordenada de elementos del mismo tipo.",
        "Descripción de mapa": "Tipo diccionario - Colección de pares clave-valor para almacenar datos relacionados.",
        "Descripción de observador": "Estructura condicional if - Evalúa una condición y ejecuta código si es verdadera.",
        "Descripción de spawner": "Estructura repetitiva while - Repite código mientras una condición sea verdadera.",
        "Descripción de cultivar": "Estructura repetitiva for - Itera un número específico de veces con control de contador.",
        "Descripción de mesa_crafteo": "Declaración de función - Define un bloque de código reutilizable con parámetros y tipo de retorno.",
    },
    
    "Ejemplos Completos": {
        "Fibonacci (recursivo)": '''# Secuencia de Fibonacci usando recursión
mesa_crafteo bloques fibonacci(bloques n):
    observador (n <= 1):
        craftear n;
    fin
    craftear fibonacci(n - 1) + fibonacci(n - 2);
fin

mesa_crafteo vacío main():
    letrero("=== Secuencia de Fibonacci ===");
    texto entrada = cofre("¿Cuántos números de Fibonacci deseas? ");
    bloques cantidad = to_bloques(entrada);
    
    letrero("Secuencia de Fibonacci:");
    bloques i = 0;
    cultivar (i = 0; i < cantidad; i = i + 1):
        bloques resultado = fibonacci(i);
        letrero("F(" + to_texto(i) + ") = " + to_texto(resultado));
    cosechar
fin''',

        "Números primos": '''# Verificar si un número es primo
mesa_crafteo redstone esPrimo(bloques numero):
    observador (numero <= 1):
        craftear falso;
    fin
    
    observador (numero == 2):
        craftear verdadero;
    fin
    
    bloques i = 0;
    cultivar (i = 2; i < numero; i = i + 1):
        bloques residuo = numero % i;
        observador (residuo == 0):
            craftear falso;
        fin
    cosechar
    
    craftear verdadero;
fin

mesa_crafteo vacío main():
    letrero("=== Detector de Números Primos ===");
    texto entrada = cofre("Ingresa un número: ");
    bloques num = to_bloques(entrada);
    
    redstone resultado = esPrimo(num);
    
    observador (resultado):
        letrero(to_texto(num) + " es un número primo");
    dispensador:
        letrero(to_texto(num) + " NO es un número primo");
    fin
    
    letrero("Números primos del 1 al 50:");
    bloques j = 0;
    cultivar (j = 1; j <= 50; j = j + 1):
        observador (esPrimo(j)):
            letrero(to_texto(j));
        fin
    cosechar
fin''',

        "Factorial (iterativo)": '''# Calcular factorial de un número
mesa_crafteo bloques factorial(bloques n):
    observador (n < 0):
        letrero("Error: factorial no definido para negativos");
        craftear -1;
    fin
    
    observador (n == 0 o n == 1):
        craftear 1;
    fin
    
    bloques resultado = 1;
    bloques i = 0;
    cultivar (i = 2; i <= n; i = i + 1):
        resultado = resultado * i;
    cosechar
    
    craftear resultado;
fin

mesa_crafteo vacío main():
    letrero("=== Calculadora de Factorial ===");
    texto entrada = cofre("Ingresa un número: ");
    bloques num = to_bloques(entrada);
    
    bloques fact = factorial(num);
    letrero(to_texto(num) + "! = " + to_texto(fact));
    
    letrero("Tabla de factoriales del 1 al 10:");
    bloques i = 0;
    cultivar (i = 1; i <= 10; i = i + 1):
        bloques f = factorial(i);
        letrero(to_texto(i) + "! = " + to_texto(f));
    cosechar
fin''',

        "Ordenamiento burbuja": '''# Algoritmo de ordenamiento por burbuja
mesa_crafteo vacío ordenarBurbuja(inventario<bloques> arr):
    bloques n = 5;  # tamaño del array
    bloques i = 0;
    
    cultivar (i = 0; i < n - 1; i = i + 1):
        bloques j = 0;
        cultivar (j = 0; j < n - i - 1; j = j + 1):
            observador (arr[j] > arr[j + 1]):
                # Intercambiar elementos
                bloques temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            fin
        cosechar
    cosechar
fin

mesa_crafteo vacío main():
    letrero("=== Ordenamiento Burbuja ===");
    
    inventario<bloques> numeros = [64, 34, 25, 12, 22];
    
    letrero("Array original:");
    bloques i = 0;
    cultivar (i = 0; i < 5; i = i + 1):
        letrero(to_texto(numeros[i]));
    cosechar
    
    ordenarBurbuja(numeros);
    
    letrero("Array ordenado:");
    bloques j = 0;
    cultivar (j = 0; j < 5; j = j + 1):
        letrero(to_texto(numeros[j]));
    cosechar
fin''',

        "Búsqueda binaria": '''# Búsqueda binaria en array ordenado
mesa_crafteo bloques busquedaBinaria(inventario<bloques> arr, bloques objetivo):
    bloques izquierda = 0;
    bloques derecha = 4;  # tamaño - 1
    
    spawner (izquierda <= derecha):
        bloques medio = to_bloques((izquierda + derecha) / 2);
        
        observador (arr[medio] == objetivo):
            craftear medio;
        fin
        
        observador (arr[medio] < objetivo):
            izquierda = medio + 1;
        dispensador:
            derecha = medio - 1;
        fin
    romper
    
    craftear -1;  # No encontrado
fin

mesa_crafteo vacío main():
    letrero("=== Búsqueda Binaria ===");
    
    inventario<bloques> numeros = [2, 5, 8, 12, 16];
    
    letrero("Array: [2, 5, 8, 12, 16]");
    texto entrada = cofre("¿Qué número buscas? ");
    bloques buscar = to_bloques(entrada);
    
    bloques indice = busquedaBinaria(numeros, buscar);
    
    observador (indice != -1):
        letrero("Número encontrado en índice: " + to_texto(indice));
    dispensador:
        letrero("Número no encontrado en el array");
    fin
fin''',

        "Calculadora completa": '''# Calculadora con múltiples operaciones
mesa_crafteo coordenada calcular(coordenada a, coordenada b, texto operacion):
    portal (operacion):
        caso "+":
            craftear a + b;
        caso "-":
            craftear a - b;
        caso "*":
            craftear a * b;
        caso "/":
            observador (b == 0.0):
                letrero("Error: División por cero");
                craftear 0.0;
            fin
            craftear a / b;
        defecto:
            letrero("Operación no válida");
            craftear 0.0;
    salir_portal
fin

mesa_crafteo vacío main():
    letrero("=== Calculadora JCraft ===");
    
    redstone continuar = verdadero;
    
    spawner (continuar):
        letrero("Operaciones: +, -, *, /");
        
        texto entrada1 = cofre("Primer número: ");
        coordenada num1 = to_coordenada(entrada1);
        
        texto op = cofre("Operación: ");
        
        texto entrada2 = cofre("Segundo número: ");
        coordenada num2 = to_coordenada(entrada2);
        
        coordenada resultado = calcular(num1, num2, op);
        letrero("Resultado: " + to_texto(resultado));
        
        texto respuesta = cofre("¿Otra operación? (si/no): ");
        observador (respuesta == "no"):
            continuar = falso;
        fin
    romper
    
    letrero("¡Gracias por usar la calculadora!");
fin''',

        "Suma de matriz": '''# Suma de elementos de una matriz (simulada)
mesa_crafteo bloques sumaMatriz(inventario<bloques> matriz, bloques filas, bloques cols):
    bloques suma = 0;
    bloques i = 0;
    
    cultivar (i = 0; i < filas * cols; i = i + 1):
        suma = suma + matriz[i];
    cosechar
    
    craftear suma;
fin

mesa_crafteo vacío main():
    letrero("=== Suma de Matriz 3x3 ===");
    
    # Matriz 3x3 representada como array 1D
    inventario<bloques> matriz = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    
    letrero("Matriz:");
    letrero("[1, 2, 3]");
    letrero("[4, 5, 6]");
    letrero("[7, 8, 9]");
    
    bloques total = sumaMatriz(matriz, 3, 3);
    letrero("Suma total: " + to_texto(total));
fin''',

        "Palíndromo (texto)": '''# Verificar si un texto es palíndromo
mesa_crafteo redstone esPalindromo(texto palabra):
    bloques longitud = 5;  # longitud de la palabra
    bloques mitad = longitud / 2;
    bloques i = 0;
    
    cultivar (i = 0; i < mitad; i = i + 1):
        # Aquí simplificaremos la comparación
        # En un caso real, compararíamos palabra[i] con palabra[longitud-1-i]
        letrero("Comparando posiciones...");
    cosechar
    
    craftear verdadero;  # Simplificado para el ejemplo
fin

mesa_crafteo vacío main():
    letrero("=== Detector de Palíndromos ===");
    texto palabra = cofre("Ingresa una palabra: ");
    
    redstone resultado = esPalindromo(palabra);
    
    observador (resultado):
        letrero("¡Es un palíndromo!");
    dispensador:
        letrero("No es un palíndromo");
    fin
fin''',

        "Menú interactivo completo": '''# Sistema de menú con gestión de inventario
mesa_crafteo vacío mostrarMenu():
    letrero("=========================");
    letrero("  MENÚ PRINCIPAL");
    letrero("=========================");
    letrero("1. Ver inventario");
    letrero("2. Agregar item");
    letrero("3. Eliminar item");
    letrero("4. Buscar item");
    letrero("5. Salir");
    letrero("=========================");
fin

mesa_crafteo vacío verInventario(mapa<texto, bloques> items):
    letrero("--- INVENTARIO ---");
    letrero("Oro: " + to_texto(items["oro"]));
    letrero("Hierro: " + to_texto(items["hierro"]));
    letrero("Diamantes: " + to_texto(items["diamantes"]));
fin

mesa_crafteo vacío agregarItem(mapa<texto, bloques> items):
    texto nombre = cofre("Nombre del item (oro/hierro/diamantes): ");
    texto cantStr = cofre("Cantidad a agregar: ");
    bloques cantidad = to_bloques(cantStr);
    
    bloques actual = items[nombre];
    items[nombre] = actual + cantidad;
    
    letrero("✓ Item agregado correctamente");
fin

mesa_crafteo vacío main():
    letrero("=== GESTOR DE INVENTARIO ===");
    
    mapa<texto, bloques> items_jugador = {
        "oro": 10,
        "hierro": 25,
        "diamantes": 3
    };
    
    redstone ejecutando = verdadero;
    
    spawner (ejecutando):
        mostrarMenu();
        texto opcion = cofre("Selecciona una opción: ");
        
        portal (opcion):
            caso "1":
                verInventario(items_jugador);
            caso "2":
                agregarItem(items_jugador);
            caso "3":
                letrero("Función de eliminar - por implementar");
            caso "4":
                letrero("Función de buscar - por implementar");
            caso "5":
                letrero("¡Hasta luego!");
                ejecutando = falso;
            defecto:
                letrero("Opción no válida");
        salir_portal
    romper
fin''',

        "Validación de datos": '''# Sistema de validación de entrada de usuario
mesa_crafteo redstone esNumeroPositivo(bloques num):
    craftear num > 0;
fin

mesa_crafteo redstone esRangoValido(bloques num, bloques min, bloques max):
    craftear num >= min y num <= max;
fin

mesa_crafteo bloques leerNumeroValido(texto mensaje, bloques min, bloques max):
    bloques intentos = 0;
    bloques numero = 0;
    
    spawner (intentos < 3):
        letrero(mensaje);
        texto entrada = cofre("Ingresa un número: ");
        numero = to_bloques(entrada);
        
        observador (esRangoValido(numero, min, max)):
            craftear numero;
        fin
        
        letrero("Error: el número debe estar entre " + to_texto(min) + " y " + to_texto(max));
        intentos = intentos + 1;
    romper
    
    letrero("Demasiados intentos fallidos");
    craftear -1;
fin

mesa_crafteo vacío main():
    letrero("=== Sistema de Validación ===");
    
    bloques edad = leerNumeroValido("Ingresa tu edad:", 1, 120);
    
    observador (edad != -1):
        letrero("Edad válida: " + to_texto(edad));
        
        observador (edad >= 18):
            letrero("Eres mayor de edad");
        dispensador:
            letrero("Eres menor de edad");
        fin
    dispensador:
        letrero("No se pudo obtener una edad válida");
    fin
fin''',
    },
}


def get_snippet_menu_structure():
    """Retorna la estructura del menú de snippets"""
    return SNIPPETS


def get_snippet(category: str, name: str) -> str:
    """Obtiene un snippet específico"""
    if category in SNIPPETS and name in SNIPPETS[category]:
        return SNIPPETS[category][name]
    return ""
