import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'assets'/'blender'/'survivor_female.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
for o in list(bpy.context.scene.objects):
    if o.name.startswith('DetailCheek'): bpy.data.objects.remove(o,do_unlink=True)
nose=bpy.data.objects.get('Nose')
if nose: nose.scale=(0.78,0.82,0.85)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/'models'/'survivor_female.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print('FEMALE_FACE_POLISHED')
