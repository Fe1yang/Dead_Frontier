import bpy, sys, math
from pathlib import Path
from mathutils import Vector

## Painterly pass: drag Tripo's glossy semi-realistic output toward the cast's hand-painted
## comic look — quantize albedo into flat painterly bands, kill specular shine, then re-export
## the GLB with its animation set intact.
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
target = ROOT / 'assets' / 'models' / 'actors' / argv[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(target))

# 1. Matte materials: no metal, high roughness, low specular.
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Roughness'].default_value = 0.92
            node.inputs['Metallic'].default_value = 0.0
            if 'Specular IOR Level' in node.inputs:
                node.inputs['Specular IOR Level'].default_value = 0.22

# 2. Posterize base-colour textures into painterly bands (via PIL on a temp file).
from PIL import Image, ImageEnhance
tmp = ROOT / 'diagnostics' / '_painterly_tmp.png'
touched = 0
for img in bpy.data.images:
    if img.name.startswith(('Normal', 'ORM')) or 'Normal' in img.name or 'ORM' in img.name:
        continue
    if not img.has_data: continue
    img.filepath_raw = str(tmp); img.file_format = 'PNG'
    img.save()
    im = Image.open(tmp).convert('RGB')
    im = im.filter(Image.Filter.MEDIAN_FILTER) if hasattr(Image, 'Filter') else im
    im = im.quantize(colors=56, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    im = ImageEnhance.Color(im).enhance(0.94)   # a hair less saturated, like the rest of the cast
    im.save(tmp)
    img.filepath_raw = str(tmp)
    img.reload()
    img.pack()
    touched += 1
print('PAINTERLY_TEXTURES', touched)

# 3. Re-export in place, animations included.
bpy.ops.export_scene.gltf(
    filepath=str(target), export_format='GLB',
    export_animations=True, export_animation_mode='ACTIONS',
    export_frame_range=False, export_force_sampling=True, export_apply=False)
print('PAINTERLY_EXPORTED', target)
