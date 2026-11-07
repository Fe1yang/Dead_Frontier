import bpy, sys
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    print("OBJ", ob.type, ob.name)
    if ob.type=="ARMATURE":
        print(" BONES:")
        for bone in ob.pose.bones:
            if bone.name in ("thigh_l","thigh_r","calf_l","calf_r","foot_l","foot_r","ball_l","ball_r","hand_l","hand_r","lowerarm_l","lowerarm_r","upperarm_l","upperarm_r","clavicle_l","clavicle_r","pelvis"):
                print(f"  {bone.name}: head={tuple(round(v,3) for v in bone.head)} tail={tuple(round(v,3) for v in bone.tail)} quat={tuple(round(v,3) for v in bone.rotation_quaternion)} matrix={bone.matrix}")
    if ob.type=="MESH":
        print(" MESH verts", len(ob.data.vertices))
        # foot vertex spread in Blender (Z up)
        for side in ("l","r"):
            pass
        # print lowest vertices x spread
        vs=[v.co for v in ob.data.vertices if v.co.z<0.2]
        if vs:
            xs=[v.x for v in vs]
            print(f"  lowZ count={len(vs)} x_min={min(xs):.3f} x_max={max(xs):.3f}")
print("DONE")
