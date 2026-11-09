"""Bake a district's buildings into ONE atlas, but leave the road surface alone.

The districts are ~42 meshes with 46 materials, so each costs 46 draw calls. Baking everything into a
single atlas killed the tiled asphalt/pavement detail, which made the ground look flat. So the ground
meshes keep their own tiling materials and only the buildings are atlased: ~5 draw calls per district.

Run per district:
  blender -b -P atlas_district.py -- <in.glb> <out.glb> [size]
"""
import bpy, os, sys, time

args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = args[0], args[1]
SIZE = int(args[2]) if len(args) > 2 else 2048
t0 = time.time()

GROUND_HINTS = ("asphalt", "pavement", "curb", "paint", "soil", "tree pit")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not meshes:
    print("NO_MESHES", SRC)
    raise SystemExit(1)

ground = [o for o in meshes if any(h in o.name.lower() for h in GROUND_HINTS)]
rest = [o for o in meshes if o not in ground]

bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# join only the building side
bpy.ops.object.select_all(action="DESELECT")
for o in rest:
    o.select_set(True)
bpy.context.view_layer.objects.active = rest[0]
if len(rest) > 1:
    bpy.ops.object.join()
body = bpy.context.view_layer.objects.active
src_mats = len(body.data.materials)

bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.003)
bpy.ops.object.mode_set(mode="OBJECT")

atlas = bpy.data.images.new("district_atlas", SIZE, SIZE, alpha=False)
for m in body.data.materials:
    if m is None or not m.use_nodes:
        continue
    node = m.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = atlas
    m.node_tree.nodes.active = node

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 1
sc.render.bake.use_pass_direct = False
sc.render.bake.use_pass_indirect = False
sc.render.bake.use_pass_color = True
sc.render.bake.margin = 6

bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.bake(type="DIFFUSE")

atlas.filepath_raw = os.path.splitext(OUT)[0] + "_atlas.png"
atlas.file_format = "PNG"
atlas.save()
atlas.pack()

mat = bpy.data.materials.new("district_atlas")
mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = atlas
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
body.data.materials.clear()
body.data.materials.append(mat)
for poly in body.data.polygons:
    poly.material_index = 0
if body.data.uv_layers:
    body.data.uv_layers.active_index = 0

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=False,
    export_apply=False,
)
print("ATLAS_OK", os.path.basename(OUT), "mats", src_mats, "-> 1", "ground kept", len(ground),
      "faces", len(body.data.polygons), "bytes", os.path.getsize(OUT), "seconds", round(time.time() - t0, 1))
