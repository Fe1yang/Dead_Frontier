import bpy, os
from mathutils import Vector
NEW=r"C:\Users\user\Downloads\tactical female character 3d model (1).glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=NEW)
bpy.context.view_layer.update()
# flatten the empty hierarchy and bake transforms so bones and mesh share world space
for o in bpy.context.scene.objects:
    if o.type=="MESH" and o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
for o in bpy.context.scene.objects:
    if o.type=="EMPTY":
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.view_layer.update()
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
print("ARM", arm.name, "world", tuple(round(v,3) for v in arm.matrix_world.translation), tuple(round(v,3) for v in arm.matrix_world.to_scale()))
for n in ("pelvis","head","hand_l","hand_r","thigh_l","foot_l"):
    if n in arm.data.bones:
        b=arm.data.bones[n]
        print("BONE %-9s head=(%.3f,%.3f,%.3f) tail=(%.3f,%.3f,%.3f)" % (n,*b.head_local,*b.tail_local))
b=[body.matrix_world @ Vector(c) for c in body.bound_box]
lo=Vector((min(p.x for p in b),min(p.y for p in b),min(p.z for p in b)))
hi=Vector((max(p.x for p in b),max(p.y for p in b),max(p.z for p in b)))
print("MESH_BOX", tuple(round(v,3) for v in lo), tuple(round(v,3) for v in hi))
print("VGROUPS", len(body.vertex_groups))