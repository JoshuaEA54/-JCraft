"""
Fragmentos de código (snippets) para JCraft
Organizados por categorías para insertar en el editor
"""

SNIPPETS = {
    "Declaraciones": {
        "Declaración de enteros (bloques)": '''bloques vidas = 3;''',
        "Declaración de flotantes (coordenada)": '''coordenada pi = 3.14;''',
        "Declaración de cadenas (texto)": '''texto nombre = "Alex";''',
        "Declaración de booleanos (redstone)": '''redstone activo = verdadero;''',
        "Declaración de caracteres (glifo)": '''glifo inicial = 'A';''',
        "Declaración de lista (inventario)": '''inventario<bloques> numeros = [1, 2, 3, 4, 5];''',
        "Declaración de mapa (mapa)": '''mapa<texto,bloques> stats = {"vida": 100, "mana": 50};''',
    },
    
    "Estructuras de Control": {
        "IF simple (observador)": '''observador (vida > 0):
    letrero "Aún tienes vida";
fin''',
        
        "IF-ELSE (observador-dispensador)": '''observador (puntaje >= 100):
    letrero "¡Ganaste!";
dispensador:
    letrero "Sigue intentando";
fin''',
        
        "IF-ELSE IF-ELSE completo": '''observador (temperatura > 30):
    letrero "Hace calor";
comparador (temperatura > 20):
    letrero "Clima agradable";
dispensador:
    letrero "Hace frío";
fin''',
        
        "FOR (cultivar-cosechar)": '''cultivar (i = 0; i < 5; i = i + 1):
    letrero "Iteración " + i;
cosechar''',
        
        "WHILE (spawner-romper)": '''spawner (contador > 0):
    letrero "Contador: " + contador;
    contador = contador - 1;
romper''',
        
        "DO-WHILE (creeper-boom)": '''creeper:
    letrero "Ejecutar al menos una vez";
    contador = contador + 1;
boom (contador < 5);''',
        
        "SWITCH (portal-salir_portal)": '''portal (opcion):
    caso 1:
        letrero "Opción uno";
    caso 2:
        letrero "Opción dos";
    defecto:
        letrero "Opción no válida";
salir_portal''',
    },
    
    "Funciones": {
        "Función con retorno": '''mesa_crafteo bloques sumar(bloques a, bloques b):
    craftear a + b;
fin''',
        
        "Función sin retorno (vacío)": '''mesa_crafteo vacío saludar(texto nombre):
    letrero "Hola, " + nombre;
fin''',
        
        "Función main básica": '''mesa_crafteo vacío main():
    letrero "¡Hola, JCraft!";
fin''',
        
        "Función main con variables": '''mesa_crafteo vacío main():
    bloques x = 10;
    bloques y = 20;
    bloques resultado = x + y;
    letrero "Resultado: " + resultado;
fin''',
    },
    
    "Entrada/Salida": {
        "Salida simple (letrero)": '''letrero "Mensaje en consola";''',
        
        "Salida con variable": '''bloques edad = 25;
letrero "Edad: " + edad;''',
        
        "Entrada de texto (cofre)": '''texto nombre = cofre();
letrero "Hola " + nombre;''',
        
        "Entrada con mensaje": '''letrero "Ingresa tu edad:";
texto entrada = cofre();
letrero "Tienes " + entrada + " años";''',
    },
    
    "Conversiones de Tipo": {
        "Texto a entero (to_bloques)": '''texto s = "42";
bloques n = to_bloques(s);
letrero "Número: " + n;''',
        
        "Texto a flotante (to_coordenada)": '''texto s = "3.14";
coordenada f = to_coordenada(s);
letrero "Flotante: " + f;''',
        
        "Número a texto (to_texto)": '''bloques n = 100;
texto s = to_texto(n);
letrero "Texto: " + s;''',
        
        "Texto a booleano (to_redstone)": '''texto entrada = "verdadero";
redstone flag = to_redstone(entrada);
letrero "Bandera: " + flag;''',
        
        "Texto a carácter (to_glifo)": '''texto s = "#";
glifo simbolo = to_glifo(s);
letrero "Símbolo: " + simbolo;''',
        
        "Entrada numérica con conversión": '''letrero "Ingresa tu edad:";
texto entrada = cofre();
bloques edad = to_bloques(entrada);
letrero "Edad: " + edad;''',
        
        "Validar entrada booleana": '''letrero "¿Continuar? (verdadero/falso):";
texto respuesta = cofre();
redstone continuar = to_redstone(respuesta);
observador (continuar):
    letrero "Continuando...";
fin''',
    },
    
    "Operaciones con Listas": {
        "Crear lista vacía": '''inventario<bloques> lista = [];''',
        
        "Crear lista con elementos": '''inventario<bloques> numeros = [10, 20, 30, 40];''',
        
        "Acceder a elemento": '''bloques primero = lista[0];
letrero "Primer elemento: " + primero;''',
        
        "Modificar elemento": '''lista[1] = 99;
letrero "Lista modificada: " + lista;''',
        
        "Agregar elemento (push)": '''push(lista, 50);
letrero "Elemento agregado: " + lista;''',
        
        "Remover último (pop)": '''bloques ultimo = pop(lista);
letrero "Elemento removido: " + ultimo;''',
        
        "Obtener longitud": '''bloques tamaño = length(lista);
letrero "Tamaño: " + tamaño;''',
        
        "Recorrer lista con FOR": '''inventario<bloques> nums = [1, 2, 3, 4, 5];
cultivar (i = 0; i < length(nums); i = i + 1):
    letrero "Elemento " + i + ": " + nums[i];
cosechar''',
    },
    
    "Operaciones con Mapas": {
        "Crear mapa vacío": '''mapa<texto,bloques> mapa = {};''',
        
        "Crear mapa con elementos": '''mapa<texto,bloques> jugador = {"vida": 100, "energia": 50};''',
        
        "Acceder a valor": '''bloques vida = jugador["vida"];
letrero "Vida: " + vida;''',
        
        "Modificar valor": '''jugador["vida"] = 80;
letrero "Nueva vida: " + jugador["vida"];''',
        
        "Agregar nueva clave": '''jugador["mana"] = 30;
letrero "Mana agregado: " + jugador["mana"];''',
        
        "Verificar si existe clave": '''observador (tiene(jugador, "vida")):
    letrero "El jugador tiene vida";
fin''',
    },
    
    "Ejemplos Completos": {
        "Calculadora simple": '''mesa_crafteo vacío main():
    bloques a = 10;
    bloques b = 5;
    
    bloques suma = a + b;
    bloques resta = a - b;
    bloques mult = a * b;
    bloques div = a / b;
    
    letrero "Suma: " + suma;
    letrero "Resta: " + resta;
    letrero "Multiplicación: " + mult;
    letrero "División: " + div;
fin''',
        
        "Contador con while": '''mesa_crafteo vacío main():
    bloques contador = 5;
    
    spawner (contador > 0):
        letrero "Cuenta regresiva: " + contador;
        contador = contador - 1;
    romper
    
    letrero "¡Despegue!";
fin''',
        
        "Inventario de items": '''mesa_crafteo vacío main():
    inventario<texto> items = ["Espada", "Escudo", "Poción"];
    mapa<texto,bloques> stats = {"fuerza": 10, "defensa": 8};
    
    letrero "=== INVENTARIO ===";
    cultivar (i = 0; i < length(items); i = i + 1):
        letrero (i + 1) + ". " + items[i];
    cosechar
    
    letrero "=== ESTADÍSTICAS ===";
    letrero "Fuerza: " + stats["fuerza"];
    letrero "Defensa: " + stats["defensa"];
fin''',
        
        "Menú interactivo": '''mesa_crafteo vacío main():
    letrero "=== MENÚ ===";
    letrero "1. Nueva partida";
    letrero "2. Cargar partida";
    letrero "3. Salir";
    letrero "Selecciona una opción:";
    
    texto opcion = cofre();
    
    portal (opcion):
        caso "1":
            letrero "Iniciando nueva partida...";
        caso "2":
            letrero "Cargando partida...";
        caso "3":
            letrero "¡Hasta luego!";
        defecto:
            letrero "Opción no válida";
    salir_portal
fin''',
        
        "Calculadora con conversiones": '''mesa_crafteo vacío main():
    letrero "=== CALCULADORA ===";
    letrero "Ingresa el primer número:";
    texto entrada1 = cofre();
    bloques num1 = to_bloques(entrada1);
    
    letrero "Ingresa el segundo número:";
    texto entrada2 = cofre();
    bloques num2 = to_bloques(entrada2);
    
    bloques suma = num1 + num2;
    bloques resta = num1 - num2;
    bloques mult = num1 * num2;
    
    letrero "=== RESULTADOS ===";
    letrero "Suma: " + suma;
    letrero "Resta: " + resta;
    letrero "Multiplicación: " + mult;
fin''',
        
        "Procesamiento de lista de textos": '''mesa_crafteo vacío main():
    inventario<texto> nums_texto = ["10", "20", "30", "40", "50"];
    inventario<bloques> nums = [];
    bloques suma = 0;
    
    letrero "Convirtiendo y sumando...";
    cultivar (i = 0; i < length(nums_texto); i = i + 1):
        bloques n = to_bloques(nums_texto[i]);
        push(nums, n);
        suma = suma + n;
    cosechar
    
    letrero "Lista original: " + nums_texto;
    letrero "Lista convertida: " + nums;
    letrero "Suma total: " + suma;
    letrero "Promedio: " + (suma / length(nums));
fin''',
    },
}
