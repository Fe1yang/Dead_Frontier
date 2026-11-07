import struct, json, numpy as np
from PIL import Image, ImageDraw

def load_glb(path):
    d=open(path,'rb').read()
    clen,=struct.unpack('<I',d[12:16])
    js=json.loads(d[20:20+clen])
    off=20+clen
    blen,=struct.unpack('<I',d[off:off+4])
    binary=d[off+8:off+8+blen]
    return js,binary

def acc(js,binary,idx):
    a=js['accessors'][idx]
    bv=js['bufferViews'][a['bufferView']]
    off=bv.get('byteOffset',0)+a.get('byteOffset',0)
    n=a['count']; nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dt={5126:'f4',5123:'u2',5125:'u4',5121:'u1'}[a['componentType']]
    return np.frombuffer(binary,dtype=dt,count=n*nc,offset=off).reshape((n,nc)).astype(np.float64)

def render(path,out):
    js,binary=load_glb(path)
    prim=js['meshes'][0]['primitives'][0]
    pos=acc(js,binary,prim['attributes']['POSITION'])
    # front view: x horizontal, y vertical. Sample 8000 pts
    idx=np.random.RandomState(0).choice(len(pos),size=min(8000,len(pos)),replace=False)
    pts=pos[idx]
    W,H=400,800
    img=Image.new('RGB',(W,H),(20,20,20))
    dr=ImageDraw.Draw(img)
    x0,y0=pts[:,0].min(),pts[:,1].min(); x1,y1=pts[:,0].max(),pts[:,1].max()
    sx=(W-20)/(x1-x0); sy=(H-20)/(y1-y0); s=min(sx,sy)
    for x,y,z in pts:
        px=10+(x-x0)*s; py=H-10-(y-y0)*s
        c=int(255*(0.5+0.5*(z+0.3)/0.6))
        dr.ellipse([px,py,px+2,py+2],fill=(c,c,c))
    img.save(out)
    print(out, "x range",x0,x1,"y",y0,y1)
    # also print foot spacing: vertices y<0.15, x of left/right boots
    feet=pos[pos[:,1]<0.15]
    left=feet[feet[:,0]>0]; right=feet[feet[:,0]<0]
    print(" foot L center x",left[:,0].mean() if len(left) else None,"R",right[:,0].mean() if len(right) else None)
    # knee vs ankle x: bands
    for name,ylo,yhi in [('knee',0.40,0.55),('ankle',0.05,0.20),('thigh',0.70,0.90),('hand-ish',1.35,1.55)]:
        band=pos[(pos[:,1]>=ylo)&(pos[:,1]<=yhi)]
        l=band[band[:,0]>0.03]; r=band[band[:,0]<-0.03]
        print(f"  {name}: Lx={l[:,0].mean() if len(l) else 0:.3f} (n={len(l)}) Rx={r[:,0].mean() if len(r) else 0:.3f} (n={len(r)})")

for f,o in [('assets/models/actors/survivor_riley_universal.glb','renders/riley_bind.png'),('assets/models/actors/survivor_male_universal.glb','renders/mason_bind.png'),('assets/models/actors/survivor_maya_universal.glb','renders/maya_bind.png')]:
    render(f,o)
