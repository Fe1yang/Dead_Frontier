"""The chaser's flank is skinned to the ARMS, not the legs: upperarm/clavicle/lowerarm carry it,
so the side of the chest swings whenever the arms move. Move that influence to the spine, keeping
the real shoulder and arm geometry driven by the arms.
"""
import bpy

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\pursuer_abomination.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

mesh_obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
groups = {g.index: g.name for g in mesh_obj.vertex_groups}

co = [mesh_obj.matrix_world @ v.co for v in mesh_obj.data.vertices]
min_z = min(p.z for p in co)
max_z = max(p.z for p in co)
H = max_z - min_z
print("HEIGHT", round(H, 3), "min_z", round(min_z, 3))

# torso band: from just above the hips to just under the shoulders
band_lo = min_z + 0.42 * H
band_hi = min_z + 0.72 * H
half_w = 0.20 * H

arm_keys = ("upperarm", "lowerarm", "clavicle", "hand", "shoulder")

moved = 0
for v, p in zip(mesh_obj.data.vertices, co):
    if p.z < band_lo or p.z > band_hi:
        continue
    if abs(p.x - (min(x.x for x in co) + max(x.x for x in co)) * 0.5) > half_w:
        continue
    arm_total = 0.0
    for g in v.groups:
        name = groups.get(g.group, "")
        if any(k in name for k in arm_keys):
            arm_total += g.weight
    if arm_total <= 0.05:
        continue
    for g in v.groups:
        name = groups.get(g.group, "")
        if any(k in name for k in arm_keys):
            g.weight = 0.0
    target = "spine_02" if "spine_02" in groups.values() else groups[list(groups)[0]]
    mesh_obj.vertex_groups[target].add([v.index], arm_total, "ADD")
    moved += 1

print("REWEIGHTED", moved)

bpy.context.view_layer.objects.active = mesh_obj
mesh_obj.select_set(True)
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True, export_animations=True, export_apply=False)
print("EXPORTED")
