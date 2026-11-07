import json, struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def joints(path):
    data=open(path,'rb').read()
    ln=struct.unpack('<I',data[12:16])[0]
    js=json.loads(data[20:20+ln])
    nodes=js['nodes']
    out={}
    for s in js.get('skins',[]):
        for i in s['joints']:
            n=nodes[i]
            out[n['name']]=(n.get('translation',[0,0,0]), n.get('rotation',[0,0,0,1]))
    return out, [a.get('name') for a in js.get('animations',[])]
a,aa=joints(ROOT/'assets/models/actors/survivor_male_universal.glb')
b,ba=joints(ROOT/'assets/models/actors/survivor_jian_scout_universal.glb')
diff=[k for k in a if k in b and (max(abs(x-y) for x,y in zip(a[k][0],b[k][0]))>0.001 or max(abs(x-y) for x,y in zip(a[k][1],b[k][1]))>0.001)]
print('JOINT_DIFF_COUNT', len(diff), diff[:10])
print('MASON_ACTIONS', sorted(aa))
print('SCOUT_ACTIONS', sorted(ba))
