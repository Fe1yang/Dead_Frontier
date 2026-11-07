import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
mode = argv[0] if argv else 'skinned'
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'diagnostics' / 'retarget_jian.blend'))
sc = bpy.context.scene
target = bpy.data.objects['HighDetailCharacter']
if mode == 'raw':
    arm_mod = next(m for m in target.modifiers if m.type == 'ARMATURE')
    arm_mod.show_viewport = False
bpy.context.view_layer.update()
cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector((2.2, -3.2, 1.4))
d = Vector((0,0,0.95)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
cam_data.clip_start = 0.1
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN'))
sc.collection.objects.link(sun); sun.rotation_euler=(math.radians(50),0,math.radians(30))
sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='STUDIO'
sc.render.resolution_x=420; sc.render.resolution_y=560
out = ROOT/'diagnostics/pose'/('blend_%s_jian.png' % mode)
sc.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('BLEND_RENDERED', mode, out)
