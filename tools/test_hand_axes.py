import bpy, mathutils
def render_axis(axis_idx, out):
    glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='MATCAP'
    for ob in bpy.context.scene.objects:
        if ob.type=="ARMATURE":
            arm=ob
            for side in ["l","r"]:
                for finger in ["index","middle","ring","pinky"]:
                    for ph,ang in [(1,0.6),(2,0.6),(3,0.4)]:
                        name=f"{finger}_{ph:02d}_{side}"
                        if name in arm.pose.bones:
                            pb=arm.pose.bones[name]
                            pb.rotation_mode='XYZ'
                            e=[0,0,0]; e[axis_idx]=ang
                            pb.rotation_euler=tuple(e)
                for ph,ang in [(1,0.4)]:
                    name=f"thumb_{ph:02d}_{side}"
                    if name in arm.pose.bones:
                        pb=arm.pose.bones[name]
                        pb.rotation_mode='XYZ'
                        e=[0,0,0]; e[axis_idx]=ang
                        pb.rotation_euler=tuple(e)
            break
    bpy.ops.object.camera_add(location=(0.6,-0.6,1.1), rotation=(1.3,0,0.6))
    cam=bpy.context.active_object
    scene.camera=cam
    cam.data.lens=60
    import mathutils as mu
    target=mu.Vector((0.32,-0.02,0.85))
    dirvec = target - cam.location
    cam.rotation_euler = dirvec.to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x=640
    scene.render.resolution_y=640
    scene.render.filepath=out
    bpy.ops.render.render(write_still=True)
    print("saved",out)
for i,ax in enumerate(["X","Y","Z"]):
    render_axis(i, f"C:\\Users\\user\\Documents\\kimi\\tasks\\2026-11-02\\20-32-30-26dbcd78\\renders\\riley_hand_{ax}.png")
print("ALL DONE")
