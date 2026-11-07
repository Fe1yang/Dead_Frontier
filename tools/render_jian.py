import struct, json, numpy as np
from PIL import Image, ImageDraw
def load_glb(path):
    d=open(path,'rb').read(); clen,=struct.unpack('<I',d[12:16]); js=json.loads(d[20:20+clen]); off=20+clen; blen,=struct.unpack('<I',d[off:off+4]); binary=d[off+8:off+8+blen]; return js,binary
def acc(js,binary,idx):
    a=js['accessors'][idx]; bv=js['bufferViews'][a['bufferView']]; off=bv.get('byteOffset',0)+a.get('byteOffset',0); n=a['count']; nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]; dt={5126:'f4',5123:'u2',5125:'u4',5121:'u1'}[a['componentType']]; return np.frombuffer(binary,dtype=dt,count=n*nc,offset=off).reshape((n,nc)).astype(np.float64)
for path,out in [('assets/models/actors/survivor_jian_scout_universal.glb','renders/jian_bind.png'),('assets/models/actors/survivor_jian_universal.glb','renders/jian2_bind.png')]:
    js,binary=load_glb(path)
    prim=js['meshes'][0]['primitives'][0]
    pos=acc(js,binary,prim['attributes']['POSITION'])
    idx=np.random.RandomState(0).choice(len(pos),size=min(8000,len(pos)),replace=False)
    pts=pos[idx]; W,H=400,800; img=Image.new('RGB',(W,H),(20,20,20)); dr=ImageDraw.Draw(img)
    x0,y0=pts[:,0].min(),pts[:,1].min(); x1,y1=pts[:,0].max(),pts[:,1].max(); s=min((W-20)/(x1-x0),(H-20)/(y1-y0))
    for x,y,z in pts:
        px=10+(x-x0)*s; py=H-10-(y-y0)*s; c=int(255*(0.5+0.5*(z+0.3)/0.6)); dr.ellipse([px,py,px+2,py+2],fill=(c,c,c))
    img.save(out); print(out, "done verts", len(pos))
    # check weight stats
    joints=acc(js,binary,prim['attributes']['JOINTS_0']).astype(int); weights=acc(js,binary,prim['attributes']['WEIGHTS_0'])
    # vertices with all zero weights? or huge discontinuity: neighbor diff? approximate: check joints range
    print("joint min/max", joints.min(), joints.max(), "weights sum mean", weights.sum(axis=1).mean())
    # count verts where max weight <0.5 (ambiguous)
    amb=(weights.max(axis=1)<0.5).sum(); print("ambiguous (<0.5) verts:", amb)
