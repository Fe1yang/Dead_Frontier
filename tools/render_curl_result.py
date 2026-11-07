import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_test_curl.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='MATCAP'
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
scene.render.filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_curl_result.png"
bpy.ops.render.render(write_still=True)
print("saved")
