import bpy, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
for name in argv:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/name))
    rig = next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    bones = [b.name for b in rig.data.bones]
    print('GLB', name, 'bones', len(bones))
    print('NAMES', ','.join(bones))
    mesh = next((o for o in bpy.context.scene.objects if o.type=='MESH'), None)
    if mesh:
        print('MESH', mesh.name, 'verts', len(mesh.data.vertices), 'groups', len(mesh.vertex_groups))
        import mathutils
        low = min((mesh.matrix_world @ v.co).z for v in mesh.data.vertices)
        high = max((mesh.matrix_world @ v.co).z for v in mesh.data.vertices)
        print('HEIGHT', round(high-low,3))
