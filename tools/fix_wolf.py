import bpy, os, sys
from mathutils import Vector
SRC=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\pets\czech_wolfdog.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
# strip the armature: the new wolf has no clips, so a static mesh is what the pet needs
for o in list(bpy.context.scene.objects):
    if o.type == "ARMATURE":
        bpy.data.objects.remove(o, do_unlink=True)
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1:
    bpy.ops.object.join()
body=bpy.context.view_layer.objects.active
body.parent=None
for m in list(body.modifiers):
    body.modifiers.remove(m)
body.rotation_euler=(0,0,0)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
sx=max(v.x for v in box)-min(v.x for v in box)
sy=max(v.y for v in box)-min(v.y for v in box)
sz=max(v.z for v in box)-min(v.z for v in box)
print("RAW size", round(sx,2), round(sy,2), round(sz,2))
# a wolf is ~1.22 m nose to tail and ~0.85 m tall: scale by the LONGEST horizontal axis
longest=max(sx,sy,sz)
scale=1.22/longest
body.scale=body.scale*scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
mz=min(v.z for v in box)
body.location.z-=mz
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
box=[body.matrix_world @ Vector(c) for c in body.bound_box]
print("FINAL size", round(max(v.x for v in box)-min(v.x for v in box),2),
      round(max(v.y for v in box)-min(v.y for v in box),2),
      round(max(v.z for v in box)-min(v.z for v in box),2))
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True, export_animations=False, export_apply=False)
print("WOLF_WRITTEN", os.path.getsize(SRC))
