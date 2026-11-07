import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter":
        mesh=ob; break
from collections import defaultdict
adj=defaultdict(set)
for p in mesh.data.polygons:
    vs=list(p.vertices)
    for i in vs:
        for j in vs:
            if i!=j: adj[i].add(j)
# Pull pointed chest back a touch (front = -Y)
for v in mesh.data.vertices:
    x,y,z = v.co.x, v.co.y, v.co.z
    if 1.0 <= z <= 1.4 and y < 0.0:
        v.co.y = y*0.92 + 0.02*0.08
mesh.data.update()
for _ in range(3):
    new = {}
    for v in mesh.data.vertices:
        if not (0.80 <= v.co.z <= 1.55): continue
        nbrs = adj.get(v.index, [])
        if not nbrs: continue
        acc = v.co.copy()
        for ni in nbrs:
            acc += mesh.data.vertices[ni].co
        new[v.index] = acc/(len(nbrs)+1)
    for idx, c in new.items():
        mesh.data.vertices[idx].co = mesh.data.vertices[idx].co*0.70 + c*0.30
mesh.data.update()
print("smoothed")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("exported")
