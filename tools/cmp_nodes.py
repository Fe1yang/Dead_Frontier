import struct, json
def nodes(f):
    d=open(f,'rb').read(); clen,=struct.unpack('<I',d[12:16]); js=json.loads(d[20:20+clen])
    return js['nodes']
a=nodes('assets/models/actors/survivor_riley_universal.glb')
b=nodes('assets/models/actors/survivor_male_universal.glb')
c=nodes('assets/models/actors/survivor_maya_universal.glb')
for i,(x,y) in enumerate(zip(a,b)):
    if x!=y:
        print(i, x.get('name'), y.get('name'))
        print(' RILEY', x)
        print(' MASON', y)
print('--- maya vs riley ---')
for i,(x,y) in enumerate(zip(a,c)):
    if x!=y:
        print(i, x.get('name'), y.get('name'))
        print(' RILEY', x)
        print(' MAYA', y)
print('done')
