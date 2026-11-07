import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'diagnostics' / 'retarget_jian.blend'))
sc = bpy.context.scene
t = bpy.data.objects['HighDetailCharacter']
# weight sums
sums = []
for v in t.data.vertices:
    sums.append(sum(g.weight for g in v.groups))
low = [s for s in sums if s < 0.9]
print('WEIGHT_SUMS n', len(sums), 'below_0.9', len(low), 'min', round(min(sums), 3), 'mean', round(sum(sums)/len(sums), 3))
# clear animation -> true rest
rig = bpy.data.objects['UniversalRig']
rig.animation_data.action = None
sc.frame_set(1)
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
te = t.evaluated_get(deps)
me = te.to_mesh()
ds = [(t.data.vertices[i].co - me.vertices[i].co).length for i in range(0, len(t.data.vertices), 53)]
print('REST_EVAL_DELTA max', round(max(ds), 4), 'median', round(sorted(ds)[len(ds)//2], 4))
te.to_mesh_clear()
# render true rest
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
out = ROOT/'diagnostics/pose/true_rest_jian.png'
sc.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('TRUE_REST_RENDERED', out)
