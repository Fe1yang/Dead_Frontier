import bpy, sys, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
blend = argv[0]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'diagnostics' / blend))
sc = bpy.context.scene
target = bpy.data.objects['HighDetailCharacter']
rig = bpy.data.objects['UniversalRig']
# report raw (pre-armature) bounds and a few landmark verts
arm_mod = next(m for m in target.modifiers if m.type == 'ARMATURE')
arm_mod.show_viewport = False
bpy.context.view_layer.update()
bb = [target.matrix_world @ Vector(c) for c in target.bound_box]
zs = [v.co.z for v in target.data.vertices]
xs = [v.co.x for v in target.data.vertices]
print('RAW_MESH verts', len(target.data.vertices), 'z_range', round(min(zs),3), round(max(zs),3), 'x_range', round(min(xs),3), round(max(xs),3))
# group weight sanity: dominant group histogram
from collections import Counter
dom = Counter()
for v in target.data.vertices:
    if v.groups:
        g = max(v.groups, key=lambda g: g.weight)
        dom[target.vertex_groups[g.group].name] += 1
print('DOMINANT_GROUPS', dom.most_common(12))
# render raw mesh
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
out = ROOT/'diagnostics/pose/raw_mesh_jian.png'
sc.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('RAW_RENDERED', out)
