import bpy
import math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets'/'models'/'generated'
OUT=ROOT/'assets'/'ui'
ACTORS=[('male','survivor_male_hd.glb',-math.pi/2),('female','survivor_female_hd.glb',-math.pi/2),('medic','survivor_medic_hd.glb',-math.pi/2)]
import sys
_selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if _selected: ACTORS=[a for a in ACTORS if a[0] in _selected]

def area(name,loc,energy,size,color):
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object; o.name=name; o.data.energy=energy; o.data.shape='DISK'; o.data.size=size; o.data.color=color
    o.rotation_euler=(Vector((0,0,1.55))-o.location).to_track_quat('-Z','Y').to_euler()

for key,filename,angle in ACTORS:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(SRC/filename))
    meshes=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1: bpy.ops.object.join()
    obj=bpy.context.object
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    coords=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    low=Vector(tuple(min(v[i] for v in coords) for i in range(3))); high=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    scale=1.86/(high.z-low.z); obj.scale=(scale,)*3; obj.rotation_mode='XYZ'; obj.rotation_euler.z=angle
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    coords=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    low=Vector(tuple(min(v[i] for v in coords) for i in range(3))); high=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    obj.location+=Vector((-(low.x+high.x)/2,-(low.y+high.y)/2,-low.z))
    bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
    # Permanently lower both arms beside the torso for a neutral portrait.
    for v in obj.data.vertices:
        p=v.co.copy()
        if abs(p.x)>0.24 and p.z>1.18:
            sign=-1 if p.x<0 else 1
            shoulder=Vector((sign*0.23,0,1.44))
            rotation=Vector((sign,0,-0.03)).normalized().rotation_difference(Vector((sign*0.12,0,-1)).normalized())
            v.co=shoulder+rotation@(p-shoulder)
    for p in obj.data.polygons: p.use_smooth=True
    scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
    scene.render.resolution_x=512; scene.render.resolution_y=512; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'; scene.render.film_transparent=True
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background'); bg.inputs[0].default_value=(0.12,0.15,0.17,1); bg.inputs[1].default_value=0.45
    area('Key',(-2.5,-3.5,4.0),420,3.0,(1.0,0.86,0.72))
    area('Fill',(2.5,-2.0,2.5),250,2.5,(0.68,0.80,1.0))
    area('Rim',(0,2.0,3.7),380,2.0,(1.0,0.92,0.80))
    bpy.ops.object.camera_add(location=(0,-4.0,1.70))
    cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,1.58))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=0.74; scene.camera=cam
    scene.render.filepath=str(OUT/(key+'_hd_portrait.png'))
    bpy.ops.render.render(write_still=True)
    print('PORTRAIT_RENDERED',key,scene.render.filepath)
