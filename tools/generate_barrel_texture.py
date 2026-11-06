from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'textures'/'original'; OUT.mkdir(parents=True,exist_ok=True)
SIZE=1024
rng=np.random.default_rng(7319)

def noise_grid(w,h):
    a=rng.random((h,w)).astype(np.float32)
    return np.asarray(Image.fromarray((a*255).astype(np.uint8)).resize((SIZE,SIZE),Image.Resampling.BICUBIC),dtype=np.float32)/255.0

broad=noise_grid(10,14)
fine=noise_grid(90,120)
grain=rng.random((SIZE,SIZE)).astype(np.float32)
noise=(broad-.5)*30+(fine-.5)*18+(grain-.5)*7
base=np.zeros((SIZE,SIZE,3),dtype=np.float32)
base[:]=np.array([155,35,29])
base+=noise[:,:,None]
# Faded grey-white centre band, painted onto the barrel rather than borrowed.
y=np.arange(SIZE)[:,None]
band=(y>420)&(y<645)
band_color=np.array([181,177,153])+noise[:,:,None]*0.65
base=np.where(band[:,:,None],band_color,base)
img=Image.fromarray(np.uint8(np.clip(base,0,255)))
# Rust drips, chipped paint and small exposed-metal scratches.
overlay=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0)); draw=ImageDraw.Draw(overlay)
for _ in range(360):
    x=int(rng.integers(0,SIZE)); yy=int(rng.integers(0,SIZE))
    length=int(rng.integers(4,80)); width=int(rng.integers(1,5))
    alpha=int(rng.integers(25,105))
    draw.line((x,yy,x+int(rng.integers(-4,5)),min(SIZE,yy+length)),fill=(55,31,21,alpha),width=width)
for _ in range(210):
    x=int(rng.integers(0,SIZE)); yy=int(rng.integers(0,SIZE)); r=int(rng.integers(2,16))
    draw.ellipse((x-r,yy-r//2,x+r,yy+r//2),fill=(57,34,25,int(rng.integers(30,115))))
    if r>8: draw.arc((x-r,yy-r//2,x+r,yy+r//2),180,330,fill=(117,74,46,110),width=2)
for _ in range(120):
    x=int(rng.integers(0,SIZE)); yy=int(rng.integers(0,SIZE)); length=int(rng.integers(5,42))
    draw.line((x,yy,x+length,yy+int(rng.integers(-2,3))),fill=(196,180,147,int(rng.integers(30,95))),width=1)
overlay=overlay.filter(ImageFilter.GaussianBlur(0.45))
img=Image.alpha_composite(img.convert('RGBA'),overlay).convert('RGB')
path=OUT/'barrel_paint_original.png'; img.save(path)
print(path)
