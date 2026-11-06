import bpy
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
path = Path(args[0]) if args else root / 'assets' / 'animations' / 'universal' / 'Universal Animation Library[Standard]' / 'Unreal-Godot' / 'UAL1_Standard.glb'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(path))
report = {'objects': [], 'actions': [], 'bones': []}
for obj in bpy.context.scene.objects:
    report['objects'].append({'name': obj.name, 'type': obj.type, 'dimensions': list(obj.dimensions)})
    if obj.type == 'ARMATURE':
        for bone in obj.data.bones:
            report['bones'].append({'name': bone.name, 'head': list(bone.head_local), 'tail': list(bone.tail_local), 'parent': bone.parent.name if bone.parent else None})
for action in bpy.data.actions:
    report['actions'].append({'name': action.name, 'frame_range': list(action.frame_range)})
out = root / 'diagnostics' / ('animation_library2.json' if args else 'animation_library.json')
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('OBJECTS', report['objects'])
print('BONES', [b['name'] for b in report['bones']])
print('ACTIONS', [a['name'] for a in report['actions']])
print('REPORT', out)
