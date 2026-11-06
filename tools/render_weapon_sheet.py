import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'diagnostics' / 'weapons'
OUT.mkdir(parents=True, exist_ok=True)
WEAPONS = [('pistol', 'pistol.glb'), ('smg', 'smg.glb'), ('shotgun', 'shotgun.glb'), ('sniper', 'sniper.glb')]

def area(name, loc, energy, size, color, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy = energy
    obj.data.shape = 'DISK'
    obj.data.size = size
    obj.data.color = color
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

for name, filename in WEAPONS:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'assets' / 'models' / 'weapons' / filename))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    points = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
    low = Vector(tuple(min(v[i] for v in points) for i in range(3)))
    high = Vector(tuple(max(v[i] for v in points) for i in range(3)))
    center = (low + high) / 2
    size = max(high.x - low.x, high.y - low.y, high.z - low.z)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 640
    scene.render.resolution_y = 400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    bg.inputs[0].default_value = (0.15, 0.17, 0.19, 1)
    bg.inputs[1].default_value = 0.55
    area('Key', center + Vector((-2, -3, 4)), 300, 3, (1.0, 0.87, 0.73), center)
    area('Fill', center + Vector((3, 1, 2)), 240, 2.5, (0.68, 0.80, 1.0), center)
    bpy.ops.object.camera_add(location=center + Vector((2.4, -3.2, 2.1)))
    cam = bpy.context.object
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = size * 1.28
    scene.camera = cam
    scene.render.filepath = str(OUT / f'{name}.png')
    bpy.ops.render.render(write_still=True)
    print('WEAPON_RENDERED', name, 'dimensions', tuple(round(v, 3) for v in (high - low)))
