import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BLEND = ROOT / 'assets/blender/pursuer_abomination.blend'
RENDER = ROOT / 'diagnostics/intro/pursuer-rest.png'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
bpy.context.view_layer.update()
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        low = Vector(tuple(min(v[i] for v in points) for i in range(3)))
        high = Vector(tuple(max(v[i] for v in points) for i in range(3)))
        print('MESH_BOUNDS', obj.name, tuple(low), tuple(high), flush=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.world = bpy.data.worlds.new('PursuerPreviewWorld')
scene.world.use_nodes = True
background = next((n for n in scene.world.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground'), None)
if background is None:
    background = scene.world.node_tree.nodes.new('ShaderNodeBackground')
    output = next((n for n in scene.world.node_tree.nodes if n.bl_idname == 'ShaderNodeOutputWorld'), None)
    if output is None:
        output = scene.world.node_tree.nodes.new('ShaderNodeOutputWorld')
    scene.world.node_tree.links.new(background.outputs[0], output.inputs[0])
background.inputs[0].default_value = (.12, .14, .16, 1)
background.inputs[1].default_value = .65
for name, loc, power, size in [('Key', (2, -4, 4), 650, 4), ('Fill', (-3, -2, 2.5), 420, 3), ('Rim', (1, 2, 3.5), 650, 3)]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(2.6, -5.4, 2.45))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, .95)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.35
scene.camera = camera
scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(RENDER)
bpy.ops.render.render(write_still=True)
print('PURSUER_RENDERED', RENDER, flush=True)
