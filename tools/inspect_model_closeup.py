import bpy, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'diagnostics'
OUT.mkdir(exist_ok=True)

argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
model = argv[0] if argv else 'zombie_banshee_universal.glb'
frac = float(argv[1]) if len(argv) > 1 else 0.85   # vertical fraction of bbox to aim at
dist_scale = float(argv[2]) if len(argv) > 2 else 1.6
tag = argv[3] if len(argv) > 3 else 'model'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'actors' / model))
bpy.context.view_layer.update()

# World-space bounding box over all meshes.
low = Vector((1e9,)*3); high = Vector((-1e9,)*3)
for ob in bpy.data.objects:
    if ob.type != 'MESH': continue
    for c in ob.bound_box:
        w = ob.matrix_world @ Vector(c)
        low = Vector(map(min, low, w)); high = Vector(map(max, high, w))
center = (low + high) / 2
size = (high - low).length
target = Vector((center.x, center.y, low.z + (high.z-low.z)*frac))  # Blender 是 Z-up

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'TEXTURE'
scene.render.resolution_x = 640
scene.render.resolution_y = 640

cam_data = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_data)
scene.collection.objects.link(cam)
d = size * dist_scale * 0.5
cam.location = target + Vector((d*0.4, -d, d*0.06))  # 从 -Y 一侧看正面（glTF +Z 前脸 → Blender -Y）
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
cam_data.lens = 55
cam_data.clip_end = 1000

scene.render.filepath = str(OUT / ('inspect-%s.png' % tag))
bpy.ops.render.render(write_still=True)
print('saved', scene.render.filepath, '| bbox', tuple(low.round(2)), tuple(high.round(2)))
