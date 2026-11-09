"""Delete the merchant from the supply truck model for good.

Merchant_HD is the shopkeeper standing inside the truck; the shop scene had to hide it and the
crate build showed it whenever the whole truck was used. Removing the geometry means nothing can
bring it back.
"""
import bpy
import os

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\supply_truck.glb"
BAK = SRC.replace(".glb", "_withmetchant.glb.bak")

if not os.path.exists(BAK):
    import shutil
    shutil.copyfile(SRC, BAK)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)

removed = 0
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.name.startswith("Merchant"):
        bpy.data.objects.remove(o, do_unlink=True)
        removed += 1

print("REMOVED", removed, "merchant objects")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=SRC,
    export_format="GLB",
    use_selection=True,
    export_animations=False,
    export_apply=False,
)
print("WROTE", SRC, os.path.getsize(SRC))
