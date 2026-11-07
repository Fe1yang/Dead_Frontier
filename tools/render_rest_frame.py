import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
model = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/actors'/model))
sc = bpy.context.scene
# stay at rest pose: no action assigned
cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector((2.2, -3.2, 1.4))
d = Vector((0,0,0.95)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
cam_data.clip_start = 0.1
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN'))
sc.collection.objects.link(sun); sun.rotation_euler=(math.radians(50),0,math.radians(30))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs[0].default_value=(0.9,0.9,0.9,1)
sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='STUDIO'
sc.render.resolution_x=420; sc.render.resolution_y=560
out = ROOT/'diagnostics/pose'/('rest_'+model.replace('.glb','.png'))
sc.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('REST_RENDERED', out)
