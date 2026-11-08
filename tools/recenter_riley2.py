"""Recentre the retargeted Riley GLB (v2).

The first pass was fooled by a stray `Icosphere` mesh left in the retarget file, and it also
moved the body up by 1 m. This version deletes the stray mesh, measures only the character,
and puts the feet on the floor (Blender Z=0) with the body centred on X/Y.
"""
import bpy, os
from mathutils import Vector

WORK = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors"
SRC = os.path.join(WORK, "survivor_riley_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
bpy.context.view_layer.update()

# drop scene junk that is not the character body
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.name not in ("HighDetailCharacter",):
        print("DELETING STRAY", o.name)
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()

body = bpy.data.objects["HighDetailCharacter"]
lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
for c in body.bound_box:
    w = body.matrix_world @ Vector(c)
    lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
    hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
print("BODY_BBOX", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))

offset = Vector((-(lo.x + hi.x) * 0.5, -(lo.y + hi.y) * 0.5, -lo.z))
print("OFFSET", tuple(round(v, 3) for v in offset))
for o in [o for o in bpy.context.scene.objects if o.parent is None]:
    o.location += offset
bpy.context.view_layer.update()

lo2 = Vector((1e9, 1e9, 1e9)); hi2 = Vector((-1e9, -1e9, -1e9))
for c in body.bound_box:
    w = body.matrix_world @ Vector(c)
    lo2 = Vector((min(lo2.x, w.x), min(lo2.y, w.y), min(lo2.z, w.z)))
    hi2 = Vector((max(hi2.x, w.x), max(hi2.y, w.y), max(hi2.z, w.z)))
print("BODY_BBOX_AFTER", tuple(round(v, 3) for v in lo2), tuple(round(v, 3) for v in hi2))

# portrait render: front, chest-up, transparent background (the "void")
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.46, 0.52, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.05

key = bpy.data.objects.new("key", bpy.data.lights.new("key", type="AREA"))
key.data.energy = 600; key.data.size = 3.0
key.location = (1.6, -2.6, 2.1)
key.rotation_euler = (Vector((0, 0, 1.45)) - Vector(key.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(key)
fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", type="AREA"))
fill.data.energy = 220; fill.data.size = 3.5
fill.location = (-2.0, -1.6, 1.5)
fill.rotation_euler = (Vector((0, 0, 1.45)) - Vector(fill.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(fill)
rim = bpy.data.objects.new("rim", bpy.data.lights.new("rim", type="AREA"))
rim.data.energy = 350; rim.data.size = 2.5
rim.location = (-1.0, 2.4, 2.2)
rim.rotation_euler = (Vector((0, 0, 1.5)) - Vector(rim.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(rim)

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 0.95          # head and chest fill the frame
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
target = Vector((0.0, 0.0, 1.50))
cam.location = Vector((0.0, -3.0, 1.52))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()

scene.render.filepath = os.path.join(WORK, "riley_new_portrait.png")
bpy.ops.render.render(write_still=True)
print("PORTRAIT", scene.render.filepath)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=SRC,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=True,
    export_apply=False,
)
print("REEXPORTED", SRC)
