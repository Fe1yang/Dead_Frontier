import bpy, sys, math
from pathlib import Path
from mathutils import Vector

# Studio bust portrait for a rigged universal survivor GLB: same 3-point lighting,
# ortho camera and framing as the male portraits (render_portraits.py), but without
# touching the mesh — rigged models stay in their bind pose.
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
model = argv[0]                       # e.g. survivor_riley_universal.glb
out = Path(argv[1])                   # output png path

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'actors' / model))
bpy.context.view_layer.update()

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
assert meshes, "no meshes in " + model
for o in meshes:
    for p in o.data.polygons: p.use_smooth = True

# Group everything under one empty, then normalise to portrait height (1.86) with
# feet on z=0, centred — the exact staging the male portraits were shot in.
root = bpy.data.objects.new('portrait_root', None)
bpy.context.scene.collection.objects.link(root)
tops = [o for o in bpy.data.objects if o != root and o.parent is None]
for o in tops: o.parent = root

def world_bounds():
    # Evaluated (armature-deformed) vertices: the raw mesh object transform ignores
    # the skeleton's scale, which would shrink the framing by ~100x.
    dg = bpy.context.evaluated_depsgraph_get()
    lo = Vector((1e9,)*3); hi = Vector((-1e9,)*3)
    for ob in meshes:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        for v in me.vertices:
            w = ev.matrix_world @ v.co
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
        ev.to_mesh_clear()
    return lo, hi

low, high = world_bounds()
h = high.z - low.z
s = 1.86 / h
root.scale = (s, s, s)
bpy.context.view_layer.update()
low2, high2 = world_bounds()
root.location = Vector((-(low2.x + high2.x) / 2, -(low2.y + high2.y) / 2, -low2.z))
bpy.context.view_layer.update()

def area(name, loc, energy, size, color):
    bpy.ops.object.light_add(type='AREA', location=loc)
    o = bpy.context.object; o.name = name
    o.data.energy = energy; o.data.shape = 'DISK'; o.data.size = size; o.data.color = color
    o.rotation_euler = (Vector((0, 0, 1.55)) - o.location).to_track_quat('-Z', 'Y').to_euler()

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32; scene.cycles.use_denoising = True
scene.render.resolution_x = 512; scene.render.resolution_y = 512
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
if scene.world is None:
    scene.world = bpy.data.worlds.new('World')
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value = (0.12, 0.15, 0.17, 1); bg.inputs[1].default_value = 0.45

area('Key', (-2.5, -3.5, 4.0), 420, 3.0, (1.0, 0.86, 0.72))
area('Fill', (2.5, -2.0, 2.5), 250, 2.5, (0.68, 0.80, 1.0))
area('Rim', (0, 2.0, 3.7), 380, 2.0, (1.0, 0.92, 0.80))

bpy.ops.object.camera_add(location=(0, -4.0, 1.70))
cam = bpy.context.object
cam.rotation_euler = (Vector((0, 0, 1.58)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = float(__import__('sys').argv[-1]) if __import__('sys').argv[-1].replace('.','').isdigit() else 0.74
scene.camera = cam

print('DBG h=',h,'cam=',scene.camera.data.type,scene.camera.data.ortho_scale,'loc=',tuple(scene.camera.location))
scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('PORTRAIT_RENDERED', model, scene.render.filepath)
