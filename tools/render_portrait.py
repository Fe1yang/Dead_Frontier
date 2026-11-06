import bpy, sys, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
model = argv[0]                       # e.g. survivor_riley_universal.glb
out = Path(argv[1])                   # output png path
mode = argv[2] if len(argv) > 2 else 'portrait'   # 'portrait' (chest-up) or 'gray' (face)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'actors' / model))
bpy.context.view_layer.update()

low = Vector((1e9,)*3); high = Vector((-1e9,)*3)
for ob in bpy.data.objects:
    if ob.type != 'MESH': continue
    for c in ob.bound_box:
        w = ob.matrix_world @ Vector(c)
        low = Vector(map(min, low, w)); high = Vector(map(max, high, w))
h = high.z - low.z
cx = (low.x + high.x) / 2; cy = (low.y + high.y) / 2

if mode == 'gray':
    span = 0.20 * h; tz = high.z - 0.13 * h
else:
    span = 0.34 * h; tz = high.z - 0.185 * h
target = Vector((cx, cy, tz))

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'TEXTURE'
scene.render.resolution_x = 512; scene.render.resolution_y = 512
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
scene.collection.objects.link(cam)
d = (span / 2) / math.tan(math.radians(19.8))
cam.location = target + Vector((d * 0.10, -d, d * 0.10))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = 50; cam_data.clip_end = 100
scene.camera = cam

scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('saved', scene.render.filepath)
