import bpy, sys, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'survivor_riley_universal.glb'
out = sys.argv[sys.argv.index('--')+2] if len(sys.argv) > sys.argv.index('--')+2 else 'diag'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/name))

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 720
scene.render.resolution_y = 720
scene.render.filepath = str(ROOT/'diagnostics'/'render-diag'/('blender-'+out+'.png'))

# neutral world
world = bpy.data.worlds.new('W'); scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.12, 0.15, 0.17, 1.0)
bg.inputs[1].default_value = 0.6

# sun like game key light
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun','SUN'))
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(32), 0, math.radians(-28))
sun.data.energy = 2.0

# find head: use armature Head bone world position
arm = next(o for o in scene.objects if o.type=='ARMATURE')
hb = arm.data.bones.get('Head') or arm.data.bones.get('head')
head_world = arm.matrix_world @ hb.head_local
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.lens = 60
cam.location = head_world + Vector((0.10, -0.85, 0.02))  # blender: character faces -Y after gltf import
direction = (head_world + Vector((0,0,0.015))) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()

bpy.ops.render.render(write_still=True)
print('BLENDER_RENDER_DONE', scene.render.filepath)
