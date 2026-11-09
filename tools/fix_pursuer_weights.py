"""Stop the pursuer's torso from following the legs.

Hip and thigh bones were picking up weight from body/arm vertices, so the side muscles slid with
every step. Any vertex clearly above the hips has its leg weights removed and the rest renormalised.

  blender -b -P fix_pursuer_weights.py -- <in.glb> <out.glb>
"""
import bpy, sys, os

args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = args[0], args[1]

LEG_HINTS = ("thigh", "shin", "calf", "leg", "foot", "toe", "knee", "ankle")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
mesh = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = mesh

leg_groups = set()
for g in mesh.vertex_groups:
    if any(h in g.name.lower() for h in LEG_HINTS):
        leg_groups.add(g.index)
print("LEG_GROUPS", len(leg_groups), "of", len(mesh.vertex_groups))

# hips sit at the lowest leg bone head; anything 25% above that must not follow the legs
hip_z = None
for b in arm.data.bones:
    if any(h in b.name.lower() for h in ("thigh", "hip", "pelvis")):
        z = (arm.matrix_world @ b.head_local).z
        hip_z = z if hip_z is None else min(hip_z, z)
if hip_z is None:
    hip_z = min((arm.matrix_world @ b.head_local).z for b in arm.data.bones if any(h in b.name.lower() for h in LEG_HINTS))
cutoff = hip_z + 0.22
print("HIP_Z", round(hip_z, 3), "CUTOFF", round(cutoff, 3))

cleaned = 0
for v in mesh.data.vertices:
    world_z = (mesh.matrix_world @ v.co).z
    if world_z <= cutoff:
        continue
    leg = [g for g in v.groups if g.group in leg_groups and g.weight > 0.0001]
    if not leg:
        continue
    total = sum(g.weight for g in v.groups)
    keep = total - sum(g.weight for g in leg)
    for g in leg:
        mesh.vertex_groups[g.group].remove([v.index])
    if keep > 0.0001:
        for g in v.groups:
            mesh.vertex_groups[g.group].add([v.index], g.weight / keep, "REPLACE")
    cleaned += 1

print("VERTICES_CLEANED", cleaned)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_force_sampling=False,
    export_apply=False,
)
print("EXPORTED", OUT, os.path.getsize(OUT))
