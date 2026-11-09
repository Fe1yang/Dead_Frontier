"""Remove the lion mesh that leaked into the white tiger during the idle bake."""
import bpy, os, sys

ARGS = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = ARGS[0], ARGS[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

removed = []
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and "lion" in o.name.lower():
        removed.append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)

# meshes parented to nothing but named like the lion armature are gone already
print("REMOVED_LION_MESHES", removed)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_apply=False,
)
print("EXPORTED", OUT, os.path.getsize(OUT))
