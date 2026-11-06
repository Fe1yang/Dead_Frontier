import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
report={}
for key in ('male','female'):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    path=ROOT/'assets'/'models'/'actors'/f'survivor_{key}_universal.glb'
    bpy.ops.import_scene.gltf(filepath=str(path))
    mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    info={'images':[], 'hands':{}, 'vertices':len(mesh.data.vertices)}
    for image in bpy.data.images:
        if image.type=='IMAGE' and image.size[0]>0:
            info['images'].append({'name':image.name,'size':list(image.size)})
    for side in ('l','r'):
        wrist=rig.data.bones['hand_'+side].head_local
        groups={}
        for group in mesh.vertex_groups:
            if group.name.endswith('_'+side) and (group.name=='hand_'+side or group.name.startswith(('thumb_','index_','middle_','ring_','pinky_'))):
                count=0; total=0.0
                for v in mesh.data.vertices:
                    for g in v.groups:
                        if g.group==group.index:
                            count+=1; total+=g.weight
                groups[group.name]={'vertices':count,'weight':round(total,3)}
        info['hands'][side]={'wrist':list(wrist),'groups':groups,'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones if b.name.endswith('_'+side) and b.name.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_'))}}
    report[key]=info
(ROOT/'diagnostics'/'survivor-quality.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SURVIVOR_QUALITY_INSPECTED')
