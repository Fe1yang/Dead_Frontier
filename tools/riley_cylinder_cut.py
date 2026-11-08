import bpy, bmesh, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","actors","survivor_riley_universal.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
bm=bmesh.new(); bm.from_mesh(body.data); bm.faces.ensure_lookup_table()
# the strand is not a separate island: it hangs off the head/neck mesh. Delete the faces that
# sit inside a thin cylinder along the visible line (neck -> up-right past the shoulder).
A=Vector((0.04,-0.02,1.40)); B=Vector((0.34,0.02,1.66))
AB=B-A
def seg_dist(p):
    t=max(0.0,min(1.0,(p-A).dot(AB)/AB.length_squared))
    return (p-(A+AB*t)).length
kill=[f for f in bm.faces if seg_dist(f.calc_center_median())<0.012]
print("CYLINDER_FACES", len(kill))
if 0 < len(kill) < 400:
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(body.data); body.data.update()
bm.free()
print("VERTS", len(body.data.vertices))
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=False, export_apply=False)
print("WROTE", os.path.getsize(SRC))