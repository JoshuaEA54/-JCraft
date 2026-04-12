import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """Devuelve la ruta absoluta al recurso.
    Funciona tanto en desarrollo como empaquetado con PyInstaller (--onefile).
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative
