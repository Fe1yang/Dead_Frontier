import bpy, mathutils
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
mesh=None; arm=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter": mesh=ob
    if ob.type=="ARMATURE": arm=ob
def bone(name):
    return arm.pose.bones.get(name)
def curl_side(side):
    palm_dir = mathutils.Vector((-1 if side=="l" else 1,0,0))
    moved_total=0
    for finger in ["index","middle","ring","pinky"]:
        prox = bone(f"{finger}_01_{side}")
        if prox is None: continue
        distal_name = f"{finger}_{side}"  # not exist; find leaf
        # find last bone in chain: try _03 or _04_leaf
        tip = None
        for suffix in ["_04_leaf_","_03_","_02_","_01_"]:
            b = bone(f"{finger}{suffix}{side}")
            if b: tip = b.tail.copy(); break
        if tip is None: continue
        pivot = prox.head.copy()
        # Bone tail points back toward the wrist in this rig; the mesh fingers extend the opposite way.
        fdir = (pivot - tip).normalized()
        axis = fdir.cross(palm_dir)
        if axis.length < 1e-4: continue
        axis.normalize()
        angle = 0.55  # ~31deg half-fist
        quat = mathutils.Quaternion(axis, angle)
        moved=0
        for v in mesh.data.vertices:
            # distance to segment pivot->tip
            to_v = v.co - pivot
            t = to_v.dot(fdir)
            if t < -0.002 or t > 0.15: continue
            closest = pivot + fdir*max(0.0,min(t, (tip-pivot).length))
            d = (v.co - closest).length
            if d > 0.040: continue
            # rotate toward palm around proximal pivot (rigid whole-finger curl)
            v.co = pivot + quat @ (v.co - pivot)
            moved+=1
        moved_total+=moved
        print(finger, side, "moved", moved, "pivot", list(pivot), "tip", list(tip), "fdir", list(fdir))
    print(side, "TOTAL moved", moved_total)
curl_side("l")
curl_side("r")
mesh.data.update()
print("vertex curled")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("exported riley")
