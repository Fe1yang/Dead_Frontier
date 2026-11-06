from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
import numpy as np
import shutil

ROOT=Path(__file__).resolve().parents[1]
PH=ROOT/'assets'/'textures'/'polyhaven'
NEW=PH/'concrete_wall_neutral'
NEW.mkdir(parents=True,exist_ok=True)
source=PH/'concrete_wall_003'/'concrete_wall_003_diff_2k.jpg'
im=Image.open(source).convert('RGB')
g=ImageOps.grayscale(im)
g=ImageEnhance.Contrast(g).enhance(0.34)
g=ImageOps.autocontrast(g,cutoff=0.5)
neutral=ImageOps.colorize(g,black='#555b5c',white='#c5c7c3')
neutral=Image.blend(neutral,Image.new('RGB',neutral.size,'#aeb2af'),0.16)
neutral.save(NEW/'concrete_wall_neutral_diff_2k.jpg',quality=94,subsampling=0)
for kind in ('nor_gl','rough','ao'):
    src=PH/'concrete_wall_003'/f'concrete_wall_003_{kind}_2k.jpg'
    if src.exists(): shutil.copy2(src,NEW/f'concrete_wall_neutral_{kind}_2k.jpg')

TEX=ROOT/'assets'/'textures'/'street_debris'
TEX.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(741103)
# Small tiling maps retain surface detail without making each prop GLB heavy.
small=neutral.resize((512,512),Image.Resampling.LANCZOS)
small.save(TEX/'fractured_concrete.png')
a=np.asarray(small).astype(np.float32)
brick=np.clip(a*np.array([0.83,0.54,0.43])+np.array([34,23,20]),0,255).astype(np.uint8)
Image.fromarray(brick).save(TEX/'broken_brick.png')

w=h=512
y,x=np.mgrid[0:h,0:w]
noise=rng.normal(0,2.2,(h,w))
grain=5*np.sin(x*0.24+2*np.sin(y*0.012))+2.5*np.sin(x*0.91+y*0.007)
base=np.array([107,91,70])[None,None,:]+grain[:,:,None]+noise[:,:,None]
wood=Image.fromarray(np.clip(base,0,255).astype(np.uint8))
d=ImageDraw.Draw(wood,'RGBA')
for i in range(34):
    xx=int(rng.integers(0,w)); d.line([(xx,0),(xx+int(rng.integers(-10,11)),h)],fill=(30,25,19,int(rng.integers(15,50))),width=1)
wood.save(TEX/'weathered_wood.png')

paper_arr=np.ones((512,512,3),dtype=np.float32)*np.array([184,181,163])
paper_arr+=rng.normal(0,3.0,(512,512,1))
paper=Image.fromarray(np.clip(paper_arr,0,255).astype(np.uint8))
d=ImageDraw.Draw(paper)
try:
    title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',36)
    body=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
except OSError:
    title=ImageFont.load_default(); body=title
d.rectangle((25,24,487,85),fill=(53,55,51))
d.text((40,35),'CITY EVACUATION',font=title,fill=(202,199,179))
d.text((28,101),'DEAD FRONTIER  /  EMERGENCY EDITION',font=body,fill=(62,60,53))
for col in range(3):
    x0=28+col*157
    for row in range(24):
        yy=137+row*13
        length=int(rng.integers(105,143))
        d.line((x0,yy,x0+length,yy),fill=(92,90,80),width=2)
d.rectangle((184,132,334,253),fill=(104,104,95))
d.rectangle((190,138,328,247),outline=(62,62,57),width=2)
paper=paper.filter(ImageFilter.GaussianBlur(0.25))
paper.save(TEX/'evacuation_newspaper.png')
print('STREET_TEXTURES_READY',NEW,TEX)
