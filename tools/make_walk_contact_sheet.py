from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
folder = root / 'diagnostics' / 'godot_actor_walk'
font = ImageFont.load_default(size=20)
canvas = Image.new('RGB', (4 * 384, 3 * 550), '#20252a')
draw = ImageDraw.Draw(canvas)
for row, actor in enumerate(('male', 'female', 'walker')):
    for col in range(4):
        image = Image.open(folder / f'{actor}_{col}.png').convert('RGB')
        canvas.paste(image, (col * 384, row * 550 + 38))
        draw.text((col * 384 + 12, row * 550 + 8), f'{actor}  phase {col}', fill='white', font=font)
out = folder / 'godot_actor_walk_contact.png'
canvas.save(out)
print(out)
