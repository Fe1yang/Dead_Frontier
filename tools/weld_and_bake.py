"""Weld a fragmented Tripo character into one continuous shell and re-bake its texture.

Welding merges the UV seams too, so the textures have to be re-baked from the original mesh
onto the new UV layout. Without this step the glTF exporter splits the vertices again and the
cracks come back.

Run: blender -b -P weld_and_bake.py -- <glb_in> <glb_out> [size]
"""
import bpy, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SRC, OUT = argv[0], argv[1]
SIZE = int(argv[2]) if len(argv) > 2 else 2048

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Icosphere")]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
high = bpy.context.view_layer.objects.active
high.name = "Source"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# copy for the welded target
low = high.copy()
low.data = high.data.copy()
low.name = "Welded"
bpy.context.collection.objects.link(low)

bpy.ops.object.select_all(action="DESELECT")
low.select_set(True)
bpy.context.view_layer.objects.active = low
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.004)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")
print("WELDED verts", len(low.data.vertices))

# bake the original look onto the new UVs
img = bpy.data.images.new("Baked", SIZE, SIZE, alpha=False)
mat = bpy.data.materials.new("BakedSkin")
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes["Principled BSDF"]
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = img
tex.select = True
nt.nodes.active = tex
low.data.materials.clear()
low.data.materials.append(mat)

# Make every source material emit its own base colour: baking DIFFUSE/COLOR came out blank,
# while EMIT captures exactly the authored texture regardless of lighting.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    nt2 = mat.node_tree
    out = next((n for n in nt2.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        continue
    bsdf2 = next((n for n in nt2.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf2 is None:
        continue
    src_input = bsdf2.inputs["Base Color"]
    emitter = nt2.nodes.new("ShaderNodeEmission")
    if src_input.is_linked:
        nt2.links.new(src_input.links[0].from_socket, emitter.inputs["Color"])
    else:
        emitter.inputs["Color"].default_value = src_input.default_value
    nt2.links.new(emitter.outputs["Emission"], out.inputs["Surface"])

bpy.ops.object.select_all(action="DESELECT")
low.select_set(True)
high.select_set(True)
bpy.context.view_layer.objects.active = low
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.render.bake.use_selected_to_active = True
scene.render.bake.margin = 6
scene.render.bake.use_clear = True
bpy.ops.object.bake(type="EMIT", use_clear=True)
img.pack()
print("BAKED", SIZE)

bpy.data.objects.remove(high, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
low.select_set(True)
bpy.context.view_layer.objects.active = low
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_animations=False, export_apply=False)
print("WROTE", OUT, os.path.getsize(OUT))
