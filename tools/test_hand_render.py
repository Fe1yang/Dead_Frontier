import bpy, math
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
# setup render
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='MATCAP'
# Find armature
for ob in bpy.context.scene.objects:
    if ob.type=="ARMATURE":
        arm=ob
        # pose fingers: try rotation on local X 0.55 rad
        for side in ["l","r"]:
            for finger in ["index","middle","ring","pinky"]:
                for ph,ang in [(1,0.55),(2,0.60),(3,0.40)]:
                    name=f"{finger}_{ph:02d}_{side}"
                    if name in arm.pose.bones:
                        pb=arm.pose.bones[name]
                        pb.rotation_mode='XYZ'
                        pb.rotation_euler=(ang,0,0)
            for ph,ang in [(1,0.35),(2,0.40),(3,0.30)]:
                name=f"thumb_{ph:02d}_{side}"
                if name in arm.pose.bones:
                    pb=arm.pose.bones[name]
                    pb.rotation_mode='XYZ'
                    pb.rotation_euler=(ang,0,0)
        break
# frame shot
bpy.ops.object.camera_add(location=(0,-3.5,1.2), rotation=(1.45,0,0))
cam=bpy.context.active_object
scene.camera=cam
cam.data.lens=40
# aim at right hand
import mathutils
target=mathutils.Vector((0.28,0,0.9))
dirvec = target - cam.location
cam.rotation_euler = dirvec.to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=640
scene.render.resolution_y=640
scene.render.filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_hand_test.png"
bpy.ops.render.render(write_still=True)
print("rendered")
