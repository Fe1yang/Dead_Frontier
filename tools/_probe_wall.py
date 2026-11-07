
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
obj = bpy.data.objects.get("Safe_wall")
mw = obj.matrix_world
xs,ys,zs=[],[],[]
h = collections.Counter()
cellz = collections.defaultdict(list)
for v in obj.data.vertices:
    p = mw @ v.co
    xs.append(p.x); ys.append(p.y); zs.append(p.z)
    key=(round(p.x*2)/2, round(p.y*2)/2)
    h[key]+=1; cellz[key].append(p.z)
print("WALLBBOX x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f n=%d" % (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),len(xs)))
for (x,y),n in sorted(h.items(), key=lambda kv:-kv[1]):
    if n>=15:
        zl=cellz[(x,y)]
        print("WCELL x=%.1f y=%.1f n=%d z %.2f..%.2f" % (x,y,n,min(zl),max(zl)))
