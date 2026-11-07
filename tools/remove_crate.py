import bpy
import bmesh
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'environment' / 'safehouse_interior.glb'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))

# The circled slatted crate under the workbench (Godot: x 0.46..0.96, z -2.7..-3.2,
# height 0.17..1.07). Blender mapping: same x, y = -godot_z, z = godot_y.
LO = Vector((0.20, 2.60, 0.00))
HI = Vector((1.35, 3.40, 1.20))

target = bpy.data.objects.get('Safe_wall')
assert target, 'Safe_wall not found'
mw = target.matrix_world
bpy.context.view_layer.objects.active = target
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(target.data)
to_del = [v for v in bm.verts
          if LO.x <= (mw @ v.co).x <= HI.x
          and LO.y <= (mw @ v.co).y <= HI.y
          and LO.z <= (mw @ v.co).z <= HI.z]
removed = len(to_del)
bmesh.ops.delete(bm, geom=to_del, context='VERTS')
bmesh.update_edit_mesh(target.data)
bpy.ops.object.mode_set(mode='OBJECT')
print('CRATE_REMOVE deleted verts', removed)

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(GLB), export_format='GLB', use_selection=True,
    export_animations=False, export_apply=False)
print('CRATE_REMOVE exported', GLB)
