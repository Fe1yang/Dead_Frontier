import bpy, mathutils
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None; arm=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter": mesh=ob
    if ob.type=="ARMATURE": arm=ob
bone=arm.pose.bones.get("index_01_l")
pivot=bone.head.copy(); tip=bone.tail.copy()
print("pivot",list(pivot),"tip",list(tip))
fdir=(pivot-tip).normalized()
print("fdir flipped",list(fdir))
dists=[]
for v in mesh.data.vertices:
    to_v=v.co-pivot
    t=to_v.dot(fdir)
    if -0.01<t<0.12:
        closest=pivot+fdir*max(0.0,t)
        d=(v.co-closest).length
        dists.append((d,t,list(v.co)))
dists.sort(key=lambda x:x[0])
print("near verts",len(dists))
for d,t,co in dists[:10]:
    print(f"d={d:.4f} t={t:.4f} co={[round(x,3) for x in co]}")
print("DONE")
