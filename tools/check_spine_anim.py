import struct, json, numpy as np, sys

def load(path):
    d=open(path,'rb').read()
    clen,=struct.unpack('<I',d[12:16])
    js=json.loads(d[20:20+clen])
    off=20+clen
    blen,=struct.unpack('<I',d[off:off+4])
    binary=d[off+8:off+8+blen]
    return js,binary

def read_accessor(js,binary,idx):
    a=js['accessors'][idx]
    bv=js['bufferViews'][a['bufferView']]
    off=bv.get('byteOffset',0)+a.get('byteOffset',0)
    n=a['count']
    ncomp={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
    dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']]
    arr=np.frombuffer(binary,dtype=dtype,count=n*ncomp,offset=off).reshape((n,ncomp)).astype(np.float64)
    return arr

def analyze(path):
    js,b=load(path)
    nodes=js['nodes']
    name_to_idx={n.get('name',''):i for i,n in enumerate(nodes)}
    for anim in js.get('animations',[]):
        if anim['name'] not in ('Run_Gun_Loop','Run_Gun_F_Loop'): continue
        print(f"\n== {path} anim {anim['name']} channels {len(anim['channels'])} samplers {len(anim['samplers'])}")
        # group by node+path
        from collections import defaultdict
        chans=defaultdict(list)
        for ch in anim['channels']:
            node_idx=ch['target']['node']
            pname=ch['target']['path']
            chans[(nodes[node_idx].get('name'),pname)].append(ch)
        for (nname,pname), chs in sorted(chans.items()):
            if nname not in ('spine_01','spine_02','spine_03','pelvis','clavicle_l','clavicle_r','upperarm_l','upperarm_r','lowerarm_l','lowerarm_r'): continue
            for ch in chs:
                samp=anim['samplers'][ch['sampler']]
                out=read_accessor(js,b,samp['output'])
                if pname=='rotation':
                    # quaternions -> check dominant axis oscillation: convert to small angles? print quart range
                    # print min/max quat components
                    print(f" {nname} rot keys={len(out)} min={np.round(out.min(axis=0),3)} max={np.round(out.max(axis=0),3)}")
                elif pname=='translation':
                    print(f" {nname} trans keys={len(out)} min={np.round(out.min(axis=0),3)} max={np.round(out.max(axis=0),3)}")

for f in ['assets/models/actors/survivor_male_universal.glb','assets/models/actors/survivor_riley_universal.glb','assets/models/actors/survivor_medic_universal.glb','assets/models/actors/survivor_maya_universal.glb','assets/models/actors/survivor_jian_scout_universal.glb']:
    analyze(f)
