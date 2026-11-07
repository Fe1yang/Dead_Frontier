import sys, os
sys.path.insert(0, r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\tools")
import bpy
import cabin_prims as P

bpy.ops.wm.read_factory_settings(use_empty=True)
M = P.build_materials()
g = P.Group("Probe", M["wall"])
P.box(g, (0, 0, 0), (2, 1, 0.2), bevel=0.02, seg=2, tile=1.0, grain="X")
P.cylinder(g, (2.5, 0, 0), 0.3, 1.0, segments=24, tile=0.5, rot=(0, 0.4, 0))
P.lathe(g, [(0.0, 0.0), (0.3, 0.0), (0.32, 0.2), (0.12, 0.4), (0.1, 0.6), (0.11, 0.62)], center=(-2.5, 0, 0), segments=20)
P.tube(g, [(-1, 0, 1), (0, 0, 1.5), (1, 0, 1.2)], 0.03, sides=6)
P.torus(g, (0, 2, 0), 0.4, 0.05, major_seg=20, minor_seg=8)
P.sphere(g, (0, -2, 0.5), (0.3, 0.2, 0.4), subdiv=2)
P.extrude_xz(g, [(-0.5, 0), (0.5, 0), (0.35, 0.3), (-0.2, 0.5)], y=2, depth=0.1, bevel=0.01)
P.cloth(g, (-1, -1, 1), (2, 0, 0), (0, 0, -1), (0, 1, 0), 20, 20, 0.01,
        lambda u, v: 0.03 * __import__("math").sin(u * 12.0) * (0.3 + 0.7 * v))
ob = g.finish()
print("PROBE_OBJ", ob.name, len(ob.data.vertices), len(ob.data.polygons))
for o in bpy.context.scene.objects:
    o.select_set(o.type == "MESH")
bpy.ops.export_scene.gltf(filepath=os.path.join(P.ROOT, "tools", "cabin_probe.glb"),
                          export_format="GLB", use_selection=True, export_apply=True,
                          export_yup=True, export_cameras=False, export_lights=False)
print("PROBE_EXPORT_OK")
