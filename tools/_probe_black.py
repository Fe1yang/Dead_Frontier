
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
from mathutils import Vector
obj = bpy.data.objects.get("Safe_black")
mw = obj.matrix_world
xs,ys,zs=[],[],[]
for v in obj.data.vertices:
    p = mw @ v.co
    xs.append(p.x); ys.append(p.y); zs.append(p.z)
print("BLACKBBOX x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f n=%d" % (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),len(xs)))
# z-histogram to see clusters
import collections
h = collections.Counter(round(z*2)/2 for z in zs)
for k in sorted(h): print("ZHIST z=%.1f n=%d" % (k, h[k]))
