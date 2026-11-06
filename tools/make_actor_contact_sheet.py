from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
folder = root / 'diagnostics' / 'actor_axes'
views = [('neg_y', 'camera -Y'), ('pos_x', 'camera +X'), ('pos_y', 'camera +Y'), ('neg_x', 'camera -X')]
font = ImageFont.load_default(size=22)
canvas = Image.new('RGB', (4 * 384, 2 * 550), '#20252a')
draw = ImageDraw.Draw(canvas)
for row, actor in enumerate(('male', 'female')):
    for col, (view, label) in enumerate(views):
        path = folder / f'{actor}_{view}.png'
        image = Image.open(path).convert('RGB')
        canvas.paste(image, (col * 384, row * 550 + 38))
        draw.text((col * 384 + 14, row * 550 + 8), f'{actor}  {label}', fill='white', font=font)
out = folder / 'actor_axes_contact.png'
canvas.save(out)
print(out)
