import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets' / 'models' / 'generated'
OUT = ROOT / 'diagnostics' / 'actor_axes_normalized'
OUT.mkdir(parents=True, exist_ok=True)
ACTORS = [('male', 'survivor_male_hd.glb'), ('female', 'survivor_female_hd.glb')]
VIEWS = [('neg_y', (0, -6, 1.05)), ('pos_x', (6, 0, 1.05)), ('pos_y', (0, 6, 1.05)), ('neg_x', (-6, 0, 1.05))]

def area(name, loc, energy, size, color):
    bpy.ops.object.light_add(type='AREA', location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy = energy
    obj.data.shape = 'DISK'
    obj.data.size = size
    obj.data.color = color
    obj.rotation_euler = (Vector((0, 0, 1.0)) - obj.location).to_track_quat('-Z', 'Y').to_euler()

for key, filename in ACTORS:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(SRC / filename))
    meshes = [o for o in bpy.context.scene.objects if o not in before and o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    coords = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    low = Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    high = Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    scale = 1.86 / (high.z - low.z)
    obj.scale = (scale,) * 3
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler.z = -math.pi / 2
    bpy.context.view_layer.update()
    print('NORMALIZED_TRANSFORM', key, 'parent', obj.parent, 'rotation', tuple(obj.rotation_euler), 'world', obj.matrix_world)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    coords = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    low = Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    high = Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    obj.location += Vector((-(low.x + high.x) / 2, -(low.y + high.y) / 2, -low.z))
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 384
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    bg.inputs[0].default_value = (0.16, 0.18, 0.20, 1)
    bg.inputs[1].default_value = 0.55
    area('Key', (-2.5, -3.5, 4), 400, 3.0, (1.0, 0.88, 0.76))
    area('Fill', (3.0, 2.0, 3), 350, 3.0, (0.72, 0.82, 1.0))
    area('Top', (0, 0, 5), 250, 2.0, (1.0, 1.0, 1.0))
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 2.18
    cam.data.clip_end = 100
    scene.camera = cam
    for view, loc in VIEWS:
        cam.location = loc
        cam.rotation_euler = (Vector((0, 0, 1.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(OUT / f'{key}_{view}.png')
        bpy.ops.render.render(write_still=True)
        print('AXIS_VIEW', key, view, 'dimensions', tuple(round(v, 3) for v in obj.dimensions))
