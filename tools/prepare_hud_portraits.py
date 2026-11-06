from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import random
import sys

root = Path(__file__).resolve().parents[1]
out = root / 'assets' / 'ui'
_names = ['male', 'medic', 'riley', 'maya']
_selected = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if _selected: _names = [n for n in _names if n in _selected]
for name in _names:
    source_path = out / f'{name}_hd_portrait.png'
    if not source_path.exists(): continue
    source = Image.open(source_path).convert('RGB')
    crop = (125, 35, 385, 295) if name in ('male', 'medic') else (130, 35, 380, 285)
    source = source.crop(crop).resize((512, 512), Image.Resampling.LANCZOS)
    gray = ImageEnhance.Contrast(source.convert('L')).enhance(1.18)
    gray = ImageEnhance.Brightness(gray).enhance(0.88)
    image = Image.merge('RGB', (gray, gray, gray))
    # Subtle permanent print grain; the HUD adds only static worn edges.
    random.seed(410 + (name == 'female'))
    pixels = image.load()
    for _ in range(image.width * image.height // 24):
        x = random.randrange(image.width); y = random.randrange(image.height)
        delta = random.choice((-20, -12, 10, 16))
        value = max(0, min(255, pixels[x, y][0] + delta))
        pixels[x, y] = (value, value, value)
    image.save(out / f'{name}_hud_gray.png')
    print('HUD_PORTRAIT', name, image.size)
