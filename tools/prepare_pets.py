import bpy
import json
import math
import shutil
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PETS = ROOT / 'assets' / 'models' / 'pets'
RAW = ROOT / 'assets' / 'models' / 'generated'
SOURCE = ROOT / 'assets' / 'blender' / 'pets'
RENDERS = ROOT / 'renders' / 'pets'
for folder in (PETS, RAW, SOURCE, RENDERS):
    folder.mkdir(parents=True, exist_ok=True)

SPECS = {
    'doberman': {'height': 0.82, 'label': 'DOBERMAN'},
    'german_shepherd': {'height': 0.78, 'label': 'GERMAN SHEPHERD'},
    'czech_wolfdog': {'height': 0.82, 'label': 'CZECH WOLFDog'.upper()},
    'tibetan_mastiff': {'height': 0.94, 'label': 'TIBETAN MASTIFF'},
}


def bounds(objects):
    points = [o.matrix_world @ Vector(corner) for o in objects for corner in o.bound_box]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    return low, high


def area_light(name, location, energy, color, size, target):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.color = color
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


report = {}
for name, spec in SPECS.items():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    path = PETS / f'{name}.glb'
    raw_path = RAW / f'{name}_raw.glb'
    if not raw_path.exists():
        shutil.copy2(path, raw_path)
        source = raw_path
    else:
        # Re-running this script always starts from the untouched Tripo result.
        source = raw_path
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f'No mesh in {source}')
    bpy.context.view_layer.update()
    low, high = bounds(meshes)
    size = high - low
    scale = spec['height'] / size.z
    centre = (low + high) * 0.5
    root = bpy.data.objects.new(f'{name}_root', None)
    bpy.context.collection.objects.link(root)
    for obj in list(bpy.context.scene.objects):
        if obj != root and obj.parent is None:
            obj.parent = root
    root.scale = (scale, scale, scale)
    root.location = (-centre.x * scale, -centre.y * scale, -low.z * scale)
    # Every generated dog faces Blender +X. Turn it towards Godot +Z (the lobby camera).
    root.rotation_euler.z = -math.pi / 2
    bpy.context.view_layer.update()
    triangles = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    report[name] = {
        'source_dimensions': list(size),
        'metres_high': spec['height'],
        'triangles': triangles,
        'mesh_objects': len(meshes),
        'source': str(source),
    }
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_apply=True, export_animations=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / f'{name}.blend'))

    # Neutral product render for geometry and breed inspection; not exported.
    floor_mat = bpy.data.materials.new('Inspection floor')
    floor_mat.diffuse_color = (0.035, 0.045, 0.050, 1)
    floor_mat.use_nodes = True
    bsdf = floor_mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is None:
        bsdf = floor_mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        output = floor_mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        floor_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.035, 0.045, 0.050, 1)
    bsdf.inputs['Roughness'].default_value = 0.8
    bpy.ops.mesh.primitive_plane_add(size=200)
    floor = bpy.context.object
    floor.name = 'Inspection floor - not exported'
    floor.data.materials.append(floor_mat)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.12, 0.16, 0.19, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
    area_light('Key', (2.0, -3.0, 4.0), 550, (1.0, 0.88, 0.73), 3.0, (0, 0, 0.45))
    area_light('Fill', (-3.0, -1.0, 2.0), 350, (0.66, 0.80, 1.0), 2.5, (0, 0, 0.40))
    area_light('Rim', (1.5, 2.5, 3.0), 600, (0.78, 0.88, 1.0), 2.0, (0, 0, 0.45))
    bpy.ops.object.camera_add(location=(1.8, -3.3, 1.55))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, spec['height'] * 0.48)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = max(1.45, spec['height'] * 1.65)
    scene.camera = camera
    scene.render.resolution_x = 760
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(RENDERS / f'{name}.png')
    scene.view_settings.view_transform = 'AgX'
    bpy.ops.render.render(write_still=True)
    print('PET_PREPARED', name, report[name], flush=True)

(ROOT / 'diagnostics' / 'pet-model-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('ALL_PETS_PREPARED', flush=True)
