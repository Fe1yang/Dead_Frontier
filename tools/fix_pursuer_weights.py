"""Stop the chaser's flank and upper body from riding the leg bones.

The pursuer is one skinned mesh on the 65-bone UAL rig. Its flank/belly vertices carry weight from
the thigh bones, so the side of the torso swings whenever a leg lifts. Any torso vertex whose hips
bone sits above the thigh root gets its thigh weights handed back to the spine/pelvis.

Run: blender -b -P fix_pursuer_weights.py
"""
import bpy
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC = os.path.join(ROOT, "assets", "models", "actors", "pursuer_abomination.glb")
OUT = SRC

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

mesh_obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]

LEG_HINTS = ("thigh", "upleg", "upperleg", "leg_l", "leg_r", "calf", "shin", "knee", "foot", "toe")
SPINE_HINTS = ("spine", "pelvis", "hips", "torso", "chest", "abdomen")

leg = [g.name for g in mesh_obj.vertex_groups if any(k in g.name.lower() for k in LEG_HINTS)]
spine = [g.name for g in mesh_obj.vertex_groups if any(k in g.name.lower() for k in SPINE_HINTS)]
print("LEG_GROUPS", leg)
print("SPINE_GROUPS", spine)

hips = arm.data.bones.find("Hips")
hip_z = (arm.matrix_world @ arm.data.bones[hips].head_local).z if hips >= 0 else 0.9
print("HIP_Z", round(hip_z, 3))

gidx = {g.name: g.index for g in mesh_obj.vertex_groups}
leg_idx = {gidx[n] for n in leg if n in gidx}
spine_name = next((n for n in spine if "spine" in n.lower()), spine[0] if spine else None)
if spine_name is None:
    print("NO_SPINE_GROUP")
    raise SystemExit(1)
spine_group = mesh_obj.vertex_groups[spine_name]

# Everything above the hip line that still carries leg weight is torso: give it back to the spine.
cut = hip_z + 0.02
moved = 0
for v in mesh_obj.data.vertices:
    world_z = (mesh_obj.matrix_world @ v.co).z
    if world_z <= cut:
        continue
    total = sum(g.weight for g in v.groups if g.group in leg_idx)
    if total <= 0.01:
        continue
    for g in v.groups:
        if g.group in leg_idx:
            g.weight = 0.0
    spine_group.add([v.index], total, "ADD")
    moved += 1

print("REWEIGHTED", moved, "of", len(mesh_obj.data.vertices), "vertices")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=True, export_apply=False)
print("EXPORTED", OUT, os.path.getsize(OUT))
