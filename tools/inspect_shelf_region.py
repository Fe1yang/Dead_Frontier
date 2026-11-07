import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'environment' / 'safehouse_interior.glb'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB))

# Probe the region blender x 1.3..3.0, y 1.3..3.0 (right side of room)
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    mw = obj.matrix_world
    pts = [mw @ v.co for v in obj.data.vertices
           if 1.3 <= (mw @ v.co).x <= 3.0 and 1.3 <= (mw @ v.co).y <= 3.0]
    if not pts:
        continue
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    print('REGION %s n=%d x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f' % (
        obj.name, len(pts), min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
print('REGION_DONE')
