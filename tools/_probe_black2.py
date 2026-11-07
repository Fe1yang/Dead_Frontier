
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
obj = bpy.data.objects.get("Safe_black")
mw = obj.matrix_world
h = collections.Counter()
zs = collections.defaultdict(list)
for v in obj.data.vertices:
    p = mw @ v.co
    key = (round(p.x*2)/2, round(p.y*2)/2)
    h[key] += 1
    zs[key].append(p.z)
for (x,y),n in sorted(h.items(), key=lambda kv:-kv[1]):
    if n >= 20:
        zl = zs[(x,y)]
        print("CELL x=%.1f y=%.1f n=%d z %.2f..%.2f" % (x,y,n,min(zl),max(zl)))
