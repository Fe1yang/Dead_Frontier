import bpy
from mathutils import Vector
src = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 540
scene.render.resolution_y = 960
scene.render.filepath = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\icons\p_covers\ken_preview.png"
# strong key + fill so the dark jacket reads
sun = bpy.data.lights.new("Sun", "SUN")
sun.energy = 5
so = bpy.data.objects.new("Sun", sun)
scene.collection.objects.link(so)
so.location = (1.5, -2.5, 4)
fill = bpy.data.lights.new("Fill", "POINT")
fill.energy = 120
fill.color = (1.0, 0.85, 0.6)
fo = bpy.data.objects.new("Fill", fill)
scene.collection.objects.link(fo)
fo.location = (0, -3, 2)
cam = bpy.data.cameras.new("Cam")
cam.angle = 0.55
camo = bpy.data.objects.new("Cam", cam)
scene.collection.objects.link(camo)
scene.camera = camo
camo.location = (0, -3.4, 1.1)
# point at center of character (0,0,0.9)
d = Vector((0, 0, 0.9)) - Vector(camo.location)
camo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("PREVIEW_OK", scene.render.filepath)
