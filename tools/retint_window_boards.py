import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'environment' / 'safehouse_interior.glb'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))

# The boarded window behind the workbench (Godot: x 0.76..1.88, wall z -3.3,
# height 1.2..2.5). Blender: x same, y = -godot_z, z = godot_y.
LO = Vector((0.40, 2.60, 1.00))
HI = Vector((2.70, 3.60, 2.60))

obj = bpy.data.objects.get('Safe_wood')
assert obj, 'Safe_wood not found'
mw = obj.matrix_world

dark = bpy.data.materials.get('Safe_boards_dark')
if dark is None:
    dark = bpy.data.materials.new('Safe_boards_dark')
    dark.use_nodes = True
    bsdf = dark.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.055, 0.032, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.92

slot = next((i for i, m in enumerate(obj.data.materials) if m and m.name.startswith('Safe_boards_dark')), -1)
if slot < 0:
    obj.data.materials.append(dark)
    slot = len(obj.data.materials) - 1

changed = 0
for poly in obj.data.polygons:
    c = mw @ poly.center
    if LO.x <= c.x <= HI.x and LO.y <= c.y <= HI.y and LO.z <= c.z <= HI.z:
        poly.material_index = slot
        changed += 1
print('BOARDS_RETINT faces', changed, 'slot', slot)

bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    o.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(GLB), export_format='GLB', use_selection=True,
    export_animations=False, export_apply=False)
print('BOARDS_RETINT exported', GLB)
