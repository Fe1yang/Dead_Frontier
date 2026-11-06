import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/blender/pets/doberman.blend'))
for o in bpy.context.scene.objects:
    print('OBJ',o.name,o.type,'loc',tuple(o.location),'scale',tuple(o.scale),'parent',o.parent.name if o.parent else None)
    if o.type=='MESH':
        counts=[sum(g.weight for g in v.groups) for v in o.data.vertices]
        print('WEIGHTS',len(counts),min(counts),max(counts),sum(c>0 for c in counts))
        print('BASE_BOUNDS',tuple(min(v.co[i] for v in o.data.vertices) for i in range(3)),tuple(max(v.co[i] for v in o.data.vertices) for i in range(3)))
        print('GROUPS',[(g.index,g.name) for g in o.vertex_groups])
    if o.type=='ARMATURE':
        print('BONES',[(b.name,tuple(b.head_local),tuple(b.tail_local)) for b in o.data.bones])
        dg=bpy.context.evaluated_depsgraph_get()
        ev=o.evaluated_get(dg)
        mesh=ev.to_mesh()
        pts=[ev.matrix_world@v.co for v in mesh.vertices]
        print('EVAL_BOUNDS',tuple(min(p[i] for p in pts) for i in range(3)),tuple(max(p[i] for p in pts) for i in range(3)))
        ev.to_mesh_clear()
