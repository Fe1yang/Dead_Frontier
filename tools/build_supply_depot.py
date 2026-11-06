import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'supply_truck.glb'
MERCHANT=ROOT/'assets'/'models'/'generated'/'merchant_hd.glb'
BLEND=ROOT/'assets'/'blender'/'supply_depot.blend'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
MATS={}

def mat(name,hex_color,rough=0.72,metal=0.0):
    h=hex_color.lstrip('#')
    rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    rgba=tuple(c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb)+(1,)
    m=bpy.data.materials.new(name); m.diffuse_color=rgba; m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=rgba
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    MATS[name]=m

def assign(o,name):
    o.data.materials.append(MATS[name]); return o

def cube(name,loc,dims,material,bevel=0.035,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    assign(o,material)
    if bevel:
        b=o.modifiers.new('Machined edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,radius,depth,material,vertices=24,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name
    if rot: o.rotation_euler=rot
    assign(o,material)
    b=o.modifiers.new('Edge bevel','BEVEL'); b.width=0.018; b.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def beam(name,a,b,width,material):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,width,(b-a).length),material,0.018)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return o

def text(name,body,loc,size,material,rot=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.data.body=body; o.data.align_x='CENTER'; o.data.align_y='CENTER'
    o.data.size=size; o.data.extrude=0.006; o.data.bevel_depth=0.0015; assign(o,material)
    return o

for name,color in {
    'olive':'46534a','olive_light':'667265','olive_dark':'2c3732','canvas':'343d36',
    'steel':'606c68','darkmetal':'202927','rubber':'141918','glass':'273f45',
    'rust':'87513a','wood':'66523c','cream':'d4d0b7','mark':'d9b66d',
    'red':'9e4036','amber':'e6b85c','medical':'d6d7c9','ammo':'4c6045'
}.items(): mat(name,color)
mat('steel', '606c68',0.35,0.65)
mat('glass','273f45',0.18,0.25)
mat('lamp','ffd78a',0.25,0.1)
p=next(n for n in MATS['lamp'].node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
p.inputs['Emission Color'].default_value=(1.0,0.55,0.18,1)
p.inputs['Emission Strength'].default_value=2.0

# A rugged supply truck: long cargo body, armored cab, no ice-cream ornament.
cube('Chassis',(0,0,0.62),(5.5,2.25,0.34),'darkmetal',0.08)
cube('CargoFloor',(0.85,0,0.88),(3.55,2.35,0.26),'olive_dark',0.05)
cube('CabLower',(-1.95,0,1.12),(1.75,2.22,1.02),'olive',0.10)
cube('CabUpper',(-1.72,0,2.00),(1.45,2.12,0.92),'olive_light',0.09)
cube('CabRoof',(-1.70,0,2.52),(1.62,2.30,0.16),'olive_dark',0.06)
cube('Hood',(-2.75,0,1.32),(0.52,2.12,0.42),'olive',0.08)
for y in (-0.57,0.57):
    cube('Windshield',(-2.47,y,2.07),(0.055,0.91,0.60),'glass',0.04,(0,math.radians(-10),0))
    cube('CabSideWindow',(-1.73,y*1.92,2.07),(0.94,0.045,0.56),'glass',0.035)
    cube('DoorPanel',(-1.66,y*1.94,1.43),(1.05,0.055,0.55),'olive',0.035)
    cube('DoorHandle',(-1.33,y*2.00,1.68),(0.24,0.045,0.055),'steel',0.012)
    cube('Headlamp',(-3.025,y*1.25,1.38),(0.055,0.38,0.24),'lamp',0.045)
    beam('MirrorArm',(-2.05,y*1.75,2.12),(-2.05,y*2.12,2.12),0.045,'steel')
    cube('Mirror',(-2.05,y*2.16,2.13),(0.20,0.10,0.30),'darkmetal',0.035)
cube('FrontGrille',(-3.035,0,1.04),(0.05,1.10,0.36),'darkmetal',0.025)
for y in (-0.42,-0.21,0,0.21,0.42): cube('GrilleSlat',(-3.07,y,1.04),(0.025,0.055,0.31),'steel',0.008)
cube('FrontBumper',(-3.14,0,0.78),(0.20,2.40,0.20),'steel',0.045)
cube('BumperPlate',(-3.25,0,0.80),(0.025,0.62,0.16),'mark',0.012)
text('PlateText','LAST-07',(-3.27,0,0.80),0.10,'darkmetal',(math.pi/2,0,-math.pi/2))

# Open serving hatch, large enough to frame the new merchant.
cube('CargoBack',(0.88,1.12,1.99),(3.55,0.16,2.15),'olive',0.05)
cube('CargoEnd',(2.61,0,1.99),(0.16,2.26,2.15),'olive',0.05)
cube('CargoFront',(-0.84,0,1.99),(0.16,2.26,2.15),'olive',0.05)
cube('ServiceLower',(0.88,-1.12,1.13),(3.55,0.16,0.52),'olive_light',0.04)
cube('ServiceTop',(0.88,-1.12,2.92),(3.55,0.16,0.28),'olive_dark',0.04)
for x in (-0.80,2.55): cube('WindowPost',(x,-1.14,2.05),(0.15,0.18,1.66),'steel',0.025)
cube('CargoRoof',(0.88,0,3.09),(3.72,2.48,0.18),'olive_dark',0.055)
cube('ServingCounter',(0.88,-1.35,1.42),(3.60,0.66,0.16),'wood',0.045)
cube('CounterEdge',(0.88,-1.69,1.42),(3.65,0.055,0.18),'steel',0.018)
# Plain canvas awning with supports, not striped ice-cream styling.
cube('Awning',(0.88,-1.52,2.96),(3.90,1.05,0.10),'canvas',0.035,(math.radians(8),0,0))
cube('AwningEdge',(0.88,-2.02,2.85),(3.90,0.10,0.26),'canvas',0.025)
for x in (-0.78,2.54): beam('AwningSupport',(x,-1.18,2.30),(x,-1.96,2.88),0.055,'steel')
text('SupplySign','FIELD SUPPLY  /  07',(0.88,-2.085,2.86),0.20,'cream')

# Wheels, hubs, tread blocks, armored fenders.
for x in (-1.98,1.72):
    for y in (-1.20,1.20):
        cyl('Tire',(x,y,0.66),0.57,0.32,'rubber',32,(math.pi/2,0,0))
        cyl('Hub',(x,y*1.15,0.66),0.30,0.08,'steel',24,(math.pi/2,0,0))
        cyl('HubCap',(x,y*1.19,0.66),0.13,0.07,'darkmetal',16,(math.pi/2,0,0))
        for i in range(16):
            a=i*math.tau/16
            o=cube('TireTread',(x+0.55*math.sin(a),y,0.66+0.55*math.cos(a)),(0.17,0.35,0.055),'rubber',0.008)
            o.rotation_euler[1]=a
        cube('Fender',(x,y,1.18),(1.30,0.42,0.15),'olive_dark',0.045)

# Panel ribs, rivets, wear and recovery hardware.
for x in (-0.55,-0.05,0.45,0.95,1.45,1.95,2.45):
    cube('PanelRib',(x,1.225,1.95),(0.045,0.055,1.80),'olive_dark',0.01)
    for z in (1.12,2.82): cyl('Rivet',(x,-1.215,z),0.032,0.025,'steel',10,(math.pi/2,0,0))
for x,z,w in [(-0.35,1.10,0.42),(1.90,1.05,0.34),(2.25,2.86,0.28),(-1.75,1.28,0.35)]:
    cube('RustWear',(x,-1.215,z),(w,0.012,0.075),'rust',0.01,(0,0.08,0))
beam('RoofRail',(-0.65,0.90,3.33),(2.42,0.90,3.33),0.055,'steel')
beam('RoofRail',(-0.65,-0.90,3.33),(2.42,-0.90,3.33),0.055,'steel')
for x in (-0.65,2.42):
    for y in (-0.90,0.90): beam('RoofRiser',(x,y,3.10),(x,y,3.34),0.055,'steel')
cube('RoofCrate',(1.35,0.12,3.40),(1.10,1.25,0.52),'ammo',0.055)
for x in (0.97,1.72): cube('CrateStrap',(x,0.12,3.68),(0.09,1.28,0.045),'darkmetal',0.008)

# Shelves and recognizable supplies around the merchant.
for z in (1.52,2.05): cube('InteriorShelf',(0.90,0.72,z),(2.95,0.55,0.10),'wood',0.025)
for i in range(6):
    x=-0.25+i*0.47
    cube('AmmoBox',(x,0.64,1.75),(0.38,0.38,0.35),'ammo' if i%2==0 else 'medical',0.025)
    cube('SupplyLabel',(x,0.435,1.75),(0.19,0.018,0.11),'cream',0.006)
    if i%2: cube('MedicalCross',(x,0.421,1.75),(0.10,0.012,0.032),'red',0.003)
for i in range(4):
    x=-0.20+i*0.66
    cube('Crate',(x,-1.39,1.64),(0.48,0.42,0.30),'ammo',0.025)
    cube('CrateLatch',(x,-1.61,1.64),(0.08,0.025,0.13),'steel',0.008)
cyl('SupplyLantern',(2.24,-1.35,1.79),0.13,0.38,'lamp',20)
cyl('LanternCap',(2.24,-1.35,2.00),0.17,0.08,'darkmetal',20)

# Import the actual new merchant and normalize him to a standing adult.
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(MERCHANT))
merchant_meshes=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in merchant_meshes: o.select_set(True)
bpy.context.view_layer.objects.active=merchant_meshes[0]
if len(merchant_meshes)>1: bpy.ops.object.join()
merchant=bpy.context.object; merchant.name='Merchant_HD'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
coords=[merchant.matrix_world@Vector(c) for c in merchant.bound_box]
mins=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
maxs=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
scale=1.82/(maxs.z-mins.z)
merchant.scale=(scale,scale,scale)
merchant.rotation_euler[2]=-math.pi
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
coords=[merchant.matrix_world@Vector(c) for c in merchant.bound_box]
mins=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
maxs=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
merchant.location+=Vector((0.70-(mins.x+maxs.x)/2,-0.47-(mins.y+maxs.y)/2,0.90-mins.z))
# Keep textured detail while reducing the static shop mesh for mobile.
dec=merchant.modifiers.new('Mobile LOD','DECIMATE'); dec.ratio=0.28
bpy.context.view_layer.objects.active=merchant
bpy.ops.object.modifier_apply(modifier=dec.name)
for p in merchant.data.polygons: p.use_smooth=True

bpy.ops.object.select_all(action='SELECT')
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers):
            try: bpy.ops.object.modifier_apply(modifier=mod.name)
            except RuntimeError: pass
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
print('SUPPLY_DEPOT_EXPORTED',OUT,'objects',len(bpy.context.scene.objects))
