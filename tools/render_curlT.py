import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_curlT.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='MATCAP'
# top-down view of hands to see curl
bpy.ops.object.camera_add(location=(0.75,0,2.2), rotation=(0,0,0))
cam=bpy.context.active_object
scene.camera=cam
cam.data.lens=40
scene.render.resolution_x=640
scene.render.resolution_y=640
scene.render.filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_curlT_top.png"
bpy.ops.render.render(write_still=True)
print("saved")
