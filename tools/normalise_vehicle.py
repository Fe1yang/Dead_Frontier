"""Normalise a vehicle GLB so its nose faces -Z in glTF (Blender +Y) space.

The nose end is found by geometry, not by guessing: sample every vertex, split the model's
long axis into 10 bins and compare the tallest point in the first/last bin. The cabin/roof
is tall and sits at the back, so the end whose bin has the lower roof is the nose.

Run: blender -b -P normalise_vehicle.py -- <in.glb> <out.glb>
"""
import bpy, os, sys, math
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.context.view_layer.update()

lo = Vector((1e9, 1e9, 1e9))
hi = Vector((-1e9, -1e9, -1e9))
for m in meshes:
    for c in m.bound_box:
        q = m.matrix_world @ Vector(c)
        lo = Vector((min(lo.x, q.x), min(lo.y, q.y), min(lo.z, q.z)))
        hi = Vector((max(hi.x, q.x), max(hi.y, q.y), max(hi.z, q.z)))
size = hi - lo
print("SIZE", tuple(round(v, 2) for v in size))

# long axis: X or Y (Blender is Z-up here)
axis = 0 if size.x >= size.y else 1
n = 10
tops = [lo.z] * n
for m in meshes:
    mw = m.matrix_world
    for v in m.data.vertices:
        p = mw @ v.co
        t = (p[axis] - lo[axis]) / max(size[axis], 1e-6)
        b = min(n - 1, max(0, int(t * n)))
        tops[b] = max(tops[b], p.z)

first = max(tops[0], tops[1])
last = max(tops[n - 1], tops[n - 2])
print("TOPS", [round(t, 2) for t in tops])
# the nose is the low end
nose_at_max = first > last
print("NOSE_AT", "max" if nose_at_max else "min", "first", round(first, 2), "last", round(last, 2))

# rotate so the nose points at Blender +Y (which the exporter maps to glTF -Z)
if axis == 1:
    rot = Matrix.Identity(4) if nose_at_max else Matrix.Rotation(math.radians(180), 4, "Z")
else:
    # long axis on X: turn it onto Y first, nose to +Y
    rot = Matrix.Rotation(math.radians(90), 4, "Z") if not nose_at_max else Matrix.Rotation(math.radians(-90), 4, "Z")
bpy.ops.object.select_all(action="SELECT")
for m in meshes:
    m.matrix_world = rot @ m.matrix_world
bpy.context.view_layer.update()

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_apply=True, export_yup=True)
print("EXPORTED", OUT, os.path.getsize(OUT))
