import bpy, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'survivor_riley_universal.glb'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/name))

meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']

for m in meshes:
    me = m.data
    print('=== MESH', m.name)
    # world-space bbox center
    bb = [m.matrix_world @ v.co for v in me.vertices]
    cx = sum(v.x for v in bb)/len(bb); cy = sum(v.y for v in bb)/len(bb); cz = sum(v.z for v in bb)/len(bb)
    print('CENTER %.3f %.3f %.3f' % (cx, cy, cz),
          'SIZE %.3f %.3f %.3f' % (max(v.x for v in bb)-min(v.x for v in bb),
                                   max(v.y for v in bb)-min(v.y for v in bb),
                                   max(v.z for v in bb)-min(v.z for v in bb)))
    if len(me.vertices) > 1000:
        # 1) duplicate positions: same-normal pairs (true overlap) vs different-normal (seam)
        pos_groups = defaultdict(list)
        for v in me.vertices:
            pos_groups[tuple(round(c,4) for c in v.co)].append(v)
        same_n = 0; diff_n = 0
        for vs in pos_groups.values():
            if len(vs) < 2: continue
            n0 = vs[0].normal
            if all((v.normal - n0).length < 0.05 for v in vs[1:]): same_n += len(vs)-1
            else: diff_n += len(vs)-1
        print('DUP_SAME_NORMAL(overlap?)', same_n, 'DUP_DIFF_NORMAL(seam)', diff_n)
        # 2) duplicate faces: same sorted position set
        fset = Counter()
        for p in me.polygons:
            key = tuple(sorted(tuple(round(c,4) for c in me.vertices[i].co) for i in p.vertices))
            fset[key] += 1
        print('DUP_FACES', sum(c-1 for c in fset.values() if c>1))
        # 3) UV mirrored islands: negative UV area polygons
        uv = me.uv_layers[0].data
        neg = 0; tot = 0
        for p in me.polygons:
            pts = [uv[l].uv for l in p.loop_indices]
            area = 0.0
            for i in range(len(pts)):
                x1,y1 = pts[i]; x2,y2 = pts[(i+1)%len(pts)]
                area += x1*y2 - x2*y1
            tot += 1
            if area < 0: neg += 1
        print('UV_NEG_AREA_POLYS(mirrored)', neg, '/', tot)
        # 4) smooth shading + sharp edges
        sm = sum(1 for p in me.polygons if p.use_smooth)
        print('SMOOTH_POLYS', sm, '/', len(me.polygons))
        # 5) custom normal extremes: detect zero/garbage loops
        if me.has_custom_normals:
            bad = sum(1 for l in me.loops if l.normal.length < 0.5)
            print('BAD_CUSTOM_NORMAL_LOOPS', bad)
        # 6) UV bounds
        xs = [d.uv.x for d in uv]; ys = [d.uv.y for d in uv]
        print('UV_RANGE x[%.3f,%.3f] y[%.3f,%.3f]' % (min(xs),max(xs),min(ys),max(ys)))
    else:
        # small mesh: which material, bound to what
        print('MAT_SLOTS', [ms.material.name if ms.material else None for ms in m.material_slots])
        vg = [g.name for g in m.vertex_groups]
        print('VERTEX_GROUPS', vg[:10])
        # hidden?
        print('HIDE', m.hide_render, m.hide_viewport, 'parent', m.parent.name if m.parent else None,
              'parent_type', m.parent_type)
