import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/models/generated'/'survivor_jian_hd.glb'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
print('SRC_MESHES', [(o.name, len(o.data.vertices)) for o in meshes])
# join all like pipeline does
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
target = bpy.context.object
target.name = 'Joined'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
target.rotation_mode = 'XYZ'
target.rotation_euler.z = -math.pi / 2
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
before_v = len(target.data.vertices)
# same dedup logic
snapshot = set(bpy.context.scene.objects)
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True)
bpy.context.view_layer.objects.active = target
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
parts = [o for o in bpy.context.scene.objects if o not in snapshot and o.type == 'MESH']
print('PARTS', len(parts)+1)
clusters = []
for o in sorted([target]+parts, key=lambda p: -len(p.data.vertices)):
    c = [o.matrix_world @ Vector(cor) for cor in o.bound_box]
    center = sum(c, Vector())/8.0
    placed = False
    for cl in clusters:
        if (cl['center']-center).length < 0.025:
            cl['objs'].append(o); placed=True; break
    if not placed:
        clusters.append({'center':center,'objs':[o]})
keep = max(clusters, key=lambda cl: sum(len(o.data.vertices) for o in cl['objs']))
print('KEEP_CLUSTER objs', len(keep['objs']), 'verts', sum(len(o.data.vertices) for o in keep['objs']), 'center', tuple(round(v,3) for v in keep['center']))
for cl in clusters:
    if cl is keep: continue
    for o in cl['objs']: bpy.data.objects.remove(o, do_unlink=True)
rest = [o for o in keep['objs'] if o != target]
if rest:
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    for o in rest: o.select_set(True)
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.join()
xs=[v.co.x for v in target.data.vertices]; ys=[v.co.y for v in target.data.vertices]; zs=[v.co.z for v in target.data.vertices]
print('KEPT_BOUNDS x', round(min(xs),3), round(max(xs),3), 'y', round(min(ys),3), round(max(ys),3), 'z', round(min(zs),3), round(max(zs),3))
# render kept mesh
target.name='Keep'
sc = bpy.context.scene
cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector((2.2, -3.2, 1.4))
d = Vector((0,0,0.95)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
cam_data.clip_start = 0.1
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN'))
sc.collection.objects.link(sun); sun.rotation_euler=(math.radians(50),0,math.radians(30))
sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.light='STUDIO'
sc.render.resolution_x=420; sc.render.resolution_y=560
out = ROOT/'diagnostics/pose/dedup_kept_jian.png'
sc.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print('KEPT_RENDERED', out)
