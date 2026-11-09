"""Store/lobby portrait from the REST pose: no animation, front camera, head-and-chest crop.

Run: blender -b -P char_portrait_rest.py -- <glb> <out.png>
"""
import bpy, os, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
GLB, OUT = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
if arm and arm[0].animation_data:
    arm[0].animation_data.action = None          # REST pose, not the idle clip
    for pb in arm[0].pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = 900
sc.render.resolution_y = 900
sc.render.film_transparent = True
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.exposure = -0.35
try:
    sc.view_settings.look = "AgX - Punchy"
except Exception:
    pass
if sc.world is None:
    sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.46, 0.5, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.85
for loc, en, size in (((1.8, -2.2, 2.2), 420, 3.0), ((-2.0, -1.4, 1.6), 140, 3.5),
                      ((-0.4, 2.4, 2.0), 260, 2.5)):
    L = bpy.data.objects.new("L", bpy.data.lights.new("L", type="AREA"))
    L.data.energy = en
    L.data.size = size
    L.location = loc
    L.rotation_euler = (Vector((0, 0, 1.5)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(L)

# head bone position -> frame the head and chest
head = None
if arm:
    for n in ("head", "Head", "head_01"):
        if n in arm[0].data.bones:
            head = arm[0].matrix_world @ arm[0].data.bones[n].head_local
            break
if head is None:
    box = [o.matrix_world @ Vector(c) for o in bpy.context.scene.objects if o.type == "MESH"
           for c in o.bound_box]
    head = Vector((0, 0, max(p.z for p in box) * 0.92))

target = Vector((head.x, head.y, head.z - 0.06))
cd = bpy.data.cameras.new("c")
cd.type = "ORTHO"
cd.ortho_scale = 0.78          # ~head + shoulders, same for every character
cam = bpy.data.objects.new("c", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = target + Vector((0, -3.0, 0.02))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("PORTRAIT", OUT, "ortho", cd.ortho_scale, "head", tuple(round(v, 2) for v in head))
