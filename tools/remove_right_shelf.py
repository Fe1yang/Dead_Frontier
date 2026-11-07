import bpy
import bmesh
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'environment' / 'safehouse_interior.glb'
OUT = GLB  # in-place re-export

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))

# Region to clear (Blender axes; x=world x, y=Godot -z, z=Godot y): the slatted shelf
# on the right of the set: world x 1.55..2.8, y 0.3..2.05, z -2.75..-1.55 (Godot) ->
# Blender x 1.55..2.8, y 1.55..2.75, z 0.3..2.05.
LO = Vector((1.55, 1.55, 0.30))
HI = Vector((2.80, 2.75, 2.05))

target = bpy.data.objects.get('Safe_steel_dark')
if target is None:
    print('SHELF_REMOVE: Safe_steel_dark not found')
    raise SystemExit(1)

mw = target.matrix_world
bpy.context.view_layer.objects.active = target
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(target.data)
removed = 0
for v in list(bm.verts):
    p = mw @ v.co
    if LO.x <= p.x <= HI.x and LO.y <= p.y <= HI.y and LO.z <= p.z <= HI.z:
        bm.remove_vert(v)
        removed += 1
bmesh.update_edit_mesh(target.data)
bpy.ops.object.mode_set(mode='OBJECT')
print('SHELF_REMOVE deleted verts', removed)

bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(OUT), export_format='GLB', use_selection=True,
    export_animations=False, export_apply=False)
print('SHELF_REMOVE exported', OUT)
