"""Render a 512x512 chest-up portrait in the void for an actor GLB (transparent background).

Run: blender -b -P make_portrait.py -- <actor_glb> <out_png>
"""
import bpy, os, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SRC = argv[0]
OUT = argv[1]
ANGLE = int(argv[2]) if len(argv) > 2 else 90

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
bpy.context.view_layer.update()
# a portrait is the rest pose: drop any action the importer assigned
for o in bpy.context.scene.objects:
	if o.type == "ARMATURE":
		if o.animation_data:
			o.animation_data.action = None
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.55, 0.6, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.25


def light(name, loc, energy, size, target=(0, 0, 1.45)):
    L = bpy.data.objects.new(name, bpy.data.lights.new(name, type="AREA"))
    L.data.energy = energy
    L.data.size = size
    L.location = loc
    L.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(L)


light("key", (1.8, -2.2, 2.4), 420, 3.0)
light("fill", (-2.2, -1.0, 1.6), 120, 3.5)
light("rim", (-0.6, 2.6, 2.2), 260, 2.5)
# the old renders washed the whites and the skin out: pull the exposure down and add contrast
scene.view_settings.exposure = -0.45
try:
	scene.view_settings.look = "AgX - Punchy"
except Exception as exc:
	print("look skipped:", exc)

cam_data = bpy.data.cameras.new("c")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.0
cam = bpy.data.objects.new("c", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
# the imported character faces +X after the glTF import, so put the camera on +X
rad = math.radians(ANGLE)
pos = Vector((math.sin(rad) * 3.0, math.cos(rad) * -3.0, 0.95))
cam.location = pos
cam.rotation_euler = (Vector((0, 0, 0.95)) - pos).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("PORTRAIT_RENDERED", OUT)
