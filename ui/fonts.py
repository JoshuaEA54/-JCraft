from pathlib import Path
from PySide6.QtGui import QFontDatabase

ASSETS = Path("assets")

PIXEL_FONT_FILES = [
    ASSETS / "Minecraft.ttf",
    ASSETS / "Minecrafter-Regular.ttf",
    ASSETS / "PressStart2P-Regular.ttf",
    ASSETS / "VT323-Regular.ttf",
]

def load_pixel_font_family() -> str | None:
    for fpath in PIXEL_FONT_FILES:
        if fpath.exists():
            fid = QFontDatabase.addApplicationFont(str(fpath))
            fams = QFontDatabase.applicationFontFamilies(fid)
            if fams:
                return fams[0]
    for fpath in ASSETS.glob("*.ttf"):
        fid = QFontDatabase.addApplicationFont(str(fpath))
        fams = QFontDatabase.applicationFontFamilies(fid)
        if fams:
            return fams[0]
    return None
