"""
Fragmentos de código (snippets) para JCraft
Organizados por categorías para insertar DENTRO de la función main
NOTA: Al crear un nuevo archivo (Ctrl+N), ya tendrás la estructura de main lista.
Solo pega estos fragmentos DENTRO del main.
"""

SNIPPETS = {
    "Declaraciones": {
        "Declaración de enteros (bloques)": '''bloques vidas = 3;''',
        "Declaración de flotantes (coordenada)": '''coordenada pi = 3.14;''',
        "Declaración de cadenas (texto)": '''texto nombre = "Alex";''',
        "Declaración de booleanos (redstone)": '''redstone activo = verdadero;''',
        "Declaración de caracteres (glifo)": '''glifo inicial = 'A';''',
        "Declaración de lista (inventario)": '''inventario<bloques> numeros = [1, 2, 3, 4, 5];''',
        "Declaración de mapa (mapa)": '''mapa<texto,bloques> stats = {};
stats["vida"] = 100;
stats["mana"] = 50;''',
    },
    
    "Estructuras de Control": {
        "IF simple (observador)": '''observador (vida > 0):
    letrero("Aún tienes vida");
fin''',
        
        "IF-ELSE (observador-dispensador)": '''observador (puntaje >= 100):
    letrero("¡Ganaste!");
dispensador:
    letrero("Sigue intentando");
fin''',
        
        "IF-ELSE IF-ELSE completo": '''observador (temperatura > 30):
    letrero("Hace calor");
comparador (temperatura > 20):
    letrero("Clima agradable");
dispensador:
    letrero("Hace frío");
fin''',
        
        "FOR (cultivar-cosechar)": '''bloques i = 0;
cultivar (i = 0; i < 5; i = i + 1):
    letrero("Iteración " + to_texto(i));
cosechar''',
        
        "WHILE (spawner-romper)": '''spawner (contador > 0):
    letrero("Contador: " + to_texto(contador));
    contador = contador - 1;
romper''',
        
        "DO-WHILE (creeper-boom)": '''creeper:
    letrero("Ejecutar al menos una vez");
    contador = contador + 1;
boom (contador < 5);''',
        
        "SWITCH (portal-salir_portal)": '''portal (opcion):
    caso 1:
        letrero("Opción uno");
    caso 2:
        letrero("Opción dos");
    defecto:
        letrero("Opción no válida");
salir_portal''',
    },
    
    "Funciones Auxiliares": {
        "Definir función con retorno (pegar ANTES de main)": '''# Pegar esta función ANTES de main
mesa_crafteo bloques sumar(bloques a, bloques b):
    craftear a + b;
fin

''',
        
        "Definir función sin retorno (pegar ANTES de main)": '''# Pegar esta función ANTES de main
mesa_crafteo vacío saludar(texto nombre):
    letrero("Hola, " + nombre);
fin

''',
        
        "Llamar función con retorno": '''bloques resultado = sumar(10, 20);
letrero("Resultado: " + to_texto(resultado));''',
        
        "Llamar función sin retorno": '''saludar("Jugador");''',
    },
    
    "Entrada/Salida": {
        "Salida simple (letrero)": '''letrero("Mensaje en consola");''',
        
        "Salida con variable": '''bloques edad = 25;
letrero("Edad: " + to_texto(edad));''',
        
        "Entrada de texto (cofre)": '''texto nombre = cofre();
letrero("Hola " + nombre);''',
        
        "Entrada con mensaje": '''letrero("Ingresa tu edad:");
texto entrada = cofre();
letrero("Tienes " + entrada + " años");''',
    },
    
    "Conversiones de Tipo": {
        "Texto a entero (to_bloques)": '''texto s = "42";
bloques n = to_bloques(s);
letrero("Número: " + to_texto(n));''',
        
        "Texto a flotante (to_coordenada)": '''texto s = "3.14";
coordenada f = to_coordenada(s);
letrero("Flotante: " + to_texto(f));''',
        
        "Número a texto (to_texto)": '''bloques n = 100;
texto s = to_texto(n);
letrero("Texto: " + s);''',
        
        "Texto a booleano (to_redstone)": '''texto entrada = "verdadero";
redstone flag = to_redstone(entrada);
letrero("Bandera: " + to_texto(flag));''',
        
        "Entrada numérica con conversión": '''letrero("Ingresa tu edad:");
texto entrada = cofre();
bloques edad = to_bloques(entrada);
letrero("Edad: " + to_texto(edad));''',
        
        "Validar entrada booleana": '''letrero("¿Continuar? (verdadero/falso):");
texto respuesta = cofre();
redstone continuar = to_redstone(respuesta);
observador (continuar):
    letrero("Continuando...");
fin''',
    },
    
    "Operaciones con Listas": {
        "Crear lista vacía": '''inventario<bloques> lista = [];''',
        
        "Crear lista con elementos": '''inventario<bloques> numeros = [10, 20, 30, 40];''',
        
        "Acceder a elemento": '''bloques primero = lista[0];
letrero("Primer elemento: " + to_texto(primero));''',
        
        "Modificar elemento": '''lista[1] = 99;
letrero("Lista modificada");''',
        
        "Agregar elemento (push)": '''push(lista, 50);
letrero("Elemento agregado");''',
        
        "Remover último (pop)": '''bloques ultimo = pop(lista);
letrero("Elemento removido: " + to_texto(ultimo));''',
        
        "Obtener longitud": '''bloques tamaño = length(lista);
letrero("Tamaño: " + to_texto(tamaño));''',
        
        "Recorrer lista con FOR": '''inventario<bloques> nums = [1, 2, 3, 4, 5];
bloques i = 0;
cultivar (i = 0; i < length(nums); i = i + 1):
    letrero("Elemento " + to_texto(i) + ": " + to_texto(nums[i]));
cosechar''',
    },
    
    "Operaciones con Mapas": {
        "Crear mapa vacío": '''mapa<texto,bloques> datos = {};''',
        
        "Crear mapa con asignaciones": '''mapa<texto,bloques> jugador = {};
jugador["vida"] = 100;
jugador["energia"] = 50;''',
        
        "Acceder a valor": '''bloques vida = jugador["vida"];
letrero("Vida: " + to_texto(vida));''',
        
        "Modificar valor": '''jugador["vida"] = 80;
letrero("Nueva vida: " + to_texto(jugador["vida"]));''',
        
        "Agregar nueva clave": '''jugador["mana"] = 30;
letrero("Mana agregado: " + to_texto(jugador["mana"]));''',
        
        "Verificar si existe clave": '''observador (tiene(jugador, "vida")):
    letrero("El jugador tiene vida");
fin''',
    },
    
    "Operadores Compuestos": {
        "Incremento (+=)": '''bloques x = 10;
x += 5;  # x = x + 5
letrero("x: " + to_texto(x));''',
        
        "Decremento (-=)": '''bloques vida = 100;
vida -= 20;  # vida = vida - 20
letrero("Vida: " + to_texto(vida));''',
        
        "Multiplicación (*=)": '''bloques puntos = 50;
puntos *= 2;  # puntos = puntos * 2
letrero("Puntos: " + to_texto(puntos));''',
        
        "División (/=)": '''coordenada valor = 100.0;
valor /= 4.0;  # valor = valor / 4.0
letrero("Valor: " + to_texto(valor));''',
        
        "Módulo (%=)": '''bloques numero = 27;
numero %= 5;  # numero = numero % 5
letrero("Módulo: " + to_texto(numero));''',
        
        "Concatenación (+=)": '''texto mensaje = "Hola";
mensaje += " Mundo";
letrero(mensaje);''',
    },
    
    "Ejemplos Completos": {
        "Calculadora simple": '''bloques a = 10;
bloques b = 5;

bloques suma = a + b;
bloques resta = a - b;
bloques mult = a * b;
coordenada div = to_coordenada(to_texto(a)) / to_coordenada(to_texto(b));

letrero("=== CALCULADORA ===");
letrero("Suma: " + to_texto(suma));
letrero("Resta: " + to_texto(resta));
letrero("Multiplicación: " + to_texto(mult));
letrero("División: " + to_texto(div));''',
        
        "Contador regresivo": '''bloques contador = 5;

spawner (contador > 0):
    letrero("Cuenta regresiva: " + to_texto(contador));
    contador -= 1;
romper

letrero("¡Despegue!");''',
        
        "Inventario simple": '''inventario<texto> items = ["Espada", "Escudo", "Poción"];

letrero("=== INVENTARIO ===");
bloques i = 0;
cultivar (i = 0; i < length(items); i = i + 1):
    letrero(to_texto(i + 1) + ". " + items[i]);
cosechar''',
        
        "Sistema de puntos": '''bloques puntos = 0;
bloques multiplicador = 1;

# Ganar puntos
puntos += 50;
letrero("Puntos ganados: " + to_texto(puntos));

# Aplicar multiplicador
multiplicador += 1;
puntos *= multiplicador;
letrero("Puntos con multiplicador: " + to_texto(puntos));''',
        
        "Menú interactivo": '''letrero("=== MENÚ ===");
letrero("1. Nueva partida");
letrero("2. Cargar partida");
letrero("3. Salir");
letrero("Selecciona una opción:");

texto opcion = cofre();

portal (opcion):
    caso "1":
        letrero("Iniciando nueva partida...");
    caso "2":
        letrero("Cargando partida...");
    caso "3":
        letrero("¡Hasta luego!");
    defecto:
        letrero("Opción no válida");
salir_portal''',
        
        "Suma de lista": '''inventario<bloques> nums = [10, 20, 30, 40, 50];
bloques suma = 0;

bloques i = 0;
cultivar (i = 0; i < length(nums); i = i + 1):
    suma += nums[i];
cosechar

coordenada promedio = to_coordenada(to_texto(suma)) / to_coordenada(to_texto(length(nums)));

letrero("Suma total: " + to_texto(suma));
letrero("Promedio: " + to_texto(promedio));''',
    },
}
