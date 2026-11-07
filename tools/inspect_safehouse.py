import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'environment' / 'safehouse_interior.glb'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))
    hi = Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
    c = (lo + hi) / 2
    n_mat = len(obj.data.materials)
    print('OBJ %s verts=%d mats=%d center=(%.2f,%.2f,%.2f) size=(%.2f,%.2f,%.2f)' % (
        obj.name, len(obj.data.vertices), n_mat, c.x, c.y, c.z,
        hi.x - lo.x, hi.y - lo.y, hi.z - lo.z))
print('SAFEHOUSE_INSPECT_DONE')
