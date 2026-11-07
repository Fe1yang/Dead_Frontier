import struct, json, numpy as np, sys

def load_glb(path):
    d = open(path,'rb').read()
    assert d[:4]==b'glTF'
    clen, ctype = struct.unpack('<I4s', d[12:20])
    js = json.loads(d[20:20+clen])
    off = 20+clen
    blen, btype = struct.unpack('<I4s', d[off:off+8])
    binary = d[off+8:off+8+blen]
    return js, binary

def accessor_data(js, binary, idx):
    acc = js['accessors'][idx]
    bv = js['bufferViews'][acc['bufferView']]
    off = bv.get('byteOffset',0)+acc.get('byteOffset',0)
    n = acc['count']
    t = acc['type']
    comp = acc['componentType']
    ncomp = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[t]
    dtype = {5126:'f4',5123:'u2',5125:'u4',5121:'u1'}[comp]
    arr = np.frombuffer(binary, dtype=dtype, count=n*ncomp, offset=off).reshape((n,ncomp)).astype(np.float64)
    return arr

def analyze(path, label):
    js, binary = load_glb(path)
    print(f"=== {label} {path} ===")
    print("meshes:", len(js.get('meshes',[])), "nodes:", len(js.get('nodes',[])), "skins:", len(js.get('skins',[])))
    for mi, mesh in enumerate(js['meshes']):
        for pi, prim in enumerate(mesh['primitives']):
            pos = accessor_data(js, binary, prim['attributes']['POSITION'])
            print(f"  mesh {mi} prim {pi} verts={len(pos)} min={pos.min(axis=0)} max={pos.max(axis=0)}")
            # overall height axis: assume Y up? Print by y quantiles
            # analyze legs: lowest Y quarter, x spread
            ymin, ymax = pos[:,1].min(), pos[:,1].max()
            for frac, name in [(0.05,"feet"),(0.25,"calf"),(0.5,"thigh")]:
                ycut = ymin + (ymax-ymin)*frac
                # vertices within +-5% height band
                band = pos[(pos[:,1]>ycut-0.05*(ymax-ymin)) & (pos[:,1]<ycut+0.05*(ymax-ymin))]
                if len(band):
                    print(f"    {name} y~{ycut:.3f} count={len(band)} x_mean={band[:,0].mean():+.3f} x_min={band[:,0].min():+.3f} x_max={band[:,0].max():+.3f} z_mean={band[:,2].mean():+.3f}")
            # hands: likely near mid height, extreme X
            xmax = np.abs(pos[:,0]).max()
            band = pos[np.abs(pos[:,0])>xmax*0.8]
            if len(band):
                print(f"    extreme-X (hands?) x_max*0.8 count={len(band)} y_mean={band[:,1].mean():.3f} z_mean={band[:,2].mean():.3f}")
    skin = js['skins'][0]
    print("  joints:", skin['joints'][:10], "...")
    # joint world rests
    nib = accessor_data(js, binary, skin['inverseBindMatrices'])
    # nodes for joints
    for ji, node_idx in enumerate(skin['joints']):
        node = js['nodes'][node_idx]
        name = node.get('name','?')
        if name in ('thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r','hand_l','hand_r','lowerarm_l','lowerarm_r','upperarm_l','upperarm_r','pelvis','spine_01'):
            print(f"    joint {name} node={node_idx} bind_inv={np.round(nib[ji],3).tolist()}")

for f,l in [('assets/models/actors/survivor_riley_universal.glb','RILEY'),('assets/models/actors/survivor_male_universal.glb','MASON'),('assets/models/actors/survivor_maya_universal.glb','MAYA'),('assets/models/actors/survivor_medic_universal.glb','DARIUS'),('assets/models/actors/survivor_jian_scout_universal.glb','JIAN')]:
    try: analyze(f,l)
    except Exception as e: print(l, "ERR", e)
    print()
