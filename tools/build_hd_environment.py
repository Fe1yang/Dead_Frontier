import bpy
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'environment'
SOURCE=ROOT/'assets'/'blender'/'environment'
for folder in (OUT,SOURCE): folder.mkdir(parents=True,exist_ok=True)
MATS={}
random.seed(20261103)

def linear(v):
    v=v/255
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4

def material(name,color,rough=0.8,metal=0.0,emission=0.0):
    if name in MATS: return MATS[name]
    rgb=tuple(linear(int(color[i:i+2],16)) for i in (0,2,4))
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*rgb,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*rgb,1); p.inputs['Emission Strength'].default_value=emission
    MATS[name]=m
    return m

def assign(o,mat):
    o.data.materials.append(MATS[mat] if isinstance(mat,str) else mat)
    return o

def bevel(o,width=0.02,segments=2):
    if width<=0: return
    mod=o.modifiers.new('Edge highlights','BEVEL'); mod.width=width; mod.segments=segments
    mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')

def cube(name,loc,dims,mat,edge=0.0,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    assign(o,mat); bevel(o,edge)
    return o

def cylinder(name,loc,radius,depth,mat,axis='Z',vertices=20):
    rotation={'Z':(0,0,0),'Y':(math.pi/2,0,0),'X':(0,math.pi/2,0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=bpy.context.object; o.name=name; assign(o,mat); bevel(o,0.008,2)
    for p in o.data.polygons: p.use_smooth=True
    return o

def beam(name,a,b,width,mat):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,width,(b-a).length),mat,0.006)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def uv_world(o,scale=3.0):
    uv=o.data.uv_layers.active
    if not uv: return
    for poly in o.data.polygons:
        n=poly.normal
        for li in poly.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            if abs(n.z)>0.5: uv.data[li].uv=(co.x/scale,co.y/scale)
            elif abs(n.x)>0.5: uv.data[li].uv=(co.y/scale,co.z/scale)
            else: uv.data[li].uv=(co.x/scale,co.z/scale)

def road(variant):
    o=cube('Continuous asphalt',(0,0,-0.13),(8.35,16.0,0.26),'PBR_asphalt')
    uv_world(o,4.0)
    for side in (-1,1):
        walk=cube('Pavement',(side*6.12,0,0.04),(3.45,16,0.22),'PBR_pavement',0.012); uv_world(walk,2.4)
        cube('Concrete curb',(side*4.20,0,0.10),(0.32,16,0.32),'PBR_concrete',0.025)
        cube('Road edge paint',(side*3.73,0,0.008),(0.10,16,0.012),'paint',0.003)
        cube('Gutter',(side*3.96,0,-0.008),(0.26,16,0.035),'gutter')
        for y in (-5.8,5.8):
            cube('Drain inset',(side*3.94,y,0.015),(0.28,0.64,0.025),'darkmetal',0.005)
            for k in range(7): cube('Drain slot',(side*3.94,y-0.25+k*0.083,0.032),(0.22,0.022,0.012),'steel')
    for y in (-6,2): cube('Long center dash',(0,y,0.011),(0.13,4.8,0.015),'paint',0.004)
    # Utility covers belong on the pavement and should not repeat on every block.
    if variant%4==0:
        side=1 if variant%8==0 else -1
        x=side*5.35
        cylinder('Sidewalk utility access',(x,4.9,0.160),0.34,0.018,'darkmetal',vertices=48)
        for k in range(-3,4): cube('Utility cover rib',(x+k*0.068,4.9,0.173),(0.022,0.46,0.012),'steel',0.002)

def front_box(name,side,y,z,width,height,depth,mat,x=8.04,edge=0.0):
    return cube(name,(side*x,y,z),(depth,width,height),mat,edge)

def end_box(name,x,y,z,width,height,depth,mat,edge=0.0):
    return cube(name,(x,y,z),(width,depth,height),mat,edge)

def front_window(side,y,z,w=1.05,h=1.35,style=0):
    front_box('Window recess',side,y,z,w+0.18,h+0.18,0.10,'recess',8.035,0.012)
    front_box('Glass pane',side,y,z,w,h,0.025,'glass_dark' if style%4==0 else 'glass',7.972,0.008)
    for yy in (y-w/2-0.045,y+w/2+0.045): front_box('Window jamb',side,yy,z,0.075,h+0.15,0.10,'frame',7.91,0.006)
    for zz in (z-h/2-0.045,z+h/2+0.045): front_box('Window rail',side,y,zz,w+0.15,0.075,0.10,'frame',7.91,0.006)
    front_box('Window mullion',side,y,z,0.045,h,0.075,'frame',7.895,0.004)
    front_box('Projecting sill',side,y,z-h/2-0.13,w+0.32,0.12,0.28,'concrete_trim',7.91,0.012)
    if style%5==0:
        for dz in (-0.28,-0.14,0,0.14,0.28): front_box('Venetian blind',side,y,z+dz,w*0.90,0.028,0.02,'blind',7.945)

def end_window(x,y,z,w=1.0,h=1.25,style=0):
    end_box('End window recess',x,y,z,w+0.15,h+0.15,0.09,'recess',0.01)
    end_box('End glass',x,y+0.052,z,w,h,0.025,'glass' if style%3 else 'glass_dark',0.008)
    for xx in (x-w/2-0.04,x+w/2+0.04): end_box('End jamb',xx,y+0.075,z,0.065,h+0.12,0.07,'frame',0.004)
    for zz in (z-h/2-0.04,z+h/2+0.04): end_box('End rail',x,y+0.075,zz,w+0.12,0.065,0.07,'frame',0.004)
    end_box('End mullion',x,y+0.09,z,0.04,h,0.06,'frame',0.003)

def facade_sign(side,y,z,text,width=3.1,color='sign_teal'):
    front_box('Sign surround',side,y,z,width,0.65,0.20,'darkmetal',7.78,0.035)
    front_box('Sign face',side,y,z,width-0.12,0.51,0.035,color,7.665,0.018)
    bpy.ops.object.text_add(location=(side*7.635,y,z),rotation=(math.pi/2,0,-side*math.pi/2))
    o=bpy.context.object; o.name='Store lettering'; o.data.body=text; o.data.align_x='CENTER'; o.data.align_y='CENTER'; o.data.size=0.28; o.data.extrude=0.004
    assign(o,'lettering')
    bpy.ops.object.convert(target='MESH')

def aircon(side,y,z):
    front_box('AC cabinet',side,y,z,0.78,0.52,0.42,'ac_paint',7.74,0.035)
    front_box('AC grille',side,y,z,0.58,0.35,0.025,'darkmetal',7.515,0.012)
    for k in range(6): front_box('AC vent slat',side,y,z-0.14+k*0.056,0.52,0.018,0.018,'steel',7.49)
    for yy in (y-0.28,y+0.28): beam('AC bracket',(side*8.02,yy,z-0.34),(side*7.58,yy,z-0.34),0.045,'steel')

def rooftop(x,y,width,depth,height,style):
    cube('Roof membrane',(x,y,height+0.03),(width,depth,0.12),'roof',0.015)
    for xx in (x-width/2,x+width/2): cube('Roof parapet',(xx,y,height+0.30),(0.16,depth,0.55),'concrete_trim',0.018)
    for yy in (y-depth/2,y+depth/2): cube('Roof parapet',(x,yy,height+0.30),(width,0.16,0.55),'concrete_trim',0.018)
    for j in range(1+style%2):
        xx=x+(j-0.4)*1.4
        cube('HVAC curb',(xx,y,height+0.22),(1.20,1.50,0.25),'darkmetal',0.02)
        cube('HVAC unit',(xx,y,height+0.65),(1.08,1.38,0.68),'ac_paint',0.045)
        cylinder('HVAC fan',(xx,y,height+1.01),0.39,0.035,'darkmetal',vertices=28)
        for k in range(-3,4): cube('Fan guard',(xx+k*0.09,y,height+1.035),(0.025,0.68,0.025),'steel',0.003)
    if style%3==0:
        cylinder('Roof water tank',(x,y-1.6,height+1.13),0.68,1.55,'tank',vertices=28)
        for a in range(4):
            angle=a*math.pi/2+math.pi/4
            beam('Tank support',(x+0.55*math.cos(angle),y-1.6+0.55*math.sin(angle),height+0.1),(x+0.55*math.cos(angle),y-1.6+0.55*math.sin(angle),height+0.48),0.07,'steel')

def brick_apartment(side,y,height,variant):
    width=5.7; depth=7.45; x=side*(8.15+width/2)
    cube('Brick apartment shell',(x,y,height/2+0.12),(width,depth,height),'PBR_brick',0.035)
    front_box('Stone base',side,y,0.63,depth,1.08,0.18,'PBR_concrete',8.10,0.018)
    rows=max(2,int((height-2.0)/2.35))
    for row in range(rows):
        z=2.15+row*2.28
        for col in range(3): front_window(side,y-2.4+col*2.4,z,1.10,1.40,variant+row+col)
        front_box('Brick belt course',side,y,z+1.03,depth,0.13,0.16,'concrete_trim',8.04,0.012)
    for row in range(rows):
        for col in range(2): end_window(x+(col-0.5)*2.8,y+depth/2+0.015,2.15+row*2.28,1.05,1.35,row+col)
    for z in [3.0+i*2.28 for i in range(max(1,rows-1))]:
        front_box('Balcony slab',side,y+1.20,z-0.82,1.85,0.13,0.85,'concrete_trim',7.72,0.018)
        beam('Balcony top rail',(side*7.27,y+0.33,z-0.05),(side*7.27,y+2.07,z-0.05),0.055,'steel')
        for k in range(7): beam('Balcony baluster',(side*7.27,y+0.36+k*0.28,z-0.76),(side*7.27,y+0.36+k*0.28,z-0.05),0.032,'steel')
    aircon(side,y-2.40,3.50)
    front_box('Entry surround',side,y-0.10,1.15,1.40,2.15,0.20,'concrete_trim',7.99,0.025)
    front_box('Entry door',side,y-0.10,1.10,1.10,1.96,0.08,'door',7.86,0.02)
    rooftop(x,y,width,depth,height,variant)

def shop(side,y,height,variant):
    width=5.0; depth=7.45; x=side*(8.15+width/2)
    cube('Shop upper storeys',(x,y,height/2+0.12),(width,depth,height),'PBR_plaster' if variant%2 else 'PBR_concrete',0.035)
    front_box('Storefront surround',side,y,1.52,depth-0.20,2.85,0.22,'storefront',8.08,0.02)
    for col in range(4):
        yy=y-2.75+col*1.82
        front_box('Shop glazing',side,yy,1.47,1.60,2.38,0.04,'shop_glass',7.94,0.008)
        front_box('Shop vertical frame',side,yy-0.86,1.47,0.075,2.56,0.12,'frame',7.89,0.006)
        front_box('Shop lower panel',side,yy,0.36,1.63,0.34,0.10,'sign_teal',7.90,0.008)
    awning=front_box('Canvas shop awning',side,y,3.00,depth+0.10,0.13,1.35,'awning',7.50,0.025)
    awning.rotation_euler.y=side*math.radians(7)
    front_box('Awning valance',side,y,2.78,depth+0.10,0.32,0.10,'awning',6.87,0.015)
    facade_sign(side,y,3.65,['NORTHLINE','CORNER MARKET','PHARMACY','RADIO REPAIR'][variant%4],4.8,'sign_red' if variant%2 else 'sign_teal')
    rows=max(1,int((height-4.4)/2.25))
    for row in range(rows):
        for col in range(3): front_window(side,y-2.4+col*2.4,5.0+row*2.22,1.16,1.32,row+col+variant)
    for row in range(rows):
        for col in range(2): end_window(x+(col-0.5)*2.55,y+depth/2+0.02,5.0+row*2.22,1.08,1.3,row+col)
    aircon(side,y+2.35,5.85)
    rooftop(x,y,width,depth,height,variant+1)

def office(side,y,height,variant):
    width=6.1; depth=7.45; x=side*(8.15+width/2)
    cube('Office core',(x,y,height/2),(width,depth,height),'PBR_concrete',0.025)
    floors=max(3,int(height/2.45))
    for row in range(floors):
        z=1.30+row*2.42
        for col in range(4):
            yy=y-2.78+col*1.85
            front_box('Curtain wall glass',side,yy,z,1.69,2.20,0.055,'office_glass' if (row+col)%5 else 'glass_dark',8.11,0.005)
        front_box('Curtain wall spandrel',side,y,z-1.14,depth,0.17,0.13,'office_frame',8.04,0.006)
    for col in range(5): front_box('Vertical mullion',side,y-3.70+col*1.85,height/2,0.075,height,0.14,'office_frame',8.03,0.005)
    for row in range(floors):
        for col in range(3): end_window(x+(col-1)*1.75,y+depth/2+0.015,1.30+row*2.42,1.58,2.15,row+col)
    front_box('Lobby canopy',side,y,2.75,5.6,0.18,1.15,'office_frame',7.58,0.02)
    facade_sign(side,y,height-0.65,'NOVA  /  '+str(10+variant),3.6,'sign_teal')
    rooftop(x,y,width,depth,height,variant)

def warehouse(side,y,height,variant):
    width=6.7; depth=7.45; x=side*(8.15+width/2)
    cube('Warehouse shell',(x,y,height/2),(width,depth,height),'PBR_concrete',0.025)
    for yy in [y-depth/2+0.20+i*0.28 for i in range(26)]: front_box('Corrugated wall rib',side,yy,height/2,0.045,height-0.2,0.12,'warehouse_metal',8.10)
    for col in range(2):
        yy=y-1.85+col*3.7
        front_box('Loading door recess',side,yy,1.62,3.05,3.08,0.18,'recess',8.01,0.018)
        front_box('Roll up door',side,yy,1.58,2.78,2.86,0.06,'door_metal',7.90,0.008)
        for z in [0.30+i*0.25 for i in range(11)]: front_box('Roll up door slat',side,yy,z,2.74,0.028,0.03,'steel',7.85)
        front_box('Loading bumper',side,yy,0.33,3.25,0.25,0.75,'concrete_trim',7.70,0.02)
    facade_sign(side,y,height-0.9,'METRO  LOGISTICS',5.4,'sign_red')
    cylinder('Exhaust stack',(x,y,height+1.15),0.20,2.1,'steel',vertices=20)
    cylinder('Exhaust cap',(x,y,height+2.20),0.31,0.12,'darkmetal',vertices=20)
    rooftop(x,y,width,depth,height,variant)

def motel(side,y,height,variant):
    height=6.6; width=5.3; depth=7.45; x=side*(8.15+width/2)
    cube('Motel rooms',(x,y,height/2),(width,depth,height),'PBR_plaster',0.025)
    for level in range(2):
        z=1.35+level*3.05
        front_box('Exterior walkway',side,y,z-1.04,depth,0.18,1.22,'concrete_trim',7.63,0.025)
        beam('Walkway handrail',(side*7.03,y-depth/2,z-0.18),(side*7.03,y+depth/2,z-0.18),0.06,'steel')
        for k in range(14): beam('Walkway rail',(side*7.03,y-depth/2+k*depth/13,z-1.0),(side*7.03,y-depth/2+k*depth/13,z-0.18),0.035,'steel')
        for col in range(3):
            yy=y-2.40+col*2.40
            front_box('Motel door',side,yy-0.43,z,0.77,1.96,0.08,'door',8.03,0.015)
            front_window(side,yy+0.48,z+0.08,0.88,1.12,col+level)
    facade_sign(side,y,6.25,'SUNSET  MOTEL',5.1,'sign_red')
    rooftop(x,y,width,depth,height,variant)

def parking(side,y,height,variant):
    height=8.0; width=6.0; depth=7.45; x=side*(8.15+width/2)
    for level in range(4):
        z=0.25+level*2.40
        cube('Parking deck',(x,y,z),(width,depth,0.24),'PBR_concrete',0.02)
        front_box('Deck edge',side,y,z+0.55,depth,0.72,0.18,'concrete_trim',8.12,0.018)
        for yy in (y-3.35,y,y+3.35): front_box('Parking column',side,yy,z+1.12,0.30,2.20,0.35,'PBR_concrete',8.02,0.015)
        if level<3:
            for yy in (y-1.65,y+1.65):
                front_box('Parked car silhouette',side,yy,z+0.62,2.25,0.72,1.30,'car_paint',8.85,0.15)
    facade_sign(side,y,7.58,'P  /  PUBLIC',3.8,'sign_teal')
    rooftop(x,y,width,depth,height,variant)

BUILDERS=[brick_apartment,shop,office,warehouse,motel,parking]

def streetlight(side,y):
    cylinder('Lamp base',(side*5.03,y,0.27),0.21,0.42,'darkmetal')
    cylinder('Tapered lamp pole',(side*5.03,y,2.75),0.075,5.20,'steel')
    beam('Lamp arm',(side*5.03,y,5.24),(side*4.30,y,5.50),0.095,'steel')
    cube('LED street luminaire',(side*4.20,y,5.47),(0.62,0.30,0.14),'darkmetal',0.05)
    cube('LED diffuser',(side*4.20,y,5.385),(0.48,0.23,0.025),'lamp',0.02)

def car(side,y,color='car_paint'):
    x=side*5.73
    cube('Car lower body',(x,y,0.63),(1.72,4.05,0.68),color,0.16)
    cube('Car hood',(x,y-1.25,1.01),(1.68,1.32,0.20),color,0.10)
    cube('Car cabin',(x,y+0.25,1.30),(1.45,1.90,0.90),'glass_dark',0.18)
    cube('Car roof',(x,y+0.28,1.77),(1.42,1.62,0.12),color,0.07)
    for yy in (y-1.25,y+1.25):
        for xx in (x-0.86,x+0.86):
            cylinder('Car tire',(xx,yy,0.48),0.36,0.20,'rubber','X',24)
            cylinder('Car alloy wheel',(xx+(-0.11 if xx<x else 0.11),yy,0.48),0.22,0.025,'steel','X',20)
    for xx in (x-0.55,x+0.55): cube('Headlamp',(xx,y-2.045,0.79),(0.42,0.025,0.20),'lamp',0.035)
    cube('Front grille',(x,y-2.06,0.53),(0.86,0.025,0.19),'darkmetal',0.02)

def street_details(variant):
    if variant%2==0: streetlight(-1 if variant%4==0 else 1,-4.8)
    if variant%4==1: car(-1 if variant%2 else 1,1.7,'car_blue' if variant%3 else 'car_paint')
    if variant%3==1:
        x=6.15
        cube('Public rubbish bin',(x,-4.7,0.55),(0.60,0.60,0.95),'darkmetal',0.09)
        for k in range(6): cube('Bin vertical rib',(x-0.31,-4.94+k*0.095,0.55),(0.035,0.035,0.76),'steel',0.004)
        cube('News box',(-6.10,4.75,0.70),(0.62,0.55,1.18),'sign_red',0.07)
        cube('News box window',(-6.10,4.46,0.87),(0.47,0.025,0.48),'glass',0.02)
    if variant%4==2:
        for y in (-2.8,-1.6,-0.4):
            cube('Traffic cone base',(4.55,y,0.04),(0.40,0.40,0.08),'rubber',0.03)
            bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=0.16,radius2=0.035,depth=0.55,location=(4.55,y,0.34))
            assign(bpy.context.object,'cone')

def distant_massing(variant):
    # Secondary buildings stay off the road and give the skyline depth.
    for side in (-1,1):
        for j in range(2):
            width=random.uniform(5,8); depth=random.uniform(6,8); height=random.uniform(13,24)
            x=side*(17.5+j*7.0); y=-4+j*8
            cube('Distant city mass',(x,y,height/2),(width,depth,height),'distant_'+str((variant+j)%3),0.02)
            for row in range(int(height/2.8)):
                for col in range(3):
                    front_box('Distant window',side,y-2.1+col*2.1,1.7+row*2.7,0.85,1.15,0.03,'distant_window',abs(x)-side*0+width/2+0.02)

def join_meshes():
    groups={}
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':
            key=o.data.materials[0].name if o.data.materials else 'none'
            groups.setdefault(key,[]).append(o)
    for key,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects: o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        for o in objects:
            bpy.context.view_layer.objects.active=o
            for mod in list(o.modifiers):
                try: bpy.ops.object.modifier_apply(modifier=mod.name)
                except RuntimeError: pass
        if len(objects)>1:
            bpy.context.view_layer.objects.active=objects[0]
            bpy.ops.object.join()
        bpy.context.object.name='HD_'+key

args=__import__('sys').argv
variants=[int(v) for v in args[args.index('--')+1:]] if '--' in args else list(range(12))
for variant in variants:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    MATS.clear()
    material('PBR_asphalt','777777'); material('PBR_pavement','aaaaaa'); material('PBR_concrete','999999'); material('PBR_brick','aa8877'); material('PBR_plaster','b2a996')
    for name,color,rough,metal in [
        ('paint','d7d2b6',0.78,0),('gutter','3e4445',0.85,0),('darkmetal','232a2c',0.48,0.55),('steel','707a7c',0.34,0.7),
        ('recess','171e22',0.86,0),('glass','536e77',0.19,0.38),('glass_dark','243a43',0.24,0.30),('shop_glass','354f56',0.16,0.35),('office_glass','557887',0.17,0.48),
        ('frame','a69f8c',0.46,0.28),('office_frame','4c5c61',0.35,0.62),('concrete_trim','92958f',0.88,0),('blind','8a897d',0.85,0),('door','303e3e',0.65,0.1),
        ('ac_paint','a2a49c',0.55,0.28),('roof','3c4140',0.96,0),('tank','665f50',0.66,0.34),('storefront','323d3f',0.42,0.55),('awning','495d54',0.90,0),
        ('sign_teal','245e61',0.55,0.15),('sign_red','85473c',0.62,0.12),('lettering','e4dfc9',0.52,0),('warehouse_metal','65706c',0.63,0.35),('door_metal','555f5f',0.58,0.45),
        ('car_paint','70473d',0.36,0.48),('car_blue','3b5967',0.34,0.5),('rubber','171b1b',0.88,0),('lamp','e9e1bb',0.28,0.1),('cone','c76a32',0.72,0),
        ('distant_0','626d70',0.9,0),('distant_1','77756e',0.9,0),('distant_2','59666b',0.9,0),('distant_window','40545b',0.3,0.25)
    ]: material(name,color,rough,metal)
    road(variant)
    for side in (-1,1):
        for j,y in enumerate((-4.0,4.0)):
            builder=BUILDERS[(variant*2+j+(1 if side>0 else 0))%len(BUILDERS)]
            height=[10.8,8.2,14.6,6.0,6.6,8.0][BUILDERS.index(builder)]+(variant%3)*0.6
            builder(side,y,height,variant+j)
    street_details(variant)
    # Far massing is deliberately separated from the detailed street-facing buildings.
    for side in (-1,1):
        for j in range(2):
            h=14+((variant*3+j*5+(2 if side>0 else 0))%10)
            cube('Rear city silhouette',(side*(18+j*7),-4+j*8,h/2),(6.2,7.4,h),'distant_'+str((variant+j)%3),0.02)
    join_meshes()
    bpy.ops.object.select_all(action='SELECT')
    path=OUT/f'city_hd_{variant:02d}.glb'
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
    if variant==0: bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'streetscape_master.blend'))
    print('HD_CITY_EXPORTED',variant,'meshes',len([o for o in bpy.context.scene.objects if o.type=='MESH']))
print('HD_ENVIRONMENT_COMPLETE')
