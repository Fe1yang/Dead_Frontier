import bpy, math, os
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
print(f"objects: {[o.name+'('+o.type+')' for o in bpy.context.scene.objects]}")
mesh_obj = None
arm_obj = None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name!="Icosphere":
        mesh_obj=ob
    if ob.type=="ARMATURE":
        arm_obj=ob
print("mesh:", mesh_obj.name if mesh_obj else None)
# Blender coords: X lateral, Y depth (front-back), Z up. Torso z ~0.85-1.55
# Push torso/side vertices outward to undo the old slim + shoulder narrow that caved the armpit.
for v in mesh_obj.data.vertices:
    x,y,z = v.co.x, v.co.y, v.co.z
    # height falloff: full in chest/armpit band, tapering at neck/hips
    if 0.80 <= z <= 1.55 and abs(x) > 0.06:
        # bell falloff centered at z=1.15
        t = max(0.0, 1.0 - abs(z-1.15)/0.38)
        t = t*t*(3-2*t)  # smoothstep
        # lateral expansion: move side of torso outward
        sx = 1.0 + 0.10*t   # +10% width at chest
        sy = 1.0 + 0.12*t   # front/back depth +12% so side view not flat
        v.co.x = x*sx
        # expand Y away from central spine (y~0.02), keep front/back sign
        v.co.y = 0.02 + (y-0.02)*sy
    # armpit dent specifically: vertices in armpit zone pushed slightly further out
    if 1.10 <= z <= 1.45 and 0.10 < abs(x) < 0.30:
        # extra +4% out, stronger near pit
        v.co.x = x*1.04
        v.co.y = 0.02 + (v.co.y-0.02)*1.03
mesh_obj.data.update()
# recalc normals
for p in mesh_obj.data.polygons:
    p.use_smooth=True
print("riley torso bloated")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("exported")
