import bpy
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
import sys
argv = sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/generated'/argv[0]))
meshes=[o for o in bpy.data.objects if o.type=='MESH']
print('MESH_OBJECTS', [(m.name, len(m.data.vertices), len(m.data.polygons)) for m in meshes])
for m in meshes:
    bpy.context.view_layer.objects.active=m
    bpy.ops.object.select_all(action='DESELECT'); m.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_loose_verts?
