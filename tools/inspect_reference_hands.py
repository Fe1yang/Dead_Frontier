import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'assets' / 'animations' / 'universal' / 'Universal Animation Library[Standard]' / 'Unreal-Godot' / 'UAL1_Standard.glb'
OUT = ROOT / 'diagnostics'
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(LIBRARY))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
rig.animation_data_create()
action = bpy.data.actions['Pistol_Aim_Neutral']
rig.animation_data.action = action
if action.slots:
    rig.animation_data.action_slot = action.slots[0]
bpy.context.scene.frame_set(int(action.frame_range[1]))
bpy.context.view_layer.update()
left = rig.matrix_world @ rig.pose.bones['hand_l'].head
right = rig.matrix_world @ rig.pose.bones['hand_r'].head
center = (left + right) * 0.5
print('REFERENCE_HANDS', tuple(left), tuple(right), 'distance', (left-right).length)
for name in ['hand_l','hand_r','index_01_r','index_02_r','index_03_r','middle_01_r','middle_02_r','middle_03_r','thumb_01_r','thumb_02_r','thumb_03_r']:
    pb = rig.pose.bones[name]
    print('REFERENCE_BONE', name, 'head', tuple(rig.matrix_world @ pb.head), 'tail', tuple(rig.matrix_world @ pb.tail), 'length', pb.length)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 700
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.world.color = (0.16,0.16,0.16)
scene.view_settings.view_transform = 'AgX'
for location, energy, size in [((2,-3,4),450,3),((-3,-1,2),220,3)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (center-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add()
camera = bpy.context.object
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 0.66
views = {
    'front': Vector((0,-1.0,0.12)),
    'side': Vector((1.0,-0.08,0.10)),
    'back': Vector((0,1.0,0.12)),
    'top': Vector((0,-0.12,1.0)),
}
for name, offset in views.items():
    camera.location = center + offset
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(OUT / ('reference_hands_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('REFERENCE_RENDERED', name)
