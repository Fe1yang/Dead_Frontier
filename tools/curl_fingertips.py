import bpy, mathutils
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter":
        mesh=ob; break
moved=0
for v in mesh.data.vertices:
    if v.co.x>0.72 and abs(v.co.z-1.45)<0.10:
        pivot=mathutils.Vector((0.72,0,1.45))
        ang=mathutils.Euler((0,0,-0.50))
        v.co = pivot + ang.to_matrix() @ (v.co-pivot)
        moved+=1
    if v.co.x<-0.72 and abs(v.co.z-1.45)<0.10:
        pivot=mathutils.Vector((-0.72,0,1.45))
        ang=mathutils.Euler((0,0,0.50))
        v.co = pivot + ang.to_matrix() @ (v.co-pivot)
        moved+=1
print("moved tips only",moved)
mesh.data.update()
bpy.ops.export_scene.gltf(filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_fingertip_curl.glb", export_format="GLB", export_yup=True, export_apply=True)
print("exported")
