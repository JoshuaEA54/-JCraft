# Generar ejecutable (.exe) — JCraft IDE

Este documento explica cómo empaquetar el proyecto en un único archivo `.exe` usando **PyInstaller**. El ejecutable resultante no requiere tener Python instalado para correr.

---

## Herramienta utilizada

**PyInstaller** — empaqueta el código Python junto con todas sus dependencias (incluyendo PySide6) en un solo binario ejecutable.

---

## Requisitos previos

- Tener el entorno virtual `.venv` del proyecto configurado.
- Que PySide6 esté instalado dentro del `.venv` (ya viene en `requirements.txt`).
- Estar ubicado en la raíz del proyecto (`-JCraft/`).

> **Importante:** No usar el comando `python` ni `pip` del sistema global. Este proyecto tiene su propio entorno virtual (`.venv`) donde están instaladas las dependencias. Si se usa el Python global, el build falla porque no encuentra PySide6.

---

## Paso 1 — Instalar PyInstaller

PyInstaller es la herramienta que convierte el proyecto en un `.exe`. Solo se instala una vez.

```bash
.venv/Scripts/python.exe -m pip install pyinstaller
```

- `.venv/Scripts/python.exe` — usa el Python del entorno virtual del proyecto, no el del sistema.
- `-m pip install pyinstaller` — descarga e instala PyInstaller dentro de ese entorno.

---

## Paso 2 — Generar el ejecutable

### Primera vez (sin archivo `JCraft.spec`)

```bash
.venv/Scripts/python.exe -m PyInstaller --onefile --windowed --icon=assets/jcraft_logo.ico --name=JCraft --add-data "assets;assets" main.py
```

Este comando le dice a PyInstaller cómo construir el ejecutable. Cada parte hace lo siguiente:

- `.venv/Scripts/python.exe -m PyInstaller` — ejecuta PyInstaller usando el Python del entorno virtual.
- `--onefile` — junta todo (Python, PySide6, el código del proyecto) en un **único archivo `.exe`**. Sin esto, genera una carpeta entera con decenas de archivos.
- `--windowed` — evita que aparezca una consola negra de fondo al abrir el programa. Necesario para aplicaciones con interfaz gráfica.
- `--icon=assets/jcraft_logo.ico` — asigna el ícono que aparece en el `.exe` y en la barra de tareas de Windows.
- `--name=JCraft` — define el nombre del archivo resultante (`JCraft.exe`).
- `--add-data "assets;assets"` — incluye la carpeta `assets/` dentro del ejecutable (fuentes, imágenes, íconos). Sin esto, el programa arranca sin fondo, sin ícono y sin la fuente Minecraft. El formato es `"origen;destino"`, y en Windows el separador es `;`.
- `main.py` — el archivo de entrada del proyecto, desde donde arranca la aplicación.

### Builds siguientes (ya existe `JCraft.spec`)

La primera vez que se corre el comando anterior, PyInstaller genera automáticamente un archivo `JCraft.spec` en la raíz del proyecto. Este archivo guarda toda la configuración del build. Para volver a generar el `.exe` sin tener que escribir todos los flags de nuevo, basta con:

```bash
.venv/Scripts/python.exe -m PyInstaller JCraft.spec
```

---

## Resultado

Una vez que termina el proceso (puede tardar entre 30 segundos y 2 minutos), se generan dos carpetas:

```
build/   ← archivos temporales del proceso, se puede borrar
dist/
└── JCraft.exe   ← el ejecutable final (≈ 48 MB)
```

El archivo `dist/JCraft.exe` es el único que se necesita distribuir. No requiere instalación ni Python en la máquina destino.

---

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'PySide6'` | Se usó el Python global en lugar del `.venv` | Usar `.venv/Scripts/python.exe` en todos los comandos |
| Los assets no cargan (sin fondo, sin fuente) | Se olvidó el flag `--add-data` | Incluir `--add-data "assets;assets"` o revisar `JCraft.spec` |
| El `.exe` abre y cierra instantáneamente | Error en tiempo de ejecución | Quitar `--windowed` temporalmente para ver el error en consola |
