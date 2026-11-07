import struct, json, numpy as np

def load_glb(path):
    d = open(path,'rb').read()
    clen, = struct.unpack('<I', d[12:16])
    js = json.loads(d[20:20+clen])
    off = 20+clen
    blen, = struct.unpack('<I', d[off:off+4])
    binary = d[off+8:off+8+blen]
    return js, binary

def acc(js,binary,idx):
    a=js['accessors'][idx]
    bv=js['bufferViews'][a['bufferView']]
    off=bv.get('byteOffset',0)+a.get('byteOffset',0)
    n=a['count']; nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    dt={5126:'f4',5123:'u2',5125:'u4',5121:'u1',5124:'i4'}[a['componentType']]
    return np.frombuffer(binary,dtype=dt,count=n*nc,offset=off).reshape((n,nc)).astype(np.float64)

def analyze(path,label):
    js,binary=load_glb(path)
    skin=js['skins'][0]
    joint_names=[js['nodes'][j].get('name','?') for j in skin['joints']]
    prim=js['meshes'][0]['primitives'][0]
    pos=acc(js,binary,prim['attributes']['POSITION'])
    joints=acc(js,binary,prim['attributes']['JOINTS_0']).astype(int)
    weights=acc(js,binary,prim['attributes']['WEIGHTS_0'])
    # dominant joint centroid
    dom=joints[:,0]
    print(f"\n=== {label} verts={len(pos)} ===")
    for name in ['thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r','hand_l','hand_r','lowerarm_l','lowerarm_r','upperarm_l','upperarm_r']:
        ji=joint_names.index(name)
        m=dom==ji
        if m.sum()==0: continue
        c=pos[m].mean(axis=0)
        print(f"  {name}: count={m.sum()} center={np.round(c,3)} x_min={pos[m][:,0].min():+.3f} x_max={pos[m][:,0].max():+.3f}")
    # hand fingers: vertices where any joint is hand
    for side in ['l','r']:
        ji=joint_names.index('hand_'+side)
        m=(joints==ji).any(axis=1)
        if m.sum():
            c=pos[m].mean(axis=0)
            print(f"  HAND-any {side}: count={m.sum()} center={np.round(c,3)}")
    # leg symmetry: thigh center x distance from 0
    for name in ['foot_l','foot_r']:
        ji=joint_names.index(name)
        m=dom==ji
        if m.sum():
            print(f"    {name} center x={pos[m].mean(axis=0)[0]:+.3f}")

for f,l in [('assets/models/actors/survivor_riley_universal.glb','RILEY'),('assets/models/actors/survivor_male_universal.glb','MASON'),('assets/models/actors/survivor_maya_universal.glb','MAYA'),('assets/models/actors/survivor_medic_universal.glb','DARIUS'),('assets/models/actors/survivor_jian_scout_universal.glb','JIAN')]:
    analyze(f,l)
