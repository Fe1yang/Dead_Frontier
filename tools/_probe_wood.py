
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
for name in ["Safe_wood","Safe_wood_dark"]:
    obj = bpy.data.objects.get(name)
    if obj is None:
        print("MISSING", name); continue
    mw=obj.matrix_world
    h=collections.Counter(); cellz=collections.defaultdict(list)
    for v in obj.data.vertices:
        p=mw@v.co
        key=(round(p.x*2)/2, round(p.y*2)/2, round(p.z))
        h[key]+=1; cellz[key].append(p)
    print("== %s total=%d" % (name, len(obj.data.vertices)))
    shown=0
    for (x,y,z),n in sorted(h.items(), key=lambda kv:-kv[1]):
        if n>=8 and z>=0.8 and shown<25:
            pts=cellz[(x,y,z)]
            print("  CL x=%.1f y=%.1f z=%d n=%d xr %.2f..%.2f" % (x,y,z,n,min(p.x for p in pts),max(p.x for p in pts)))
            shown+=1
