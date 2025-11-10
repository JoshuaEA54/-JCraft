"""
Snippets de código para JCraft
Fragmentos de código de ejemplo para insertar en el editor
"""

SNIPPETS = {
    "Declaraciones": {
        "Declaración de enteros (bloques)": '''bloques vida = 100;
bloques diamantes = 0;
bloques nivel = 1;''',
        
        "Declaración de flotantes (coordenada)": '''coordenada posX = 10.5;
coordenada posY = 64.0;
coordenada posZ = -23.75;''',
        
        "Declaración de cadenas (texto)": '''texto nombre = "Steve";
texto mensaje = "Hola Mundo";
texto bioma = "jungla";''',
        
        "Declaración de booleanos (redstone)": '''redstone encendido = verdadero;
redstone esDia = falso;
redstone tieneItem = verdadero;''',
        
        "Declaración de caracteres (glifo)": '''glifo inicial = 'S';
glifo simbolo = '#';
glifo letra = 'A';''',
        
        "Declaración de vectores (inventario)": '''inventario<bloques> numeros = [1, 2, 3, 4, 5];
inventario<texto> items = ["pico", "pala", "espada"];''',
        
        "Declaración de diccionarios (mapa)": '''mapa<texto, bloques> recursos = {"oro": 10, "hierro": 25};
mapa<texto, texto> jugador = {"nombre": "Alex", "clase": "minero"};''',
    },
    
    "Estructuras": {
        "If simple (observador)": '''bloques vida = 80;
observador (vida > 50):
    letrero("Tienes buena salud");
fin''',
        
        "If-Else (observador-dispensador)": '''bloques diamantes = 15;
observador (diamantes > 10):
    letrero("Eres rico!");
dispensador:
    letrero("Necesitas más diamantes");
fin''',
        
        "If-Else If-Else completo": '''bloques puntaje = 85;
observador (puntaje >= 90):
    letrero("Excelente");
comparador (puntaje >= 70):
    letrero("Bien");
comparador (puntaje >= 50):
    letrero("Regular");
dispensador:
    letrero("Necesitas mejorar");
fin''',
        
        "While (spawner)": '''bloques contador = 0;
spawner (contador < 5):
    letrero("Contador: " + to_texto(contador));
    contador = contador + 1;
romper''',
        
        "Do-While (creeper)": '''bloques intentos = 0;
creeper:
    letrero("Intento número: " + to_texto(intentos));
    intentos = intentos + 1;
boom (intentos < 3);''',
        
        "For (cultivar)": '''bloques i = 0;
cultivar (i = 0; i < 10; i = i + 1):
    letrero("Iteración: " + to_texto(i));
cosechar''',
        
        "Switch (portal)": '''texto comando = "saltar";
portal (comando):
    caso "saltar":
        letrero("Saltando...");
    caso "correr":
        letrero("Corriendo...");
    caso "atacar":
        letrero("Atacando...");
    defecto:
        letrero("Comando desconocido");
salir_portal''',
        
        "Break en loop": '''bloques i = 0;
spawner (i < 100):
    observador (i == 5):
        letrero("Saliendo en 5");
        romper();
    fin
    letrero(to_texto(i));
    i = i + 1;
romper''',
        
        "Continue en loop": '''bloques j = 0;
cultivar (j = 0; j < 10; j = j + 1):
    observador (j == 5):
        continuar();
    fin
    letrero("Número: " + to_texto(j));
cosechar''',
    },
    
    "Funciones": {
        "Función con retorno (sumar)": '''mesa_crafteo bloques sumar(bloques a, bloques b):
    bloques resultado = a + b;
    craftear resultado;
fin
###MAIN###
# Llamar a la función
bloques resultado = sumar(10, 20);
letrero("10 + 20 = " + to_texto(resultado));''',
        
        "Función sin retorno (saludar)": '''mesa_crafteo vacío saludar(texto nombre):
    letrero("¡Hola, " + nombre + "!");
fin
###MAIN###
# Llamar a la función
saludar("Jugador");''',
        
        "Función con múltiples parámetros": '''mesa_crafteo coordenada calcularPromedio(coordenada a, coordenada b, coordenada c):
    coordenada suma = a + b + c;
    coordenada promedio = suma / 3.0;
    craftear promedio;
fin
###MAIN###
# Llamar a la función
coordenada prom = calcularPromedio(10.0, 15.0, 20.0);
letrero("Promedio: " + to_texto(prom));''',
        
        "Función recursiva (factorial)": '''mesa_crafteo bloques factorial(bloques n):
    observador (n <= 1):
        craftear 1;
    fin
    craftear n * factorial(n - 1);
fin
###MAIN###
# Llamar a la función recursiva
bloques fact = factorial(5);
letrero("5! = " + to_texto(fact));''',
    },
    
    "Casting": {
        "Conversión a entero": '''texto entrada = cofre("Ingrese un número: ");
bloques numero = to_bloques(entrada);
letrero("Número ingresado: " + to_texto(numero));''',
        
        "Conversión a flotante": '''texto valor = "3.14";
coordenada pi = to_coordenada(valor);
letrero("Pi aproximado: " + to_texto(pi));''',
        
        "Conversión a texto": '''bloques edad = 25;
texto mensaje = "Tienes " + to_texto(edad) + " años";
letrero(mensaje);''',
    },
    
    "Ejemplos": {
        "Programa completo: Calculadora simple": '''mesa_crafteo bloques sumar(bloques a, bloques b):
    craftear a + b;
fin

mesa_crafteo bloques restar(bloques a, bloques b):
    craftear a - b;
fin

mesa_crafteo vacío main():
    letrero("=== Calculadora Simple ===");
    
    letrero("Ingresa el primer número:");
    texto entrada1 = cofre("Primer número: ");
    bloques num1 = to_bloques(entrada1);
    
    letrero("Ingresa el segundo número:");
    texto entrada2 = cofre("Segundo número: ");
    bloques num2 = to_bloques(entrada2);
    
    bloques suma = sumar(num1, num2);
    bloques resta = restar(num1, num2);
    
    letrero("Suma: " + to_texto(suma));
    letrero("Resta: " + to_texto(resta));
fin''',
        
        "Programa completo: Contador con loops": '''mesa_crafteo vacío main():
    letrero("=== Contador ===");
    
    bloques limite = 5;
    bloques i = 1;
    
    letrero("Contando con while:");
    spawner (i <= limite):
        letrero("Número: " + to_texto(i));
        i = i + 1;
    romper
    
    letrero("Contando con for:");
    bloques j = 0;
    cultivar (j = 1; j <= limite; j = j + 1):
        letrero("Número: " + to_texto(j));
    cosechar
    
    letrero("Fin del programa");
fin''',
        
        "Programa completo: Sistema de menú": '''mesa_crafteo vacío main():
    letrero("=== Menú Principal ===");
    letrero("1. Nueva partida");
    letrero("2. Cargar partida");
    letrero("3. Opciones");
    letrero("4. Salir");
    
    letrero("Elige una opción:");
    texto entrada = cofre("Seleccione una opción (1-4): ");
    
    portal (entrada):
        caso "1":
            letrero("Iniciando nueva partida...");
        caso "2":
            letrero("Cargando partida...");
        caso "3":
            letrero("Abriendo opciones...");
        caso "4":
            letrero("Saliendo del juego...");
        defecto:
            letrero("Opción no válida");
    salir_portal
fin''',
        
        "Programa completo: Validación de entrada": '''mesa_crafteo redstone esPositivo(bloques num):
    observador (num > 0):
        craftear verdadero;
    fin
    craftear falso;
fin

mesa_crafteo vacío main():
    letrero("Ingresa un número:");
    texto entrada = cofre("Digite un número: ");
    bloques numero = to_bloques(entrada);
    
    redstone positivo = esPositivo(numero);
    
    observador (positivo):
        letrero("El número es positivo");
    dispensador:
        letrero("El número es cero o negativo");
    fin
fin''',
        
        "Programa completo: Búsqueda en rango": '''mesa_crafteo vacío main():
    letrero("=== Buscar número par ===");
    
    bloques inicio = 1;
    bloques fin_busqueda = 20;
    bloques i = 0;
    
    cultivar (i = inicio; i <= fin_busqueda; i = i + 1):
        bloques residuo = i % 2;
        
        observador (residuo == 0):
            letrero("Primer número par encontrado: " + to_texto(i));
            romper();
        fin
    cosechar
    
    letrero("Búsqueda completada");
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
