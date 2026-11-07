import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'environment' / 'safehouse_interior.glb'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))

# Back-wall strip with the boarded windows (Godot x -1.5..2.8, z -2.4..-3.7,
# height 0.9..2.7). Blender: x same, y = -godot_z, z = godot_y.
LO = Vector((-1.50, 2.40, 0.90))
HI = Vector((2.80, 3.70, 2.70))

obj = bpy.data.objects.get('Safe_wood_dark')
assert obj, 'Safe_wood_dark not found'
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
print('WOODDARK_RETINT faces', changed, 'slot', slot)

bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    o.select_set(True)
bpy.ops.export_scene.gltf(
    filepath=str(GLB), export_format='GLB', use_selection=True,
    export_animations=False, export_apply=False)
print('WOODDARK_RETINT exported', GLB)
