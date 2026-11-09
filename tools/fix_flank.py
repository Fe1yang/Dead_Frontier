"""Stop the pursuer's flank from riding the legs: cap thigh influence above the hip line.

The original skin has thigh weights bleeding up into the flank/oblique, so the side of the
belly follows every stride. Vertices above the hip joint get the thigh influence capped and
the rest renormalised onto whatever spine/pelvis weight they already carry.

Run: blender -b -P fix_flank.py -- <in.glb> <out.glb>
"""
import bpy, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
body = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
print("bones", len(arm.data.bones), "verts", len(body.data.vertices))

b = arm.data.bones
hip_z = {}
for name in ("thigh_l", "thigh_r"):
    if name in b:
        hip_z[name] = (arm.matrix_world @ b[name].head_local).z
if not hip_z:
    raise SystemExit("no thigh bones")
hip_line = min(hip_z.values())
print("hip line", round(hip_line, 3))

leg_groups = [g for g in body.vertex_groups if g.name in ("thigh_l", "thigh_r", "calf_l", "calf_r")]
torso_groups = [g for g in body.vertex_groups if g.name in
                ("pelvis", "spine_01", "spine_02", "spine_03", "clavicle_l", "clavicle_r")]
print("leg groups", [g.name for g in leg_groups], "torso groups", [g.name for g in torso_groups])

fixed = 0
for v in body.data.vertices:
    wz = (body.matrix_world @ v.co).z
    if wz <= hip_line + 0.12:
        continue                      # below the hip: legs are allowed to drive it
    leg_w = 0.0
    for g in v.groups:
        if body.vertex_groups[g.group].name in ("thigh_l", "thigh_r", "calf_l", "calf_r"):
            leg_w += g.weight
    if leg_w <= 0.02:
        continue
    # keep at most 15% on the legs up here, push the rest to the torso bones it already has
    keep = min(leg_w, 0.15)
    scale = keep / leg_w if leg_w > 0 else 0.0
    torso_total = 0.0
    for g in list(v.groups):
        nm = body.vertex_groups[g.group].name
        if nm in ("thigh_l", "thigh_r", "calf_l", "calf_r"):
            body.vertex_groups[g.group].add([v.index], g.weight * scale, "REPLACE")
        elif nm in ("pelvis", "spine_01", "spine_02", "spine_03", "clavicle_l", "clavicle_r"):
            torso_total += g.weight
    if torso_total < 1e-4 and torso_groups:
        torso_groups[1 if len(torso_groups) > 1 else 0].add([v.index], 1.0 - keep, "REPLACE")
    else:
        add = (leg_w - keep)
        for g in list(v.groups):
            nm = body.vertex_groups[g.group].name
            if nm in ("pelvis", "spine_01", "spine_02", "spine_03"):
                body.vertex_groups[g.group].add([v.index], g.weight + add * (g.weight / torso_total), "REPLACE")
    fixed += 1
print("FLANK_FIXED", fixed)

bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
    if o.type in ("MESH", "ARMATURE"):
        o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=True, export_animation_mode="ACTIONS",
                          export_force_sampling=False, export_apply=False)
print("EXPORTED", OUT, os.path.getsize(OUT))
