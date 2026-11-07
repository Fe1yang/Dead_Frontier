
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
obj = bpy.data.objects.get("Safe_wood")
mw = obj.matrix_world
dark_i = None
for i, m in enumerate(obj.data.materials):
    if m and "dark" in m.name.lower():
        dark_i = i
print("dark slot", dark_i, "mats", [m.name if m else None for m in obj.data.materials])
h = collections.Counter(); cells = collections.defaultdict(list)
n=0
for poly in obj.data.polygons:
    if poly.material_index == dark_i:
        n+=1
        c = mw @ poly.center
        h[(round(c.x*2)/2, round(c.y*2)/2, round(c.z*2)/2)] += 1
        cells[(round(c.x*2)/2, round(c.y*2)/2, round(c.z*2)/2)].append(c)
print("dark faces", n)
for k, cnt in sorted(h.items(), key=lambda kv:-kv[1])[:15]:
    pts = cells[k]
    print("DCELL x=%.1f y=%.1f z=%.1f n=%d xr %.2f..%.2f zr %.2f..%.2f" % (k[0],k[1],k[2],cnt,min(p.x for p in pts),max(p.x for p in pts),min(p.z for p in pts),max(p.z for p in pts)))
