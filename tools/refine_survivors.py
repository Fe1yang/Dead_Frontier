import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets'/'blender'
MODELS=ROOT/'assets'/'models'
RENDERS=ROOT/'renders'

def material(name,color=None):
    m=bpy.data.materials.get(name)
    if m or color is None: return m
    color=color.lstrip('#'); rgb=tuple(int(color[i:i+2],16)/255 for i in (0,2,4))
    rgba=tuple(c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb)+(1,)
    m=bpy.data.materials.new(name); m.diffuse_color=rgba; m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=rgba; p.inputs['Roughness'].default_value=0.68
    return m

def assign(o,name): o.data.materials.append(material(name)); return o

def cube(name,loc,dims,mat,bevel=0.015,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name='Detail'+name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    assign(o,mat)
    if bevel:
        b=o.modifiers.new('Detail bevel','BEVEL'); b.width=bevel; b.segments=2
    return o

def sphere(name,loc,scale,mat,segments=14,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc)
    o=bpy.context.object; o.name='Detail'+name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,mat)
    for p in o.data.polygons: p.use_smooth=True
    return o

def cyl(name,loc,radius,depth,mat,rot=None,vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name='Detail'+name
    if rot: o.rotation_euler=rot
    assign(o,mat); return o

def beam(name,a,b,width,mat):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,width,(b-a).length),mat,0.008)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def common_gear(female=False):
    # Finger segments wrap around the weapon instead of featureless block hands.
    for side in (-1,1):
        x=side*0.14
        for i in range(4):
            cube('Finger',(x+(i-1.5)*0.032,-0.65 if side<0 else -0.78,1.27),(0.025,0.14,0.035),'skin',0.01,(0.12,0,0))
        cube('KnucklePad',(x,-0.60 if side<0 else -0.74,1.34),(0.16,0.12,0.045),'strap',0.012)
    for i in range(6): cube('PicatinnyRail',(0,-0.43-i*0.095,1.455),(0.16,0.042,0.032),'gun_edge',0.005)
    cube('Foregrip',(0,-0.83,1.19),(0.11,0.14,0.25),'gun',0.02,(0.12,0,0))
    cube('TriggerGuard',(0,-0.48,1.20),(0.13,0.16,0.035),'gun_edge',0.008)
    cube('SightLens',(0,-0.735,1.50),(0.075,0.018,0.055),'glass',0.008)
    for z in (1.08,1.16,1.24): cube('MagazineGroove',(0,-0.666,z),(0.13,0.018,0.025),'gun_edge',0.004)
    cube('BeltBuckle',(0,-0.218,0.89),(0.13,0.045,0.10),'gun_edge',0.012)
    for x in (-0.18,0.18):
        cube('BootSole',(x,-0.07,0.045),(0.26,0.45,0.07),'ink',0.02)
        for z in (0.13,0.20): cube('BootStrap',(x,-0.215,z),(0.23,0.045,0.045),'gun_edge',0.008)
    # Dog tags and chain links.
    for i in range(7):
        a=i/6*math.pi
        sphere('Chain',(0.10*math.cos(a),-0.255,1.44-0.10*math.sin(a)),(0.012,0.010,0.012),'gun_edge',8,4)
    cube('DogTag',(0,-0.27,1.31),(0.09,0.022,0.13),'gun_edge',0.015,(0,0,0.12))

def male_details():
    material('hair','302820'); material('eye_white','d9d8c4'); material('iris','526654')
    for x in (-0.09,0.09):
        sphere('Ear',(math.copysign(0.245,x),-0.005,1.72),(0.052,0.045,0.09),'skin')
        sphere('EyeWhite',(x,-0.226,1.77),(0.054,0.019,0.029),'eye_white')
        sphere('Iris',(x,-0.245,1.77),(0.022,0.010,0.023),'iris')
        sphere('Pupil',(x,-0.253,1.77),(0.010,0.006,0.014),'ink',10,6)
        beam('Brow',(x-0.055,-0.231,1.825),(x+0.05,-0.231,1.82),0.024,'hair')
        cube('Sideburn',(math.copysign(0.225,x),0.005,1.80),(0.045,0.15,0.20),'hair',0.018)
    cube('Mouth',(0,-0.235,1.60),(0.13,0.025,0.026),'blood',0.008)
    cube('LowerLip',(0,-0.235,1.575),(0.09,0.018,0.016),'skin',0.006)
    cube('CapSeam',(0,-0.232,1.93),(0.025,0.025,0.12),'gun_edge',0.005)
    for x in (-0.17,0.17): cube('CapStitch',(x,-0.215,1.90),(0.09,0.018,0.018),'bag',0.004)
    for side in (-1,1):
        cube('Collar',(side*0.17,-0.235,1.46),(0.20,0.07,0.19),'lime_dark',0.02,(0,0,side*0.28))
        cube('ShoulderPad',(side*0.36,0,1.43),(0.23,0.43,0.15),'bag',0.04)
        cube('KneePad',(side*0.18,-0.145,0.54),(0.23,0.10,0.22),'ink',0.035)
        cube('KneePadRidge',(side*0.18,-0.202,0.54),(0.14,0.025,0.05),'gun_edge',0.008)
    for z in (1.08,1.20,1.32): cube('Molle',(0,-0.302,z),(0.48,0.035,0.035),'strap',0.006)
    for x in (-0.19,0.0,0.19):
        cube('VestPouch',(x,-0.34,1.05),(0.16,0.14,0.22),'bag',0.025)
        cube('PouchFlap',(x,-0.419,1.12),(0.15,0.025,0.07),'strap',0.008)
        cube('PouchSnap',(x,-0.437,1.10),(0.035,0.012,0.035),'gun_edge',0.005)
    cube('BackpackPocket',(0,0.44,1.15),(0.40,0.16,0.30),'strap',0.04)
    cyl('Bedroll',(0,0.32,1.53),0.12,0.54,'pants',(0,math.pi/2,0),14)
    for x in (-0.18,0.18): cube('BedrollStrap',(x,0.32,1.53),(0.055,0.26,0.26),'strap',0.012)

def female_details():
    material('iris','526654')
    for x in (-0.085,0.085):
        sphere('Iris',(x,-0.247,1.77),(0.022,0.008,0.023),'iris')
        for dx in (-0.025,0.025): beam('Eyelash',(x+dx,-0.24,1.785),(x+dx*1.3,-0.246,1.81),0.009,'hair')
    cube('JacketZip',(0,-0.246,1.22),(0.022,0.020,0.43),'gun_edge',0.004)
    for z in (1.08,1.17,1.26,1.35): cube('ZipTooth',(0,-0.260,z),(0.045,0.012,0.018),'chrome' if bpy.data.materials.get('chrome') else 'gun_edge',0.003)
    for side in (-1,1):
        cube('JacketCollar',(side*0.15,-0.22,1.47),(0.18,0.075,0.19),'jacket_dark',0.02,(0,0,side*0.30))
        cube('SleeveCuff',(side*0.39,-0.27,1.20),(0.21,0.13,0.10),'jacket_dark',0.02)
        cube('ShoulderSeam',(side*0.27,-0.225,1.45),(0.18,0.025,0.025),'jacket_dark',0.004)
        cube('CargoPocket',(side*0.18,-0.13,0.72),(0.20,0.08,0.20),'strap',0.018)
    cube('HairClip',(0.19,-0.17,1.91),(0.10,0.025,0.035),'yellow',0.008,(0,0,0.35))
    cube('Holster',(0.34,0.02,0.75),(0.15,0.24,0.31),'strap',0.025,(0,0,-0.12))
    cube('HolsterBuckle',(0.36,-0.11,0.83),(0.12,0.035,0.06),'gun_edge',0.008)
    for x in (-0.20,0.20): cube('BackpackSeam',(x,0.37,1.20),(0.025,0.025,0.33),'strap',0.004)

def render(name):
    scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=40; scene.cycles.use_denoising=True
    scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.20,0.24,0.26,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.6
    for key,loc,power,size in [('Key',(2,-4,5),700,4),('Fill',(-3,-1,3),450,3),('Rim',(1,3,4),500,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        o=bpy.context.object; o.name=key; o.data.energy=power; o.data.size=size
        o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(2.5,-4.5,2.6))
    cam=bpy.context.object; cam.rotation_euler=(Vector((0,-0.05,1.12))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=2.55; scene.camera=cam
    scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(RENDERS/(name+'.png'))
    bpy.ops.render.render(write_still=True)

for asset in ('survivor','survivor_female'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    for o in list(bpy.context.scene.objects):
        if o.name.startswith('Detail'): bpy.data.objects.remove(o,do_unlink=True)
    material('chrome','879693')
    common_gear(asset=='survivor_female')
    female_details() if asset=='survivor_female' else male_details()
    bpy.ops.object.select_all(action='SELECT')
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':
            bpy.context.view_layer.objects.active=o
            for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.export_scene.gltf(filepath=str(MODELS/(asset+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    print('SURVIVOR_REFINED',asset,len([o for o in bpy.context.scene.objects if o.type=='MESH']))
    render(asset)
print('SURVIVORS_DONE')
