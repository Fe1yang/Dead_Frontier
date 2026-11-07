import struct, json, numpy as np
def load_glb(path):
    d=open(path,'rb').read(); clen,=struct.unpack('<I',d[12:16]); js=json.loads(d[20:20+clen]); off=20+clen; blen,=struct.unpack('<I',d[off:off+4]); binary=d[off+8:off+8+blen]; return js,binary
def acc(js,binary,idx):
    a=js['accessors'][idx]; bv=js['bufferViews'][a['bufferView']]; off=bv.get('byteOffset',0)+a.get('byteOffset',0); n=a['count']; nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]; dt={5126:'f4',5123:'u2',5125:'u4',5121:'u1'}[a['componentType']]; return np.frombuffer(binary,dtype=dt,count=n*nc,offset=off).reshape((n,nc)).astype(np.float64)
for f in ['assets/models/actors/survivor_male_universal.glb','assets/models/actors/survivor_jian_scout_universal.glb','assets/models/actors/survivor_jian_universal.glb']:
    js,b=load_glb(f)
    prim=js['meshes'][0]['primitives'][0]
    w=acc(js,b,prim['attributes']['WEIGHTS_0'])
    print(f, 'verts', len(w), 'amb<0.5', int((w.max(axis=1)<0.5).sum()), 'single', int((w>0.999).any(axis=1).sum()))
