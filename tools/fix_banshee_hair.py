import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLB = ROOT / 'assets' / 'models' / 'actors' / 'zombie_banshee_universal.glb'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))

# 1) Remove the hood: both scalp shells (ash black + ash grey duplicates).
# 2) Remove the duplicated dark strand layer (keeps the silver/white-streaks one).
# 3) Remove the stray icosphere if it is a renderable leftover with no material.
KILL = {'Banshee_HD_Hair_Scalp', 'Banshee_HD_Hair_Scalp.001', 'Banshee_HD_Stringy_Grey_Hair'}
removed = []
for ob in list(bpy.data.objects):
    if ob.type == 'MESH' and (ob.name in KILL or (ob.name.startswith('Icosphere') and not ob.data.materials)):
        removed.append(ob.name)
        bpy.data.objects.remove(ob, do_unlink=True)
print('removed:', removed)

bpy.ops.export_scene.gltf(
    filepath=str(GLB),
    export_format='GLB',
    export_animations=True,
    export_skins=True,
    export_apply=False,
)
print('exported', GLB)
