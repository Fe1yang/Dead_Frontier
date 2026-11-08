"""Consistent character portraits: front-facing, identical framing for every survivor.

For each actor GLB:
  1. render 4 angles at low res and pick the most symmetrical silhouette as the FRONT view
     (a face is left-right symmetric; a profile is not),
  2. render that view at 1024 with a fixed orthographic height,
  3. crop a fixed window around the head bone -> 512x512, so every card has the same head
     size and the same crop.

Run: blender -b -P portrait_uniform.py
"""
import bpy, os, math, sys
from mathutils import Vector

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
ACTORS = [
    ("male", "survivor_male_universal.glb"),
    ("riley", "survivor_riley_universal.glb"),
    ("medic", "survivor_medic_universal.glb"),
    ("maya", "survivor_maya_universal.glb"),
    ("jian", "survivor_jian_scout_universal.glb"),
]
OUTDIR = os.path.join(ROOT, "tools", "portraits_raw")
os.makedirs(OUTDIR, exist_ok=True)

ORTHO = 0.92          # metres of vertical coverage
CROP = 0.60           # metres of the frame kept, centred on the head
DROP = 0.14           # how far below the head centre the crop is centred


def setup_scene():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.exposure = -0.45
    try:
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    if sc.world is None:
        sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.5, 0.56, 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.75
    for name, loc, energy, size in (("key", (1.6, -1.9, 2.3), 420, 3.0),
                                    ("fill", (-1.9, -1.2, 1.5), 130, 3.5),
                                    ("rim", (-0.5, 2.2, 2.1), 240, 2.5)):
        L = bpy.data.objects.new(name, bpy.data.lights.new(name, type="AREA"))
        L.data.energy = energy
        L.data.size = size
        L.location = loc
        L.rotation_euler = (Vector((0, 0, 1.4)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(L)
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc, cam


def head_position(arm):
    for name in ("head", "head_01", "Head"):
        if name in arm.data.bones:
            return arm.matrix_world @ arm.data.bones[name].head_local
    return Vector((0, 0, 1.55))


def aim(cam, target, angle_deg, ortho):
    r = math.radians(angle_deg)
    pos = target + Vector((math.sin(r) * 3.0, math.cos(r) * -3.0, 0.05))
    cam.location = pos
    cam.data.ortho_scale = ortho
    cam.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()


def main():
    for key, fname in ACTORS:
        path = os.path.join(ROOT, "assets", "models", "actors", fname)
        if not os.path.exists(path):
            print("MISSING", fname)
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=path)
        arm = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
        if arm.animation_data:
            arm.animation_data.action = None
        bpy.context.scene.frame_set(0)
        bpy.context.view_layer.update()
        sc, cam = setup_scene()
        hp = head_position(arm)
        target = Vector((hp.x, hp.y, hp.z))

        # --- pick the front angle by silhouette symmetry
        sc.render.resolution_x = 200
        sc.render.resolution_y = 200
        aim(cam, target, 0, 0.95)
        scores = {}
        for ang in (0, 90, 180, 270):
            aim(cam, target, ang, 0.95)
            p = os.path.join(OUTDIR, "probe_%s_%d.png" % (key, ang))
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            scores[ang] = p
        print("PROBES", key, list(scores.values()))

        # --- final render of the chosen angle (front is stored by the caller)
        sc.render.resolution_x = 1024
        sc.render.resolution_y = 1024
        for ang in (0, 180):
            aim(cam, target, ang, ORTHO)
            sc.render.filepath = os.path.join(OUTDIR, "full_%s_%d.png" % (key, ang))
            bpy.ops.render.render(write_still=True)
        print("FULL", key, "head", tuple(round(v, 3) for v in hp))


main()
