import bpy, sys, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
model = argv[0]            # e.g. survivor_riley_universal.glb
out_prefix = Path(argv[1]) # diagnostics/deform/riley

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'actors' / model))
bpy.context.view_layer.update()

rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']

# --- weight stats ---
for mesh in meshes:
    total = len(mesh.data.vertices)
    unweighted = sum(1 for v in mesh.data.vertices if not v.groups)
    over4 = sum(1 for v in mesh.data.vertices if len([g for g in v.groups if g.weight > 0.01]) > 4)
    print('WEIGHTS', mesh.name, 'verts', total, 'unweighted', unweighted, 'over4', over4)

print('ACTIONS', [a.name for a in bpy.data.actions])
print('RIG_ACTION', rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'TEXTURE'
scene.render.resolution_x = 460; scene.render.resolution_y = 720
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
scene.collection.objects.link(cam)
cam_data.lens = 50; cam_data.clip_end = 100
scene.camera = cam

def frame_bounds():
    low = Vector((1e9,)*3); high = Vector((-1e9,)*3)
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in meshes:
        ev = ob.evaluated_get(dg).to_mesh()
        for v in ev.vertices:
            w = ob.matrix_world @ v.co
            low = Vector(map(min, low, w)); high = Vector(map(max, high, w))
        ob.evaluated_get(dg).to_mesh_clear()
    return low, high

def shot(name):
    low, high = frame_bounds()
    h = high.z - low.z
    target = Vector(((low.x+high.x)/2, (low.y+high.y)/2, (low.z+high.z)/2))
    span = h * 1.15
    d = (span/2) / math.tan(math.radians(19.8))
    offsets = {'front': (0, -d, 0), 'side': (d, 0, 0), 'back': (0, d, 0)}
    off = offsets[name.split('_')[0]]
    cam.location = target + Vector(off)
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(out_prefix) + '_' + name + '.png'
    bpy.ops.render.render(write_still=True)
    print('saved', scene.render.filepath)

run = bpy.data.actions.get('Run_Gun_Loop')
if run and rig.animation_data:
    rig.animation_data.action = run
    if run.slots: rig.animation_data.action_slot = run.slots[0]
    scene.frame_set(int(run.frame_range[0]))
    bpy.context.view_layer.update()
    shot('front_f0')
    mid = int((run.frame_range[0] + run.frame_range[1]) / 2)
    scene.frame_set(mid)
    bpy.context.view_layer.update()
    shot('front_mid')
    shot('side_mid')
else:
    scene.frame_set(0)
    bpy.context.view_layer.update()
    shot('front_f0')
    shot('side_mid')
print('DEFORM_DIAG_DONE')
