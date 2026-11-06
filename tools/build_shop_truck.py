import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
MODELS=ROOT/'assets'/'models'
SOURCE=ROOT/'assets'/'blender'
RENDERS=ROOT/'renders'
for folder in (MODELS,SOURCE,RENDERS): folder.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials): bpy.data.materials.remove(data)
MATS={}

def mat(key,color,rough=0.65,metal=0.0):
    color=color.lstrip('#')
    rgb=tuple(int(color[i:i+2],16)/255 for i in (0,2,4))
    rgba=tuple(c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb)+(1,)
    m=bpy.data.materials.new(key); m.diffuse_color=rgba; m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=rgba; p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    MATS[key]=m; return m

for key,color in {
    'cream':'d9d5b9','mint':'508d80','coral':'c95d4c','white':'ece8d5','ink':'202b2a',
    'rubber':'151b1b','chrome':'879693','glass':'35515a','wood':'765a3c','rust':'8b4931',
    'skin':'c98e66','skin_light':'dfaa7f','hair':'382b25','shirt':'d8d2ba','apron':'496b61',
    'yellow':'e4ba51','red':'a84336','ammo':'566b4c','bandage':'d6d7c5'
}.items(): mat(key,color)
mat('lamp','f2cf71',0.3,0.15); mat('steel','52605e',0.35,0.65)

def assign(o,material): o.data.materials.append(MATS[material]); return o

def cube(name,loc,dims,material,bevel=0.025,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    assign(o,material)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=bevel; b.segments=2
    return o

def sphere(name,loc,scale,material,segments=16,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def cyl(name,loc,radius,depth,material,vertices=16,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name
    if rot: o.rotation_euler=rot
    assign(o,material)
    b=o.modifiers.new('Edge bevel','BEVEL'); b.width=0.015; b.segments=2
    return o

def beam(name,a,b,width,material):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,width,(b-a).length),material,0.025)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def text(name,body,loc,size,material,rot=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.data.body=body; o.data.align_x='CENTER'; o.data.align_y='CENTER'
    o.data.size=size; o.data.extrude=0.004; o.data.bevel_depth=0.001; assign(o,material); return o

# Chassis and front cab.
cube('Chassis',(0,0,0.55),(2.35,4.15,0.30),'ink',0.08)
cube('CargoFloor',(0,0.65,0.78),(2.28,2.65,0.30),'mint',0.08)
cube('CabBody',(0,-1.30,1.05),(2.28,1.55,1.10),'cream',0.12)
cube('CabRoof',(0,-1.18,2.22),(2.32,1.80,0.20),'mint',0.08)
cube('FrontNose',(0,-2.00,0.98),(2.25,0.25,0.65),'mint',0.08)
cube('Windshield',(0,-1.985,1.70),(1.88,0.055,0.68),'glass',0.055,(math.radians(-8),0,0))
cube('WindshieldDivider',(0,-2.025,1.70),(0.055,0.035,0.70),'cream',0.01)
for x in (-1.15,1.15):
    cube('CabDoor',(x,-1.25,1.18),(0.06,1.22,0.90),'cream',0.035)
    cube('CabSideGlass',(x*1.015,-1.24,1.73),(0.035,1.10,0.55),'glass',0.025)
    cube('DoorHandle',(x*1.035,-0.91,1.27),(0.045,0.24,0.055),'chrome',0.015)
    beam('MirrorArm',(x,-1.70,1.70),(x*1.24,-1.87,1.72),0.045,'steel')
    cube('Mirror',(x*1.26,-1.88,1.75),(0.12,0.18,0.24),'ink',0.035)
    cube('Headlight',(x*0.72,-2.14,1.02),(0.40,0.055,0.25),'lamp',0.05)
cube('Grille',(0,-2.15,0.90),(0.88,0.05,0.28),'ink',0.025)
for z in (0.82,0.90,0.98): cube('GrilleSlat',(0,-2.185,z),(0.82,0.025,0.022),'chrome',0.005)
cube('FrontBumper',(0,-2.20,0.61),(2.42,0.20,0.18),'chrome',0.05)
cube('Plate',(0,-2.315,0.62),(0.58,0.025,0.14),'yellow',0.015)
text('PlateText','LAST-07',(0,-2.335,0.62),0.085,'ink')

# Cargo shell leaves a real open serving window on the right side.
cube('CargoBack',(0,1.94,1.66),(2.28,0.15,1.85),'mint',0.06)
cube('CargoLeft',(-1.10,0.63,1.67),(0.14,2.55,1.85),'mint',0.04)
cube('CargoRightLower',(1.10,0.63,0.92),(0.14,2.55,0.55),'mint',0.04)
cube('CargoRightTop',(1.10,0.63,2.39),(0.14,2.55,0.35),'mint',0.04)
for y in (-0.60,1.87): cube('WindowPost',(1.11,y,1.78),(0.15,0.12,1.25),'cream',0.025)
cube('CargoFront',(0,-0.60,1.78),(2.25,0.12,1.30),'mint',0.04)
cube('CargoRoof',(0,0.66,2.61),(2.38,2.80,0.20),'cream',0.07)
cube('ServingCounter',(1.30,0.63,1.17),(0.55,2.55,0.13),'wood',0.04)
cube('CounterTrim',(1.58,0.63,1.18),(0.045,2.55,0.12),'chrome',0.015)
# Striped awning and support arms.
for i in range(8):
    y=-0.47+i*0.315
    cube('AwningStripe',(1.53,y,2.35),(0.95,0.31,0.10),'coral' if i%2==0 else 'white',0.025,(0,math.radians(-10),0))
    cube('AwningValance',(1.99,y,2.22),(0.08,0.31,0.24),'coral' if i%2==0 else 'white',0.025)
for y in (-0.50,1.75): beam('AwningSupport',(1.13,y,1.90),(1.92,y,2.31),0.045,'steel')

# Wheels, hubs, fenders and rust.
for x in (-1.20,1.20):
    for y in (-1.34,1.30):
        cyl('Tire',(x,y,0.52),0.47,0.25,'rubber',20,(0,math.pi/2,0))
        cyl('Hub',(x*1.11,y,0.52),0.25,0.055,'chrome',16,(0,math.pi/2,0))
        cyl('HubCap',(x*1.14,y,0.52),0.10,0.06,'ink',12,(0,math.pi/2,0))
        for a in range(6):
            angle=a*math.tau/6
            cyl('WheelBolt',(x*1.17,y+0.15*math.cos(angle),0.52+0.15*math.sin(angle)),0.022,0.025,'steel',8,(0,math.pi/2,0))
for y in (-1.34,1.30): cube('Fender',(1.10,y,0.91),(0.26,1.08,0.12),'cream',0.05)
for y,z,sy in [(-0.25,0.75,0.36),(1.40,0.90,0.28),(-1.58,0.88,0.24)]:
    cube('RustPatch',(1.177,y,z),(0.018,sy,0.11),'rust',0.01,(0,0,0.12))

# Vendor standing inside the serving hatch, facing right.
vx,vy=0.64,0.48
for y in (vy-0.16,vy+0.16):
    cube('VendorBoot',(vx+0.05,y,0.88),(0.34,0.22,0.18),'ink',0.045)
    cube('VendorLeg',(vx,y,1.12),(0.25,0.23,0.43),'ink',0.05)
cube('VendorTorso',(vx,vy,1.52),(0.48,0.62,0.62),'shirt',0.10)
cube('VendorApron',(vx+0.255,vy,1.46),(0.065,0.48,0.57),'apron',0.035)
cube('ApronPocket',(vx+0.295,vy,1.37),(0.035,0.28,0.17),'mint',0.02)
cube('NameTag',(vx+0.302,vy-0.16,1.67),(0.025,0.16,0.07),'white',0.01)
cube('VendorNeck',(vx,vy,1.88),(0.20,0.20,0.18),'skin',0.035)
sphere('VendorHead',(vx+0.015,vy,2.08),(0.25,0.24,0.28),'skin_light',20,12)
for y in (vy-0.245,vy+0.245): sphere('VendorEar',(vx,y,2.08),(0.07,0.045,0.09),'skin',12,8)
sphere('VendorNose',(vx+0.265,vy,2.07),(0.075,0.065,0.08),'skin_light',12,8)
for y in (vy-0.09,vy+0.09):
    sphere('VendorEyeWhite',(vx+0.235,y,2.14),(0.022,0.052,0.032),'white',12,8)
    sphere('VendorPupil',(vx+0.255,y,2.14),(0.012,0.020,0.023),'ink',10,6)
    beam('VendorBrow',(vx+0.237,y-0.05,2.20),(vx+0.237,y+0.05,2.20),0.020,'hair')
cube('VendorMouth',(vx+0.245,vy,1.97),(0.025,0.13,0.025),'red',0.008)
sphere('VendorHair',(vx-0.035,vy,2.25),(0.23,0.24,0.13),'hair',16,8)
cube('VendorCap',(vx,vy,2.32),(0.48,0.50,0.14),'coral',0.06)
cube('VendorCapBill',(vx+0.29,vy,2.29),(0.26,0.43,0.055),'coral',0.025)
for y,dy in [(vy-0.36,-0.05),(vy+0.36,0.05)]:
    beam('VendorUpperArm',(vx,y,1.74),(vx+0.20,y+dy,1.45),0.20,'shirt')
    beam('VendorForearm',(vx+0.20,y+dy,1.45),(1.19,y+dy,1.34),0.16,'skin')
    sphere('VendorHand',(1.20,y+dy,1.34),(0.13,0.10,0.08),'skin_light',12,8)

# Interior shelves and visible wares.
for z in (1.30,1.72): cube('Shelf',(-0.70,0.75,z),(0.48,1.75,0.09),'wood',0.025)
for i in range(4):
    y=0.05+i*0.40
    cube('SupplyBox',(-0.68,y,1.47),(0.35,0.30,0.27),'ammo' if i%2==0 else 'bandage',0.025)
    cube('SupplyLabel',(-0.49,y,1.47),(0.025,0.16,0.10),'white',0.005)
for i in range(3):
    cyl('Bottle',(-0.68,0.15+i*0.48,1.89),0.09,0.29,'glass',12)
    cyl('BottleCap',(-0.68,0.15+i*0.48,2.06),0.055,0.06,'yellow',10)

# Signage and a playful ice-cream-cone roof ornament.
cube('FrontSign',(0,-1.44,2.42),(1.75,0.15,0.38),'coral',0.055)
text('SupplySign','SUPPLY',(0,-1.53,2.42),0.27,'white')
text('TruckSideBrand','LAST CLIP',(1.185,0.64,0.87),0.19,'cream',(math.pi/2,0,math.pi/2))
bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=0.12,radius2=0.32,depth=0.70,location=(0,0.62,3.03))
cone=bpy.context.object; cone.name='RoofCone'; assign(cone,'wood')
sphere('RoofScoop',(0,0.62,3.43),(0.37,0.37,0.30),'coral',20,12)
sphere('RoofScoopTop',(0.16,0.62,3.63),(0.23,0.23,0.19),'cream',16,10)

# Export editable source and mobile-friendly GLB.
bpy.ops.object.select_all(action='SELECT')
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(MODELS/'supply_truck.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'supply_truck.blend'))
print('MODEL_EXPORTED supply_truck',len([o for o in bpy.context.scene.objects if o.type=='MESH']))

# Product render, including a floor that is not exported.
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=40; scene.cycles.use_denoising=True
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.34,0.39,0.42,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.65
cube('RenderFloor',(0,0,-0.08),(200,200,0.10),'steel',0)
for name,loc,energy,size in [('Key',(4,-6,7),1000,5),('Fill',(-4,-1,5),750,4),('Window',(5,3,4),650,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    lamp=bpy.context.object; lamp.name=name; lamp.data.energy=energy; lamp.data.shape='DISK'; lamp.data.size=size
    lamp.rotation_euler=(Vector((0.3,0,1.5))-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(6.6,-8.5,5.1))
cam=bpy.context.object; cam.name='Camera'; cam.rotation_euler=(Vector((0.25,0,1.55))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=6.6; scene.camera=cam
scene.render.resolution_x=1000; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(RENDERS/'supply_truck.png')
bpy.ops.render.render(write_still=True)
print('SHOP_TRUCK_RENDERED',scene.render.filepath)
