import bpy, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'assets/models/generated/survivor_jian_hd.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
print('IMPORTED_MESHES',[(m.name,len(m.data.vertices),len(m.data.polygons)) for m in meshes])
for m in meshes:
    for p in m.data.polygons: p.use_smooth=True
    q=sum(1 for p in m.data.polygons if len(p.vertices)==4)
    t=sum(1 for p in m.data.polygons if len(p.vertices)==3)
    n=sum(1 for p in m.data.polygons if len(p.vertices)>4)
    print('TOPO',m.name,'quads',q,'tris',t,'ngons',n)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/models/generated/survivor_jian_hd.glb'),export_format='GLB')
print('CONVERTED_TO_GLB')
