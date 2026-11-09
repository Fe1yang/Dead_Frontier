import bpy, os, math
from mathutils import Vector, Matrix
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","vehicles","gold_car.glb")
OUT=os.path.join(ROOT,"assets","models","vehicles","gold_car.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
# measure raw bounds in Blender (Z-up) space
lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
for m in objs:
    for c in m.bound_box:
        q=m.matrix_world @ Vector(c)
        lo=Vector((min(lo.x,q.x),min(lo.y,q.y),min(lo.z,q.z)))
        hi=Vector((max(hi.x,q.x),max(hi.y,q.y),max(hi.z,q.z)))
print("RAW bounds", tuple(round(v,1) for v in (hi-lo)))
# the car is authored lying with its length on Blender Y: stand it up so length is on X
for m in objs:
    bpy.context.view_layer.objects.active=m
    m.select_set(True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
# rotate -90 about Z to put the length on X, then the exporter (Y-up) lays it flat in Godot
rot=Matrix.Rotation(math.radians(90.0),4,"Z")
for m in objs:
    m.matrix_world = rot @ m.matrix_world
bpy.context.view_layer.update()
lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
for m in objs:
    for c in m.bound_box:
        q=m.matrix_world @ Vector(c)
        lo=Vector((min(lo.x,q.x),min(lo.y,q.y),min(lo.z,q.z)))
        hi=Vector((max(hi.x,q.x),max(hi.y,q.y),max(hi.z,q.z)))
print("AFTER bounds", tuple(round(v,1) for v in (hi-lo)))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_apply=True, export_yup=True)
print("EXPORTED", os.path.getsize(OUT))