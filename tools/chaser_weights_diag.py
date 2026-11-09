"""Diagnose and repair the chaser's flank weights.

Prints the dominant bones of the flank vertices, then removes every leg influence from anything
above the hip line and renormalises what is left (adding chest weight when a vertex had none).
"""
import bpy

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\pursuer_abomination.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

mesh_obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
groups = {g.index: g.name for g in mesh_obj.vertex_groups}

hips = arm.data.bones.find("Hips")
hip_z = (arm.matrix_world @ arm.data.bones[hips].head_local).z if hips >= 0 else 0.9
print("HIP_Z", round(hip_z, 3))

leg = {"thigh_l", "thigh_r", "calf_l", "calf_r"}
flank = []
for v in mesh_obj.data.vertices:
    wz = (mesh_obj.matrix_world @ v.co).z
    if wz <= hip_z + 0.05:
        continue
    if abs(v.co.x) < 0.30:
        continue
    if v.groups:
        flank.append(v)

print("FLANK_VERTS", len(flank))
tally = {}
for v in flank:
    for g in sorted(v.groups, key=lambda g: -g.weight)[:2]:
        n = groups.get(g.group, "?")
        tally[n] = tally.get(n, 0) + 1
for n, c in sorted(tally.items(), key=lambda kv: -kv[1])[:10]:
    print("   ", n, c)

spine_like = [n for n in groups.values() if any(k in n.lower() for k in ("spine", "chest", "pelvis"))]
target_name = next((n for n in spine_like if "chest" in n.lower()), spine_like[0] if spine_like else None)
print("TARGET", target_name)

fixed = 0
for v in flank:
    leg_total = sum(g.weight for g in v.groups if groups.get(g.group) in leg)
    if leg_total <= 0.001:
        continue
    keep = sum(g.weight for g in v.groups if groups.get(g.group) not in leg)
    for g in v.groups:
        if groups.get(g.group) in leg:
            g.weight = 0.0
    if keep < 0.05:
        mesh_obj.vertex_groups[target_name].add([v.index], leg_total, "ADD")
    fixed += 1

print("REWEIGHTED", fixed)

# normalise so the skinned sum stays 1.0 (Godot tolerates it, Blender exports cleaner)
bpy.context.view_layer.objects.active = mesh_obj
mesh_obj.select_set(True)
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=SRC, export_format="GLB", use_selection=True, export_animations=True, export_apply=False)
print("EXPORTED")
