import bpy, sys, bmesh
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'survivor_riley_universal.glb'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/name))

meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
print('MESH_COUNT', len(meshes))
for m in meshes:
    print('MESH', m.name, 'verts', len(m.data.vertices), 'polys', len(m.data.polygons),
          'uv_layers', len(m.data.uv_layers), 'has_custom_normals', m.data.has_custom_normals)

# duplicate/overlapping surface check: hash rounded vertex positions
for m in meshes:
    seen = Counter()
    for v in m.data.vertices:
        key = tuple(round(c, 4) for c in v.co)
        seen[key] += 1
    dups = sum(c-1 for c in seen.values() if c > 1)
    print('DUP_VERTS', m.name, dups)

# materials and textures
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    nodes = [(n.type, getattr(n.image, 'name', None) if n.type=='TEX_IMAGE' else '') for n in mat.node_tree.nodes]
    print('MATERIAL', mat.name, nodes)
    for n in mat.node_tree.nodes:
        if n.type == 'NORMAL_MAP':
            print('NORMALMAP_STRENGTH', n.inputs['Strength'].default_value, 'space', n.space)

# vertex influences > 4
m = meshes[0]
over4 = sum(1 for v in m.data.vertices if len(v.groups) > 4)
print('VERTS_OVER_4_INFLUENCES', over4, '/', len(m.data.vertices))

# normals sanity: count NaN or zero-length custom normals
m.data.calc_normals()
bad = 0
for p in m.data.polygons:
    if p.normal.length < 0.5: bad += 1
print('DEGENERATE_POLYS', bad)
