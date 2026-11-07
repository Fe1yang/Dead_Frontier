import bpy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for name in ['survivor_male_universal','survivor_riley_universal','survivor_medic_universal','survivor_maya_universal','survivor_jian_universal']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors'/(name+'.glb')))
    for m in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        q=sum(1 for p in m.data.polygons if len(p.vertices)==4)
        t=sum(1 for p in m.data.polygons if len(p.vertices)==3)
        n=sum(1 for p in m.data.polygons if len(p.vertices)>4)
        print('TOPO',name,'verts',len(m.data.vertices),'quads',q,'tris',t,'ngons',n)
