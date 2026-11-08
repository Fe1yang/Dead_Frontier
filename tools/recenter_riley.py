"""Recentre the retargeted Riley GLB: the export kept a ~200 m offset from the Tripo source,
which parked the model off-camera in the lobby. Move everything so the feet sit on y=0 and
the body is centred on x/z, then re-export.

Run: blender -b -P recenter_riley.py
"""
import bpy, os
from mathutils import Vector

WORK = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors"
SRC = os.path.join(WORK, "survivor_riley_universal.glb")
OUT = os.path.join(WORK, "survivor_riley_universal.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
bpy.context.view_layer.update()

print("OBJECTS")
for o in bpy.context.scene.objects:
    print("  ", o.name, o.type, tuple(round(v, 2) for v in o.location))

def world_bbox():
    lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi

lo, hi = world_bbox()
print("BBOX", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))
offset = Vector(((lo.x + hi.x) * -0.5, -lo.z, (lo.y + hi.y) * -0.5))
print("OFFSET", tuple(round(v, 3) for v in offset))

roots = [o for o in bpy.context.scene.objects if o.parent is None]
for o in roots:
    o.location += offset
bpy.context.view_layer.update()

lo, hi = world_bbox()
print("BBOX_AFTER", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=True,
    export_apply=False,
)
print("RECENTERED", OUT)
