
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
obj = bpy.data.objects.get("Safe_wood")
mw = obj.matrix_world
LO=(0.3,2.8,0.8); HI=(2.8,4.3,2.8)
h=collections.Counter(); cells=collections.defaultdict(list)
for poly in obj.data.polygons:
    c = mw @ poly.center
    if LO[0]<=c.x<=HI[0] and LO[1]<=c.y<=HI[1] and LO[2]<=c.z<=HI[2]:
        key=(round(c.y*2)/2,)
        h[key]+=1; cells[key].append(c)
for k,n in sorted(h.items(), key=lambda kv:-kv[1]):
    pts=cells[k]
    print("YCELL y=%.1f n=%d x %.2f..%.2f z %.2f..%.2f" % (k[0],n,min(p.x for p in pts),max(p.x for p in pts),min(p.z for p in pts),max(p.z for p in pts)))
