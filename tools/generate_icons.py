from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "icons"
SOURCE = OUT / "zombie_icon_fourth_panel.png"
OUT.mkdir(parents=True, exist_ok=True)

with Image.open(SOURCE) as source:
    image = source.convert("RGB")
    if image.width != image.height:
        raise ValueError("The game icon source must be square")
    image.resize((1024, 1024), Image.Resampling.LANCZOS).save(OUT / "icon-1024.png", optimize=True)
    for side in (180, 167, 152, 120, 87, 80, 76, 60, 58, 40, 29, 20):
        image.resize((side, side), Image.Resampling.LANCZOS).save(OUT / f"icon-{side}.png", optimize=True)

print(OUT / "icon-1024.png")
