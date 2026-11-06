import bpy
import math
import random
import sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'environment'
SOURCE=ROOT/'assets'/'blender'/'environment'
for folder in (OUT,SOURCE): folder.mkdir(parents=True,exist_ok=True)
MATS={}


def linear(v):
    v=v/255
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4


def material(name,color,rough=.8,metal=0.0,emission=0.0):
    if name in MATS: return MATS[name]
    rgb=tuple(linear(c) for c in color) if not isinstance(color,str) else tuple(linear(int(color[i:i+2],16)) for i in (0,2,4))
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*rgb,1); p.inputs['Emission Strength'].default_value=emission
    MATS[name]=m
    return m


def assign(o,mat):
    o.data.materials.append(MATS[mat] if isinstance(mat,str) else mat)
    return o


WALL_MATERIALS={'wall_ivory','wall_gray','wall_sage','wall_blue','wall_sand',
                'wall_brick_red','wall_brick_tan','PBR_concrete','PBR_plaster','PBR_brick'}
# Muted colours commonly found on real masonry, concrete and painted city facades.
# A separate random choice is made for every building; there is no district colour cycle.
REALWALL_COLORS=['c8c5bb','b8b9b4','a9b0ae','d0c8b8','b9ad99','a99d8c',
                 '9aa6a8','899da2','a3aea6','929f96','b7b2a5','c2b59e',
                 '9a7567','87685e','a5826d','927d6c','b29982','a49c8e']


def recolor_building(before):
    color=random.choice(REALWALL_COLORS)
    mat=material('realwall_'+color,color,.93)
    for o in set(bpy.context.scene.objects)-before:
        if o.type!='MESH': continue
        for slot in o.material_slots:
            if not slot.material: continue
            key=slot.material.name.split('.',1)[0]
            if key in WALL_MATERIALS or key.startswith('distant_') and key!='distant_window':
                slot.material=mat
    return mat


def age_building(side,y,height,variant,wall_mat):
    # Small, opaque wear marks avoid transparent decal shimmer in the mobile renderer.
    base=wall_mat.diffuse_color
    stain=material('weathered_'+wall_mat.name,tuple(max(0,min(255,round(((c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4)*255)*.82))) for c in base[:3]),.98)
    rng=random.Random(8100+variant*73+(1 if side>0 else 0))
    facade_x=WINDOW_POSITIONS[0][4] if WINDOW_POSITIONS else 8.04
    for i in range(1+round(ACTIVE_DAMAGE*3)):
        yy=y+rng.uniform(-2.6,2.6); top=rng.uniform(2.1,max(2.2,height-.8)); length=rng.uniform(.35,.85)
        w=rng.uniform(.035,.075); x=side*(facade_x-.008)
        verts=[(x,yy-w,top),(x,yy+w,top),(x,yy+w*.55,top-length*.70),(x,yy+w*.15,top-length),(x,yy-w*.45,top-length*.76)]
        data=bpy.data.meshes.new('Rain stain mesh'); data.from_pydata(verts,[],[(0,1,2,3,4)]); data.update()
        o=bpy.data.objects.new('Faded rainwater streak',data); bpy.context.collection.objects.link(o); assign(o,stain)
    if rng.random()<ACTIVE_DAMAGE*.72:
        front_box('Ground floor rising damp',side,y,.48,4.2,.18,.012,stain,facade_x-.012,.0)
        # Hairline structural cracks cluster in rundown districts.
        for k in range(1+int(ACTIVE_DAMAGE*2)):
            yy=y+rng.uniform(-2.2,2.2); zz=rng.uniform(2.0,max(2.2,height-1.0))
            beam('Facade settlement crack',(side*(facade_x-.018),yy,zz),(side*(facade_x-.018),yy+.18,zz-.55),.022,'road_crack')
            beam('Facade settlement crack',(side*(facade_x-.018),yy+.18,zz-.55),(side*(facade_x-.018),yy-.08,zz-.92),.016,'road_crack')
    if rng.random()<ACTIVE_DAMAGE*.45:
        yy=y+rng.uniform(-1.8,1.8); zz=rng.uniform(1.2,max(1.3,height-.8)); x=side*(facade_x-.022)
        verts=[(x,yy-.52,zz-.35),(x,yy+.34,zz-.43),(x,yy+.51,zz+.18),(x,yy+.13,zz+.58),(x,yy-.43,zz+.32)]
        data=bpy.data.meshes.new('Exposed masonry scar mesh'); data.from_pydata(verts,[],[(0,1,2,3,4)]); data.update()
        o=bpy.data.objects.new('Broken plaster exposing old brick',data); bpy.context.collection.objects.link(o); assign(o,'exposed_brick')
    if rng.random()<ACTIVE_DAMAGE*.22:
        # A small, dark dried smear at one entrance; not another street-wide oil decal.
        yy=y-1.9; x=side*(facade_x-.028)
        verts=[(x,yy-.25,.25),(x,yy+.30,.25),(x,yy+.21,.82),(x,yy+.05,1.12),(x,yy-.13,.76)]
        data=bpy.data.meshes.new('Dried facade blood mesh'); data.from_pydata(verts,[],[(0,1,2,3,4)]); data.update()
        o=bpy.data.objects.new('Dried blood at abandoned entrance',data); bpy.context.collection.objects.link(o); assign(o,'old_blood')


def bevel(o,width=.02,segments=2):
    if width<=0: return
    mod=o.modifiers.new('Soft construction edges','BEVEL'); mod.width=width; mod.segments=segments
    o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')


def cube(name,loc,dims,mat,edge=0.0,rot=None):
    # Direct mesh construction avoids two dependency-graph operator calls per part.
    x,y,z=(d*.5 for d in dims)
    verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    mesh.uv_layers.new(name='UVMap')
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.location=loc
    if rot: o.rotation_euler=rot
    assign(o,mat); bevel(o,edge)
    if name in {'Masonry apartment volume','Mixed use shop volume','Narrow townhouse volume','Modern apartment main volume','Stepped deco main volume'}:
        global ACTIVE_WALL,WINDOW_CUTTERS,WINDOW_POSITIONS
        ACTIVE_WALL=o; WINDOW_CUTTERS=[]; WINDOW_POSITIONS=[]
    return o


def cylinder(name,loc,radius,depth,mat,axis='Z',vertices=24):
    rotation={'Z':(0,0,0),'Y':(math.pi/2,0,0),'X':(0,math.pi/2,0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rotation)
    o=bpy.context.object; o.name=name; assign(o,mat); bevel(o,.006,2)
    for p in o.data.polygons: p.use_smooth=True
    return o


def beam(name,a,b,width,mat):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,width,(b-a).length),mat,.004)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o


def uv_world(o,scale=3.0):
    uv=o.data.uv_layers.active
    if not uv: return
    for poly in o.data.polygons:
        n=poly.normal
        for li in poly.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            if abs(n.z)>.5: uv.data[li].uv=(co.x/scale,co.y/scale)
            elif abs(n.x)>.5: uv.data[li].uv=(co.y/scale,co.z/scale)
            else: uv.data[li].uv=(co.x/scale,co.z/scale)


def front_box(name,side,y,z,width,height,depth,mat,x=8.04,edge=0.0):
    return cube(name,(side*x,y,z),(depth,width,height),mat,edge)


def end_box(name,x,y,z,width,height,depth,mat,edge=0.0):
    return cube(name,(x,y,z),(width,depth,height),mat,edge)


ACTIVE_WALL=None
WINDOW_CUTTERS=[]
WINDOW_POSITIONS=[]
ACTIVE_DAMAGE=.12


def wall_volume(name,loc,dims,mat):
    global ACTIVE_WALL,WINDOW_CUTTERS
    ACTIVE_WALL=cube(name,loc,dims,mat,.018); WINDOW_CUTTERS=[]
    return ACTIVE_WALL


def cut_window_openings():
    global ACTIVE_WALL,WINDOW_CUTTERS
    if ACTIVE_WALL is None or not WINDOW_CUTTERS:
        ACTIVE_WALL=None; WINDOW_CUTTERS=[]; return
    wall=ACTIVE_WALL
    bpy.ops.object.select_all(action='DESELECT'); wall.select_set(True); bpy.context.view_layer.objects.active=wall
    for mod in list(wall.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action='DESELECT')
    for cutter in WINDOW_CUTTERS: cutter.select_set(True)
    bpy.context.view_layer.objects.active=WINDOW_CUTTERS[0]; bpy.ops.object.join()
    cutter=bpy.context.object
    bpy.ops.object.select_all(action='DESELECT'); wall.select_set(True); bpy.context.view_layer.objects.active=wall
    mod=wall.modifiers.new('True recessed street window openings','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True); bevel(wall,.008,2)
    ACTIVE_WALL=None; WINDOW_CUTTERS=[]


def front_window(side,y,z,w=1.05,h=1.35,style=0,x=8.04):
    global WINDOW_POSITIONS
    if ACTIVE_WALL is not None:
        if not WINDOW_CUTTERS: WINDOW_POSITIONS=[]
        WINDOW_POSITIONS.append((y,z,w,h,x))
        WINDOW_CUTTERS.append(cube('Temporary street window cutter',(side*(x+.17),y,z),(.65,w+.06,h+.06),'recess'))
    # Damage belongs to individual openings, not an identical decal repeated on every facade.
    damage_rng=random.Random(round((y+40)*173+(z+2)*719+(x+2)*1231+(side+1)*97))
    roll=damage_rng.random()
    missing=ACTIVE_DAMAGE*.16; broken=ACTIVE_DAMAGE*.40; boarded=ACTIVE_DAMAGE*.88
    state='missing' if roll<missing else ('broken' if roll<broken else ('boarded' if roll<boarded else 'intact'))
    if state=='intact':
        front_box('Recessed window glazing',side,y,z,w,h,.028,'glass_dark' if style%4==0 else 'glass',x+.13,.004)
    else:
        front_box('Dark room beyond damaged window',side,y,z,w,h,.025,'window_void',x+.25)
    if state=='broken':
        # A few thick triangular glass teeth remain around the reveal; the centre is open.
        for k in range(5):
            yy=y-w*.46+k*w*.23
            zz=z-h/2
            tip=zz+damage_rng.uniform(.16,.42)
            verts=[(side*(x+.12),yy,zz),(side*(x+.12),yy+w*.18,zz),(side*(x+.12),yy+w*.07,tip)]
            data=bpy.data.meshes.new('Broken glazing tooth mesh'); data.from_pydata(verts,[],[(0,1,2)]); data.update()
            o=bpy.data.objects.new('Jagged remaining window glass',data); bpy.context.collection.objects.link(o); assign(o,'glass')
    if state=='boarded':
        for k in range(3):
            plank=front_box('Emergency boarded window plank',side,y,z-h*.30+k*h*.30,w+.22,.17,.065,'wood_panel',x-.045,.008)
            plank.rotation_euler.x=damage_rng.uniform(-.10,.10)
        beam('Diagonal window barricade',(side*(x-.10),y-w*.43,z-h*.40),(side*(x-.10),y+w*.43,z+h*.40),.105,'wood_panel')
    for yy in (y-w/2-.015,y+w/2+.015):
        front_box('Window inner side reveal',side,yy,z,.05,h,.30,'recess',x+.07,.003)
        front_box('Slim window vertical casing',side,yy,z,.065,h+.12,.09,'frame',x+.015,.004)
    for zz in (z-h/2-.015,z+h/2+.015):
        front_box('Window inner horizontal reveal',side,y,zz,w,.05,.30,'recess',x+.07,.003)
        front_box('Slim window horizontal casing',side,y,zz,w+.12,.065,.09,'frame',x+.015,.004)
    if style%3!=2 and state!='missing':
        front_box('Recessed window centre mullion',side,y,z,.035,h,.065,'frame',x+.07,.003)
    front_box('Slim stone sill',side,y,z-h/2-.10,w+.22,.09,.20,'trim',x+.01,.009)
    if style%7==0 and state=='intact':
        for dz in (-.28,-.14,0,.14,.28):
            front_box('Interior blind slat',side,y,z+dz,w*.90,.025,.02,'blind',x+.18)


def end_window(x,y,z,w=1.0,h=1.25,style=0):
    end_box('End wall window reveal',x,y,z,w+.16,h+.16,.10,'recess',.01)
    end_box('End wall glazing',x,y+.06,z,w,h,.025,'glass_dark' if style%3==0 else 'glass',.006)
    for xx in (x-w/2-.035,x+w/2+.035): end_box('End window jamb',xx,y+.10,z,.065,h+.13,.09,'frame',.004)
    for zz in (z-h/2-.035,z+h/2+.035): end_box('End window rail',x,y+.10,zz,w+.13,.065,.09,'frame',.004)


def lettering(side,y,z,text,width=3.4,color='sign_teal',x=7.78):
    front_box('Sign metal surround',side,y,z,width,.62,.18,'darkmetal',x,.025)
    front_box('Sign enamel face',side,y,z,width-.10,.49,.035,color,x-.12,.012)
    bpy.ops.object.text_add(location=(side*(x-.155),y,z),rotation=(math.pi/2,0,-side*math.pi/2))
    o=bpy.context.object; o.name='Architectural lettering'; o.data.body=text
    o.data.align_x='CENTER'; o.data.align_y='CENTER'; o.data.size=.25 if len(text)>13 else .29; o.data.extrude=.003
    assign(o,'lettering'); bpy.ops.object.convert(target='MESH')


def aircon(side,y,z,x=7.73):
    front_box('Air conditioner cabinet',side,y,z,.72,.48,.38,'ac_paint',x,.028)
    front_box('Air conditioner grille',side,y,z,.55,.32,.025,'darkmetal',x-.22,.008)
    for k in range(6): front_box('Air conditioner louvre',side,y,z-.13+k*.052,.50,.016,.018,'steel',x-.24)
    for yy in (y-.25,y+.25): beam('Air conditioner bracket',(side*(x+.25),yy,z-.31),(side*(x-.18),yy,z-.31),.035,'steel')


def roof(x,y,width,depth,height,style):
    cube('Flat roof membrane',(x,y,height+.02),(width,depth,.10),'roof',.012)
    for xx in (x-width/2,x+width/2): cube('Side roof parapet',(xx,y,height+.27),(.14,depth,.50),'trim',.014)
    for yy in (y-depth/2,y+depth/2): cube('End roof parapet',(x,yy,height+.27),(width,.14,.50),'trim',.014)
    if style%4!=1:
        xx=x+(.35 if style%2 else -.45)
        cube('Roof HVAC curb',(xx,y,height+.19),(1.10,1.35,.22),'darkmetal',.018)
        cube('Roof HVAC cabinet',(xx,y,height+.56),(.98,1.22,.58),'ac_paint',.035)
        cylinder('Roof fan housing',(xx,y,height+.88),.34,.035,'darkmetal',vertices=32)
        for k in range(-3,4): cube('Roof fan guard',(xx+k*.075,y,height+.905),(.018,.58,.018),'steel',.002)
    if style%5==0:
        cylinder('Roof water tank',(x,y-1.2,height+1.10),.58,1.35,'tank',vertices=32)
        for a in range(4):
            angle=a*math.pi/2+math.pi/4
            beam('Tank support',(x+.45*math.cos(angle),y-1.2+.45*math.sin(angle),height+.08),(x+.45*math.cos(angle),y-1.2+.45*math.sin(angle),height+.47),.055,'steel')


def drainpipe(side,y,height,x=7.96):
    cylinder('Facade rainwater downpipe',(side*x,y,height/2),.035,height,'darkmetal',vertices=12)
    for z in [1.0+i*2.2 for i in range(max(1,int(height/2.2)))]:
        front_box('Downpipe wall clamp',side,y,z,.13,.045,.10,'steel',x+.01)


def apartment(side,y,height,variant,depth):
    width=5.3+(variant%3)*.35; x=side*(8.15+width/2)
    wall=['wall_brick_red','wall_brick_tan','wall_sage','wall_ivory'][variant%4]
    cube('Masonry apartment volume',(x,y,height/2+.12),(width,depth,height),wall,.028)
    front_box('Apartment stone plinth',side,y,.58,depth,1.02,.16,'trim',8.09,.015)
    rows=max(2,int((height-1.7)/2.25)); cols=3 if depth>6.3 else 2
    bay=depth/cols
    for row in range(rows):
        z=2.05+row*2.22
        for col in range(cols): front_window(side,y-depth/2+bay*(col+.5),z,min(1.12,bay*.48),1.36,variant+row+col)
        front_box('Apartment floor stringcourse',side,y,z+1.0,depth,.12,.15,'trim',8.06,.009)
    for row in range(rows):
        for col in range(2): end_window(x+(col-.5)*width*.45,y+depth/2+.015,2.05+row*2.22,1.0,1.30,row+col)
    if variant%2==0:
        for row in range(1,rows):
            z=1.25+row*2.22; yy=y+depth*.19
            front_box('Cantilever balcony',side,yy,z,1.75,.14,.92,'trim',7.66,.016)
            beam('Balcony handrail',(side*7.18,yy-.82,z+.78),(side*7.18,yy+.82,z+.78),.045,'steel')
            for k in range(7): beam('Balcony vertical rail',(side*7.18,yy-.78+k*.26,z+.08),(side*7.18,yy-.78+k*.26,z+.78),.026,'steel')
    front_box('Recessed apartment entrance',side,y-depth*.23,1.12,1.30,2.12,.20,'recess',8.02,.018)
    front_box('Apartment entrance door',side,y-depth*.23,1.08,1.04,1.96,.08,'door',7.89,.015)
    for k in range(3): front_box('Entrance stone step',side,y-depth*.23,.17+k*.09,1.52,.10,.40+k*.24,'trim',7.66-k*.10,.012)
    aircon(side,y+depth*.30,3.45)
    drainpipe(side,y+depth/2-.12,height)
    roof(x,y,width,depth,height,variant)


def shop(side,y,height,variant,depth):
    width=4.9+(variant%2)*.45; x=side*(8.15+width/2)
    wall=['wall_ivory','wall_gray','wall_brick_tan','wall_blue'][variant%4]
    cube('Mixed use shop volume',(x,y,height/2+.12),(width,depth,height),wall,.026)
    front_box('Shopfront surround',side,y,1.48,depth-.18,2.78,.22,'storefront',8.07,.018)
    cols=4 if depth>6.3 else 3; bay=(depth-.42)/cols
    for col in range(cols):
        yy=y-depth/2+.21+bay*(col+.5)
        front_box('Shop display glass',side,yy,1.43,bay-.17,2.28,.045,'shop_glass',7.93,.006)
        front_box('Shopfront mullion',side,yy-bay/2,1.43,.065,2.42,.12,'frame',7.88,.005)
        front_box('Shop stall riser',side,yy,.32,bay-.12,.30,.12,'sign_teal' if variant%2 else 'sign_red',7.87,.006)
    if random.Random(4000+variant).random()<ACTIVE_DAMAGE*.78:
        boarded_y=y-depth*.22
        front_box('Abandoned shop dark doorway',side,boarded_y,1.35,min(1.65,bay),2.35,.04,'window_void',7.85)
        for k in range(4):
            plank=front_box('Boarded shop entrance plank',side,boarded_y,.62+k*.47,min(1.85,bay+.2),.18,.065,'wood_panel',7.76,.008)
            plank.rotation_euler.x=.06*(-1 if k%2 else 1)
    awning=front_box('Deep canvas awning',side,y,2.94,depth+.05,.13,1.30,'awning_green' if variant%3 else 'awning_rust',7.49,.018)
    awning.rotation_euler.y=side*math.radians(7)
    front_box('Awning hanging valance',side,y,2.72,depth+.05,.28,.09,'awning_green' if variant%3 else 'awning_rust',6.88,.012)
    names=['NORTHLINE','CORNER MARKET','PHARMACY','RADIO REPAIR','LAUNDRY','CORNER CAFE','HARDWARE','BOOKS & RECORDS']
    lettering(side,y,3.58,names[variant%len(names)],min(depth-.3,5.0),'sign_red' if variant%2 else 'sign_teal')
    rows=max(1,int((height-4.2)/2.2)); cols=3 if depth>6.3 else 2; bay=depth/cols
    for row in range(rows):
        for col in range(cols): front_window(side,y-depth/2+bay*(col+.5),4.85+row*2.18,1.08,1.30,row+col+variant)
    drainpipe(side,y-depth/2+.13,height)
    roof(x,y,width,depth,height,variant+1)


def townhouse(side,y,height,variant,depth):
    width=4.15; x=side*(8.32+width/2)
    wall=['wall_brick_red','wall_brick_tan','wall_sage','wall_blue'][variant%4]
    cube('Narrow townhouse volume',(x,y,height/2+.12),(width,depth,height),wall,.025)
    front_box('Townhouse raised basement',side,y,.70,depth,1.25,.18,'trim',8.25,.016)
    rows=max(2,int((height-1.4)/2.35)); cols=2
    for row in range(rows):
        z=2.0+row*2.30
        for col in range(cols): front_window(side,y-depth*.24+col*depth*.48,z,1.04,1.48,variant+row+col,8.20)
    for z in [1.18+i*2.3 for i in range(rows)]: front_box('Townhouse floor cornice',side,y,z,depth+.08,.14,.22,'trim',8.18,.012)
    front_box('Townhouse front door',side,y-depth*.24,1.05,.92,1.94,.10,'door',8.04,.016)
    for k in range(5): front_box('Townhouse stoop step',side,y-depth*.24,.18+k*.11,1.30,.13,.40+k*.24,'trim',7.91-k*.10,.012)
    if variant%2==1:
        for row in range(1,rows):
            z=1.15+row*2.30; yy=y+depth*.19
            front_box('Fire escape landing',side,yy,z,1.55,.08,.72,'darkmetal',7.83,.006)
            for k in range(7): beam('Fire escape railing',(side*7.45,yy-.70+k*.23,z),(side*7.45,yy-.70+k*.23,z+.70),.022,'steel')
            beam('Fire escape top rail',(side*7.45,yy-.74,z+.70),(side*7.45,yy+.74,z+.70),.035,'steel')
            beam('Fire escape stair stringer',(side*7.48,yy-.64,z),(side*7.48,yy+.64,z-1.65),.045,'steel')
    front_box('Townhouse crown cornice',side,y,height-.05,depth+.25,.28,.42,'trim',8.14,.022)
    drainpipe(side,y+depth/2-.10,height,8.12)
    roof(x,y,width,depth,height,variant)


def modern_apartment(side,y,height,variant,depth):
    width=5.6; x=side*(8.22+width/2)
    cube('Modern apartment main volume',(x,y,height/2),(width,depth,height),'wall_ivory' if variant%2 else 'wall_gray',.022)
    rows=max(3,int(height/2.45)); cols=3 if depth>6.3 else 2; bay=depth/cols
    for row in range(rows):
        z=1.35+row*2.40
        front_box('Modern floor band',side,y,z-1.08,depth,.18,.20,'modern_panel',8.12,.008)
        for col in range(cols):
            yy=y-depth/2+bay*(col+.5)
            front_window(side,yy,z,min(1.35,bay*.62),1.65,variant+row+col,8.12)
        if row>0 and variant%3!=1:
            yy=y+depth*.22
            front_box('Recessed balcony slab',side,yy,z-.86,depth*.42,.13,.92,'trim',7.70,.012)
            front_box('Balcony frosted screen',side,yy,z-.35,depth*.40,.78,.035,'glass',7.23,.008)
    front_box('Full height timber accent',side,y-depth*.38,height/2,.34,height,.18,'wood_panel',8.00,.008)
    front_box('Modern entry canopy',side,y,2.60,3.40,.16,1.20,'modern_panel',7.55,.018)
    roof(x,y,width,depth,height,variant)


def office(side,y,height,variant,depth):
    width=6.0; x=side*(8.18+width/2)
    cube('Office core',(x,y,height/2),(width,depth,height),'wall_gray',.022)
    floors=max(3,int(height/2.42)); cols=4 if depth>6.3 else 3; bay=depth/cols
    for row in range(floors):
        z=1.30+row*2.40
        for col in range(cols):
            yy=y-depth/2+bay*(col+.5)
            front_box('Office glazed bay',side,yy,z,bay-.14,2.16,.055,'office_glass' if (row+col)%5 else 'glass_dark',8.12,.004)
        front_box('Office horizontal spandrel',side,y,z-1.13,depth,.16,.14,'office_frame',8.05,.005)
    for col in range(cols+1):
        yy=y-depth/2+col*bay
        front_box('Office vertical mullion',side,yy,height/2,.065,height,.15,'office_frame',8.03,.004)
    front_box('Office lobby canopy',side,y,2.68,min(5.2,depth),.18,1.15,'office_frame',7.57,.015)
    lettering(side,y,height-.62,['NOVA','MERIDIAN','CIVIC','ATLAS'][variant%4],3.2,'sign_teal')
    roof(x,y,width,depth,height,variant)


def deco(side,y,height,variant,depth):
    width=5.5; x=side*(8.25+width/2)
    cube('Stepped deco main volume',(x,y,height/2),(width,depth,height),'wall_sand',.025)
    cols=3 if depth>6.3 else 2; bay=depth/cols; rows=max(3,int(height/2.55))
    for col in range(cols):
        yy=y-depth/2+bay*(col+.5)
        front_box('Deco vertical pier',side,yy-bay/2,height/2,.18,height,.28,'trim',8.05,.012)
        for row in range(rows): front_window(side,yy,1.45+row*2.48,min(1.05,bay*.48),1.70,variant+row+col,8.13)
    cube('Deco stepped crown',(x,y,height+.65),(width*.78,depth*.88,1.25),'wall_sand',.025)
    cube('Deco upper crown',(x,y,height+1.48),(width*.52,depth*.68,.52),'trim',.018)
    front_box('Deco entry surround',side,y,1.45,2.20,2.80,.30,'trim',8.03,.022)
    front_box('Deco entry doors',side,y,1.28,1.55,2.35,.08,'door',7.84,.012)
    lettering(side,y,3.20,'HOTEL  '+['GRAND','CENTRAL','ROYAL'][variant%3],min(4.5,depth-.3),'sign_red')


def warehouse(side,y,height,variant,depth):
    width=6.5; x=side*(8.22+width/2)
    cube('Industrial warehouse volume',(x,y,height/2),(width,depth,height),'wall_gray',.022)
    ribs=max(12,int(depth/.29))
    for k in range(ribs):
        yy=y-depth/2+.16+k*(depth-.32)/(ribs-1)
        front_box('Warehouse corrugated rib',side,yy,height/2,.04,height-.18,.12,'warehouse_metal',8.11)
    for col in range(2):
        yy=y-depth*.25+col*depth*.50
        front_box('Loading door reveal',side,yy,1.55,min(2.75,depth*.42),2.95,.18,'recess',8.02,.015)
        front_box('Loading roller door',side,yy,1.51,min(2.55,depth*.40),2.75,.06,'door_metal',7.90,.006)
        for k in range(10): front_box('Roller door slat',side,yy,.30+k*.26,min(2.48,depth*.39),.025,.03,'steel',7.85)
        front_box('Loading dock bumper',side,yy,.30,min(2.9,depth*.45),.22,.68,'trim',7.67,.016)
    lettering(side,y,height-.75,['METRO LOGISTICS','NORTH DEPOT','CITY STORAGE'][variant%3],min(5.0,depth-.2),'sign_red')
    cylinder('Warehouse exhaust stack',(x,y,height+1.0),.18,1.85,'steel',vertices=24)
    roof(x,y,width,depth,height,variant)


def parking(side,y,height,variant,depth):
    height=7.8; width=5.8; x=side*(8.22+width/2)
    for level in range(4):
        z=.25+level*2.35
        cube('Parking concrete deck',(x,y,z),(width,depth,.22),'wall_gray',.016)
        front_box('Parking deck edge',side,y,z+.51,depth,.62,.16,'trim',8.12,.012)
        for yy in (y-depth*.42,y,y+depth*.42): front_box('Parking structural column',side,yy,z+1.05,.28,2.05,.34,'wall_gray',8.02,.012)
        if level<3:
            for yy in (y-depth*.23,y+depth*.23): front_box('Parked vehicle silhouette',side,yy,z+.58,2.10,.66,1.22,'car_blue' if level%2 else 'car_paint',8.77,.12)
    lettering(side,y,7.40,'P  /  PUBLIC',3.6,'sign_teal')
    roof(x,y,width,depth,height,variant)


def low_rise(side,y,height,variant,depth):
    height=min(height,7.2); width=4.7+(variant%2)*.55; x=side*(8.32+width/2)
    cube('Narrow townhouse volume',(x,y,height/2+.12),(width,depth,height),'wall_brick_tan' if variant%2 else 'wall_ivory',.025)
    front_box('Low rise stone base',side,y,.42,depth,.68,.15,'trim',8.25,.012)
    cols=2; rows=2 if height>5.6 else 1
    for row in range(rows):
        for col in range(cols): front_window(side,y-depth*.24+col*depth*.48,1.65+row*2.25,1.02,1.30,variant+row+col,8.20)
    front_box('Low rise entrance',side,y-depth*.24,1.02,.94,1.92,.11,'door',8.06,.014)
    front_box('Low rise porch roof',side,y-depth*.24,2.20,1.75,.13,.92,'awning_green',7.78,.015)
    # A pitched roof gives the residential blocks a genuinely different silhouette.
    roof_z=height+.15; ridge=height+1.12
    verts=[(x-width/2-.16,y-depth/2-.16,roof_z),(x+width/2+.16,y-depth/2-.16,roof_z),(x,y-depth/2-.16,ridge),
           (x-width/2-.16,y+depth/2+.16,roof_z),(x+width/2+.16,y+depth/2+.16,roof_z),(x,y+depth/2+.16,ridge)]
    data=bpy.data.meshes.new('Low rise pitched roof mesh'); data.from_pydata(verts,[],[(0,2,5,3),(2,1,4,5),(0,1,2),(3,5,4)]); data.update()
    o=bpy.data.objects.new('Low rise pitched roof',data); bpy.context.collection.objects.link(o); assign(o,'roof')
    drainpipe(side,y+depth/2-.10,height,8.12)


def tower(side,y,height,variant,depth):
    height=max(height,19.0); width=6.25; x=side*(8.22+width/2)
    cube('Tower street podium',(x,y,1.65),(width+.35,depth,3.3),'wall_gray',.025)
    cube('Modern apartment main volume',(x,y,(height+3.3)/2),(width,depth,height-3.3),'wall_gray' if variant%2 else 'wall_blue',.022)
    rows=max(5,int((height-4.1)/2.60)); cols=3 if depth>6.3 else 2; bay=depth/cols
    for row in range(rows):
        z=4.55+row*2.55
        if z+1.0>height: continue
        for col in range(cols):
            yy=y-depth/2+bay*(col+.5)
            front_window(side,yy,z,min(1.32,bay*.60),1.72,variant+row+col,8.12)
        front_box('Tower horizontal floor band',side,y,z-1.05,depth,.14,.20,'modern_panel',8.08,.006)
    for yy in (y-depth*.49,y,y+depth*.49): front_box('Tower full height pier',side,yy,(height+3.3)/2,.16,height-3.3,.26,'trim',8.04,.008)
    # A stepped crown and mechanical penthouse keep the towers from reading as stretched boxes.
    cube('Tower setback crown',(x+side*.34,y,height+.55),(width*.76,depth*.86,1.10),'modern_panel',.025)
    cube('Tower roof lantern',(x+side*.45,y,height+1.55),(width*.46,depth*.54,.95),'wall_gray',.020)
    front_box('Tower lobby glazing',side,y,1.55,depth-.50,2.65,.05,'shop_glass',7.98,.006)
    front_box('Tower entry canopy',side,y,2.92,min(4.8,depth),.18,1.30,'office_frame',7.48,.018)
    lettering(side,y,3.55,['MERIDIAN','NORTH TOWER','CIVIC PLAZA'][variant%3],min(4.6,depth-.3),'sign_teal')


BUILDERS=[apartment,shop,townhouse,modern_apartment,office,deco,warehouse,parking,low_rise,tower]
DISTRICTS=[
    [low_rise,shop,low_rise,townhouse,apartment,low_rise],
    [tower,office,deco,tower,modern_apartment,office],
    [townhouse,low_rise,apartment,shop,modern_apartment,apartment],
    [warehouse,low_rise,shop,warehouse,parking,apartment],
    [tower,modern_apartment,tower,office,deco,tower],
    [low_rise,shop,apartment,townhouse,low_rise,modern_apartment],
]
BASE_HEIGHT={apartment:10.8,shop:8.3,townhouse:8.8,modern_apartment:12.2,office:14.4,deco:13.0,warehouse:5.8,parking:7.8,low_rise:5.6,tower:22.0}


def road_wear(variant):
    # Damage is sparse and authored per block: no repeated crack on every street.
    rng=random.Random(9200+variant)
    road_crack_points=[]
    def crack(name,points,width):
        verts=[]; faces=[]
        for i,p in enumerate(points):
            direction=points[min(i+1,len(points)-1)]-points[max(0,i-1)]
            lateral=Vector((-direction.y,direction.x,0)).normalized()*width*rng.uniform(.65,1.35)
            verts.extend([p-lateral,p+lateral])
            if i: faces.append((2*i-2,2*i-1,2*i+1,2*i))
        data=bpy.data.meshes.new(name+' mesh'); data.from_pydata(verts,[],faces); data.update()
        o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); assign(o,'road_crack')
    if rng.random()<.10+ACTIVE_DAMAGE*.82:
        x=rng.uniform(-2.9,2.9); y=rng.uniform(-5.8,3.8); angle=rng.uniform(-.75,.75)
        points=[Vector((x,y,.003))]
        for segment in range(rng.randint(6,10)):
            angle+=rng.uniform(-.48,.48); step=rng.uniform(.22,.43)
            x=max(-3.35,min(3.35,x+math.sin(angle)*step)); y+=math.cos(angle)*step
            points.append(Vector((x,y,.003)))
        crack('Irregular asphalt fracture',points,rng.uniform(.014,.026)); road_crack_points.append(points[len(points)//2])
        if rng.random()<ACTIVE_DAMAGE*.60:
            origin=points[len(points)//2]; branch=[origin]
            for k in range(4): branch.append(branch[-1]+Vector((rng.uniform(.13,.26),rng.uniform(-.15,.17),0)))
            crack('Branched asphalt hairline',branch,.010)
    if rng.random()<ACTIVE_DAMAGE*.68 and variant%6!=5:
        side=-1 if variant%8<4 else 1; y=rng.uniform(-4.8,4.8); z=.154
        points=[Vector((side*4.62,y,z))]
        for k in range(7):
            x=side*(4.62+k*.39); y+=rng.uniform(-.19,.19)
            points.append(Vector((x,y,z)))
        crack('Irregular pavement slab fracture',points,rng.uniform(.012,.022))
    centers=[]
    if rng.random()<.18+ACTIVE_DAMAGE*.72:
        side=-1 if variant%4==0 else 1
        centers.append(Vector((side*rng.uniform(3.82,3.96),rng.choice((-6.7,6.5))+rng.uniform(-.25,.25),.004)))
    if rng.random()<ACTIVE_DAMAGE*.55 and road_crack_points:
        p=road_crack_points[0]; centers.append(Vector((p.x,p.y,.006)))
    for center in centers:
        verts=[]; faces=[]; tones=[]
        for blade in range(9):
            angle=rng.uniform(0,math.tau); height=rng.uniform(.11,.28); width=rng.uniform(.009,.017)
            offset=Vector((rng.uniform(-.055,.055),rng.uniform(-.055,.055),0))
            lateral=Vector((math.cos(angle)*width,math.sin(angle)*width,0))
            bend=Vector((math.sin(angle)*height*.32,-math.cos(angle)*height*.32,0))
            base=center+offset; mid=base+Vector((0,0,height*.58))+bend*.35; tip=base+Vector((0,0,height))+bend
            n=len(verts); verts.extend([base-lateral,base+lateral,mid-lateral*.65,mid+lateral*.65,tip])
            faces.extend([(n,n+1,n+3,n+2),(n+2,n+3,n+4)]); tones.extend([rng.randrange(2)]*2)
        data=bpy.data.meshes.new('Crack weed blades mesh'); data.from_pydata(verts,[],faces); data.update()
        o=bpy.data.objects.new('Sparse weeds in street fracture',data); bpy.context.collection.objects.link(o); assign(o,'weed_dark'); assign(o,'weed_dry')
        for poly,tone in zip(data.polygons,tones): poly.material_index=tone


def missile_crater_road():
    # One coherent blast site in the industrial disaster district, with a real concave road mesh.
    # Compact enough that both rims stay reachable: it blocks a lane, not the whole street.
    nx=48; ny=72; verts=[]; faces=[]; center=Vector((-.65,.25,0)); radius=1.70
    for j in range(ny+1):
        y=-8+16*j/ny
        for i in range(nx+1):
            x=-4.175+8.35*i/nx; dx=x-center.x; dy=y-center.y; d=math.hypot(dx,dy)
            a=math.atan2(dy,dx); edge=radius*(1+.055*math.sin(a*7)+.035*math.sin(a*11))
            z=0.0
            if d<edge:
                t=d/edge; z=-.76*max(0,1-t*t)**.72
                if t>.80: z+=.075*math.sin((t-.80)/.20*math.pi)
            verts.append((x,y,z))
    for j in range(ny):
        for i in range(nx):
            n=j*(nx+1)+i; faces.append((n,n+1,n+nx+2,n+nx+1))
    data=bpy.data.meshes.new('Concave missile crater road mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new('Missile crater concave asphalt',data); bpy.context.collection.objects.link(o); assign(o,'PBR_asphalt'); assign(o,'crater_earth')
    for poly in data.polygons:
        c=poly.center; d=math.hypot(c.x-center.x,c.y-center.y)
        if d<radius*.72: poly.material_index=1
    uv_world(o,3.2)
    for k in range(13):
        a=k*math.tau/13; r=radius*(1+.05*math.sin(a*7))
        x=center.x+math.cos(a)*r; y=center.y+math.sin(a)*r
        cube('Crater rim broken asphalt',(x,y,.030),(.30+.09*(k%3),.44,.10),'PBR_asphalt',.016,rot=(.10*math.sin(a),.12*math.cos(a),a))


# Cross streets come in real-world widths: a narrow side alley, an equal-width
# crossing, a mid-width street and one wide boulevard with open plaza corners.
CROSS_DEPTH={5:5.2,11:8.35,17:11.6,23:7.0}

# Zebra crossings vary per junction instead of blanketing all four arms: each
# intersection variant paints a different mix of avenue arms (first tuple,
# -1/+1 = south/north of the box) and cross-street arms (second tuple).
ZEBRA_ARMS={5:((-1,),(1,)),11:((-1,1),()),17:((1,),(-1,1)),23:((),(-1,))}


def lane_arrow(x,y):
    # Straight-ahead lane arrow: shaft plus triangular head, pointing along +Y
    # (the survivor's running direction once the district is in Godot).
    cube('Lane arrow shaft',(x,y-.55,.0012),(.24,1.35,.0024),'paint')
    verts=[(x-.62,y+.18,.0012),(x+.62,y+.18,.0012),(x,y+.95,.0012),
           (x-.62,y+.18,.0032),(x+.62,y+.18,.0032),(x,y+.95,.0032)]
    faces=[(0,2,1),(3,4,5),(0,1,4),(0,4,3),(1,2,5),(1,5,4),(2,0,3),(2,3,5)]
    data=bpy.data.meshes.new('Lane arrow head mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new('Lane arrow head',data); bpy.context.collection.objects.link(o); assign(o,'paint')


def road(variant):
    intersection=variant%6==5
    if variant==14: missile_crater_road()
    else:
        o=cube('Main avenue asphalt',(0,0,-.13),(8.35,16,.26),'PBR_asphalt'); uv_world(o,4.0)
    if intersection:
        # Pavement, kerbs and edge lines all yield to the real width of the cross street.
        half=CROSS_DEPTH.get(variant,4.15)/2.0
        seg=8.0-half
        spans=[(-(half+seg/2),seg),(half+seg/2,seg)]
    else:
        spans=[(0,16)]
    for side in (-1,1):
        for yy,length in spans:
            walk=cube('Segmented city pavement',(side*6.12,yy,.04),(3.45,length,.22),'PBR_pavement',.012); uv_world(walk,2.4)
            missing_side=1
            if not intersection and variant==15 and side==missing_side:
                # Only two districts lose a continuous patch of about four slabs.
                cutter=cube('Temporary missing pavement patch',(side*5.62,-1.15,.10),(1.55,1.42,.52),'recess')
                bpy.ops.object.select_all(action='DESELECT'); walk.select_set(True); bpy.context.view_layer.objects.active=walk
                mod=walk.modifiers.new('Missing continuous pavement patch','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
                bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cutter,do_unlink=True)
                cube('Missing pavement patch substrate',(side*5.62,-1.15,-.015),(1.55,1.42,.035),'road_crack')
                cube('Broken pavement edge shard',(side*5.10,-.38,.18),(.42,.25,.075),'curb',.012,rot=(.04,-.03,.12))
                cube('Broken pavement edge shard',(side*6.18,-1.91,.17),(.36,.24,.06),'curb',.010,rot=(-.03,.04,-.12))
            cube('Kerb stone',(side*4.20,yy,.10),(.32,length,.32),'curb',.022)
            cube('Avenue edge line',(side*3.73,yy,.008),(.10,length,.012),'paint',.003)
        for yy in (-5.8,5.8):
            cube('Storm drain inset',(side*3.94,yy,.015),(.28,.64,.025),'darkmetal',.005)
            for k in range(7): cube('Storm drain slot',(side*3.94,yy-.25+k*.083,.032),(.22,.022,.012),'steel')
    if intersection:
        # Keep the crossing 10 mm below the avenue: identical coplanar tops caused
        # severe z-fighting whenever the moving camera approached an intersection.
        d=CROSS_DEPTH.get(variant,4.15); half=d/2.0
        cross=cube('Cross street asphalt',(0,0,-.125),(62,d,.23),'PBR_asphalt'); uv_world(cross,4.0)
        # Kerbs and full pavements follow the cross street, so the corners read as
        # paved sidewalk instead of bare ground.
        for yy in (-half-.13,half+.13):
            for side in (-1,1): cube('Cross street kerb',(side*18,yy,.08),(27,.25,.28),'curb',.018)
        for yy in (-half-1.98,half+1.98):
            for side in (-1,1):
                walk=cube('Cross street pavement',(side*18,yy,.04),(27,3.45,.22),'PBR_pavement',.012); uv_world(walk,2.4)
        # The box itself stays clear of paint; the approaches get a wide, bright
        # zebra straight across the avenue, then the centre dashes resume. The
        # zebra is as deep as the arm allows, tight against the crossing box.
        # Zebra arms vary per intersection (ZEBRA_ARMS) so junctions no longer
        # show the same four-crossing layout every time.
        zlen=min(4.8,8.0-half-.30)
        zebra_avenue,zebra_cross=ZEBRA_ARMS.get(variant,((-1,1),(-1,1)))
        for arm in (-1,1):
            if arm in zebra_avenue:
                for k in range(8):
                    cube('Intersection zebra paint',(-3.22+k*.92,arm*(half+.15+zlen/2),.0012),(.60,zlen,.0024),'zebra_paint')
            alen=8.0-(half+zlen+.60)
            if alen>1.8:
                cube('Avenue centre dash',(0,arm*(half+zlen+.60+alen/2),.011),(.13,alen,.015),'paint',.004)
        # The cross street is a real road too: edge lines plus its own centre dashes
        # (doubled on the boulevard crossing), kept clear of the avenue box.
        dash_y=(-.30,.30) if d>=10.0 else (0.0,)
        for yy in dash_y:
            for side in (-1,1):
                for k in range(4):
                    cube('Cross street centre dash',(side*(8.6+k*5.4),yy,.001),(2.9,.13,.012),'paint',.003)
        for yy in (-half+.45,half-.45):
            for side in (-1,1): cube('Cross street edge line',(side*17.5,yy,.001),(25.4,.10,.012),'paint',.003)
        # Zebras across the cross street too, on the arms this junction uses.
        nb=max(3,int((d-1.4)/.92))
        for k in range(nb):
            yy=-(nb-1)*.46+k*.92
            for side in (-1,1):
                if side in zebra_cross:
                    cube('Cross street zebra paint',(side*6.90,yy,.0012),(4.60,.60,.0024),'zebra_paint')
    else:
        # Mid-block zebras on three of the 24 blocks; the game hides most of them at
        # runtime (CITY_zebra_paint node) so crossings stay rare and random.
        if variant in (2,9,16):
            crossing_y={2:-2.2,9:2.5,16:-1.0}[variant]
            for k in range(8):
                cube('Occasional zebra crossing paint',(-3.22+k*.92,crossing_y,.0012),(.60,5.0,.0024),'zebra_paint')
        if variant==14:
            cube('Avenue centre dash',(0,-6,.011),(.13,4.8,.015),'paint',.004)
            cube('Broken centre line beyond crater',(0,5.8,.011),(.13,2.6,.015),'paint',.004)
        else:
            # Dashes stay inside the block so the rhythm survives tiling: 4.8 m paint,
            # 3.2 m gap, no half-dash spilling into the neighbouring district.
            for yy in (-5.6,2.4): cube('Avenue centre dash',(0,yy,.011),(.13,4.8,.015),'paint',.004)
        # Straight-ahead lane arrows on a few through blocks, one per lane.
        if variant in (4,8,20):
            for x in (-1.85,1.85): lane_arrow(x,-3.2)
    if variant%5==0 and not intersection:
        side=1 if variant%10==0 else -1; x=side*5.45
        cylinder('Sidewalk utility cover',(x,4.9,.160),.32,.018,'darkmetal',vertices=48)
        for k in range(-3,4): cube('Utility cover rib',(x+k*.065,4.9,.173),(.018,.44,.012),'steel',.002)
    road_wear(variant)


def streetlight(side,y):
    cylinder('Streetlight footing',(side*5.03,y,.27),.19,.42,'darkmetal')
    cylinder('Streetlight tapered pole',(side*5.03,y,2.75),.068,5.20,'steel')
    beam('Streetlight arm',(side*5.03,y,5.24),(side*4.30,y,5.50),.085,'steel')
    cube('Streetlight housing',(side*4.20,y,5.47),(.62,.30,.14),'darkmetal',.045)
    cube('Streetlight diffuser',(side*4.20,y,5.385),(.48,.23,.025),'lamp',.018)


def traffic_signal(side,y):
    # Full-size municipal mast arm: bolted footing, tapered shaft and curved elbow.
    pole_x=side*4.65
    cube('Signal concrete plinth',(pole_x,y,.19),(.48,.48,.32),'curb',.045)
    cube('Signal base plate',(pole_x,y,.365),(.36,.36,.045),'steel',.012)
    for dx in (-.135,.135):
        for dy in (-.135,.135):
            cylinder('Signal anchor bolt',(pole_x+dx,y+dy,.402),.025,.034,'darkmetal',vertices=12)
    cylinder('Signal mast lower',(pole_x,y,1.60),.082,2.45,'darkmetal',vertices=32)
    cylinder('Signal mast upper',(pole_x,y,3.20),.065,1.05,'darkmetal',vertices=32)
    cylinder('Signal mast collar',(pole_x,y,2.68),.093,.12,'steel',vertices=32)
    # Rounded steel elbow, rather than a square beam.
    curve=bpy.data.curves.new('Signal swept mast arm','CURVE'); curve.dimensions='3D'; curve.resolution_u=12
    curve.bevel_depth=.066; curve.bevel_resolution=4; curve.resolution_u=16
    spline=curve.splines.new('BEZIER'); spline.bezier_points.add(3)
    points=[(pole_x,y,3.64),(pole_x,y,4.35),(side*4.25,y,4.56),(side*2.98,y,4.56)]
    for bp,co in zip(spline.bezier_points,points):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    arm=bpy.data.objects.new('Signal swept mast arm',curve); bpy.context.collection.objects.link(arm); assign(arm,'darkmetal')
    for xx in (side*4.45,side*3.25):
        cylinder('Signal arm coupling',(xx,y,4.56),.082,.15,'steel','X',32)

    # Die-cast three-aspect head with separate back shell, face frame and gaskets.
    x=side*2.98; front=y-.188
    cylinder('Signal hanger',(x,y,4.37),.040,.31,'steel',vertices=24)
    cube('Signal hanger clevis',(x,y,4.25),(.20,.17,.12),'steel',.018)
    cube('Signal rounded rear shell',(x,y+.035,3.77),(.40,.32,1.13),'signal_yellow',.065)
    cube('Signal black face gasket',(x,y-.139,3.77),(.365,.038,1.055),'rubber',.045)
    cube('Signal recessed face',(x,y-.164,3.77),(.325,.024,1.01),'darkmetal',.036)
    for z,mat in ((4.09,'signal_red'),(3.77,'signal_off'),(3.45,'signal_green')):
        cylinder('Signal lens retaining ring',(x,front-.010,z),.135,.048,'darkmetal','Y',48)
        cylinder('Signal prismatic lens',(x,front-.039,z),.105,.020,mat,'Y',48)
        cylinder('Signal lens inner optic',(x,front-.052,z),.078,.009,mat,'Y',48)
        # Open half-cylinder sun visor. Its front lip and inner wall remain visible.
        verts=[]; faces=[]; seg=24
        for yy in (front-.066,front-.265):
            for r in (.133,.148):
                for i in range(seg+1):
                    a=math.pi*i/seg
                    verts.append((x+r*math.cos(a),yy,z+r*math.sin(a)))
        n=seg+1
        for i in range(seg):
            faces.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),
                          (i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
        faces.extend([(0,n,3*n,2*n),(seg,2*n-1,4*n-1,3*n-1)])
        mesh=bpy.data.meshes.new('Signal visor mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
        visor=bpy.data.objects.new('Signal deep sun visor',mesh); bpy.context.collection.objects.link(visor); assign(visor,'darkmetal')
        bevel(visor,.003,2)
        for dx in (-.156,.156):
            cylinder('Signal face screw',(x+dx,y-.190,z),.012,.010,'steel','Y',12)
    # Rear service door and hinges keep the prop convincing from street level.
    cube('Signal rear service panel',(x,y+.205,3.77),(.28,.022,.88),'signal_yellow',.025)
    for z in (3.47,4.07): cube('Signal service hinge',(x-.15,y+.218,z),(.045,.034,.12),'steel',.006)
    cube('Signal identification plate',(x,y+.222,3.75),(.15,.010,.10),'steel',.004)

    # Pedestrian request station with a protected metal button and instruction plate.
    cube('Pedestrian push button box',(pole_x,y-.055,1.10),(.19,.17,.29),'signal_yellow',.030)
    cube('Pedestrian button face',(pole_x,y-.149,1.10),(.145,.020,.23),'darkmetal',.018)
    cylinder('Pedestrian metal push button',(pole_x,y-.171,1.065),.041,.025,'steel','Y',32)
    cube('Pedestrian instruction plaque',(pole_x,y-.171,1.165),(.105,.009,.055),'lettering',.004)
    for z in (.94,1.28): cylinder('Pedestrian enclosure screw',(pole_x,y-.165,z),.010,.012,'steel','Y',12)


def street_name(side,y,variant):
    cylinder('Street sign pole',(side*4.72,y,1.55),.04,2.95,'steel',vertices=16)
    cube('Avenue street blade',(side*4.72,y,2.92),(1.32,.08,.28),'sign_teal',.025)
    cube('Cross street blade',(side*4.72,y,2.63),(.08,1.15,.25),'sign_teal',.025)


def place_street_asset(name,loc,yaw=0.0,scale=1.0):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(OUT.parent/'props'/(name+'.glb')))
    imported=set(bpy.context.scene.objects)-before
    parent=bpy.data.objects.new(name+' placement',None); bpy.context.collection.objects.link(parent)
    for o in imported:
        if o.parent is None or o.parent not in imported: o.parent=parent
    parent.location=loc; parent.rotation_euler.z=yaw; parent.scale=(scale,scale,scale)


def bus_stop(side,y):
    place_street_asset('bus_stop',(side*6.22,y,.12),0.0 if side>0 else math.pi)


def street_tree(side,y,variant):
    # Different species and ages, but every square pit remains aligned with the kerb.
    selector=(variant+(1 if side>0 else 0))%5
    name='pine_tree' if selector==1 else ('sapling' if selector==3 else 'street_tree')
    scale=(.90 if name=='pine_tree' else 1.0) if name!='street_tree' else .92+.06*((variant+(1 if side>0 else 0))%3)
    place_street_asset(name,(side*6.18,y,.025),0.0,scale)


def car(side,y,color):
    x=side*5.72
    cube('Parked car lower body',(x,y,.62),(1.70,4.0,.66),color,.15)
    cube('Parked car bonnet',(x,y-1.24,.99),(1.65,1.28,.20),color,.09)
    cube('Parked car cabin',(x,y+.25,1.28),(1.43,1.88,.88),'glass_dark',.17)
    cube('Parked car roof',(x,y+.28,1.74),(1.40,1.58,.12),color,.06)
    for yy in (y-1.23,y+1.23):
        for xx in (x-.85,x+.85):
            cylinder('Parked car tyre',(xx,yy,.46),.35,.19,'rubber','X',28)
            cylinder('Parked car wheel',(xx+(-.105 if xx<x else .105),yy,.46),.21,.025,'steel','X',24)


def street_details(variant):
    if variant%6==5:
        # Signals and street name signs stand on the crossing corners, whatever its width.
        cy=CROSS_DEPTH.get(variant,4.15)/2.0+.75
        traffic_signal(-1,-cy); traffic_signal(1,cy)
        street_name(-1,-cy+.30,variant); street_name(1,cy-.30,variant)
    else:
        if variant%2==0: streetlight(-1 if variant%4==0 else 1,-4.8)
        # Shelters alternate between the two pavements and sit clear of the lamps.
        if variant%8==2: bus_stop(1,0.0)
        elif variant%8==6: bus_stop(-1,0.0)
        # Never place a parked car inside the left-hand shelter on variant 6.
        parked=variant%5==1 and variant%8!=6
        if parked: car(-1,1.7,'car_blue' if variant%3 else 'car_paint')
        # Two-sided planting is normal, but large gaps and occasional one-sided blocks break repetition.
        # Across six blocks: two planted on both sides, one single-sided, two bare, one intersection.
        block_phase=variant%6
        tree_sides=[]
        if block_phase in (0,3): tree_sides=[-1,1]
        elif block_phase==1: tree_sides=[-1 if (variant//4)%2==0 else 1]
        for side in tree_sides:
            tree_y={0:-3.8,1:4.8,3:3.6}[block_phase]
            if side<0 and parked and abs(tree_y-1.7)<3.0: tree_y=5.4
            street_tree(side,tree_y,variant)
        if variant%4==1:
            side=1 if (variant//4)%2==0 else -1
            place_street_asset('flowerbed',(side*7.12,-4.45,.15),0.0,1.0)
        if variant%3==0:
            side=-1 if variant%2==0 else 1
            cube('Occasional windblown paper',(side*4.72,.5,.165),(.18,.25,.003),'lettering',rot=(0,0,variant*.73))
        if variant%7==3:
            cylinder('Fire hydrant body',(-5.0,2.8,.45),.12,.58,'hydrant',vertices=24)
            cylinder('Fire hydrant cap',(-5.0,2.8,.77),.16,.10,'hydrant',vertices=24)
            cylinder('Fire hydrant side outlet',(-5.0,2.8,.53),.09,.35,'hydrant','X',20)


def background(variant):
    for side in (-1,1):
        for j in range(2):
            width=5.4+((variant+j)%3)*.65; depth=6.6+(variant%2)*.6
            group=variant//4
            if group in (1,4): h=22+((variant*3+j*5+(2 if side>0 else 0))%18)
            elif group in (0,5): h=7+((variant*3+j*5+(2 if side>0 else 0))%7)
            else: h=11+((variant*3+j*5+(2 if side>0 else 0))%12)
            x=side*(18.2+j*7.1); y=-4+j*8
            before=set(bpy.context.scene.objects)
            cube('Background city building',(x,y,h/2),(width,depth,h),'distant_'+str((variant+j)%4),.018)
            if j==0:
                cols=3; rows=int(h/2.85)
                for row in range(rows):
                    for col in range(cols):
                        yy=y-depth*.32+col*depth*.32
                        front_box('Background window',side,yy,1.7+row*2.75,.75,1.05,.035,'distant_window',abs(x)-width/2-.03)
            recolor_building(before)


def join_meshes():
    # Convert every selected object in one depsgraph operation. This preserves all
    # bevels/normals and is far faster than hundreds of context-dependent applies.
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active=bpy.context.scene.objects[0]
    bpy.ops.object.convert(target='MESH')
    groups={}
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':
            key=o.data.materials[0].name if o.data.materials else 'none'
            groups.setdefault(key,[]).append(o)
    for key,objects in groups.items():
        if len(objects)>1:
            bpy.ops.object.select_all(action='DESELECT')
            for o in objects: o.select_set(True)
            bpy.context.view_layer.objects.active=objects[0]; bpy.ops.object.join()
            bpy.context.object.name='CITY_'+key
        else:
            # Single-object group: rename the object itself. Renaming bpy.context.object
            # here would stomp the previously joined group (it stays the active object).
            objects[0].name='CITY_'+key


def make_materials():
    material('PBR_asphalt','777777'); material('PBR_pavement','aaaaaa')
    palette=[
        ('paint','b7b8ab',.94,0),('zebra_paint','d3d4c8',.90,0),('road_paint','767b73',.98,0),('curb','a5a8a3',.92,0),('darkmetal','252d30',.48,.55),('steel','707b7d',.35,.70),
        ('recess','192125',.88,0),('glass','59727a',.22,.30),('glass_dark','293e47',.25,.28),('shop_glass','39545b',.18,.30),('office_glass','587b88',.18,.42),
        ('frame','b3b0a4',.48,.22),('office_frame','4c5c61',.35,.60),('trim','a8aaa3',.88,0),('blind','919188',.85,0),('door','344342',.65,.10),
        ('ac_paint','a5a79f',.56,.25),('roof','414746',.96,0),('tank','6a675b',.67,.30),('storefront','354244',.44,.50),
        ('awning_green','50685e',.90,0),('awning_rust','8b5b4b',.90,0),('wood_panel','75614b',.78,0),('modern_panel','68777a',.55,.30),
        ('sign_teal','286166',.55,.12),('sign_red','875044',.62,.10),('lettering','e3e1d4',.52,0),('warehouse_metal','6b7570',.64,.32),('door_metal','596361',.58,.42),
        ('wall_ivory','c4c1b6',.92,0),('wall_gray','9ca6a5',.92,0),('wall_sage','8c9b8d',.92,0),('wall_blue','849aa3',.92,0),
        ('wall_sand','b8ab91',.92,0),('wall_brick_red','906557',.94,0),('wall_brick_tan','a38a73',.94,0),
        ('car_paint','765047',.38,.42),('car_blue','426473',.36,.45),('rubber','1b2020',.88,0),('lamp','e8e3ca',.30,.05),
        ('signal_yellow','a89148',.52,.20),('signal_red','a32e25',.28,.10),('signal_green','2d7355',.28,.10),('signal_off','26332e',.55,.10),('hydrant','9a493c',.60,.20),
        ('road_crack','45433e',1.0,0),('weed_dark','485043',.98,0),('weed_dry','706b4f',.98,0),
        ('window_void','11191b',.98,0),('exposed_brick','705044',.97,0),('old_blood','4d1718',.96,0),('crater_earth','38372f',.99,0),
        ('distant_0','697578',.92,0),('distant_1','82847c',.92,0),('distant_2','647177',.92,0),('distant_3','8a8176',.92,0),('distant_window','455c64',.32,.20)
    ]
    for name,color,rough,metal in palette: material(name,color,rough,metal)


random.seed(20261105) # reproducible export, but independent building-by-building choices
args=sys.argv
variants=[int(v) for v in args[args.index('--')+1:]] if '--' in args else list(range(24))
for variant in variants:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials):
        for block in list(blocks):
            if block.users==0: blocks.remove(block)
    MATS.clear(); make_materials()
    ACTIVE_DAMAGE=[.10,.20,.42,.78,.34,.58][variant//4]
    road(variant)
    intersection=variant%6==5
    if intersection:
        # Corner buildings yield to the cross street: the wider the crossing, the
        # shallower the plots; the boulevard junction leaves open plaza corners.
        half=CROSS_DEPTH.get(variant,4.15)/2.0
        depth=min(5.65,7.9-half-.30)
        centres=(-(half+.15+depth/2),(half+.15+depth/2)) if depth>=2.2 else ()
        if depth<2.2: depth=2.2
    else:
        depth=7.30
        centres=(-4.0,4.0)
    district=DISTRICTS[(variant//4)%len(DISTRICTS)]
    for side in (-1,1):
        for j,y in enumerate(centres):
            builder=district[(variant+j*2+(1 if side>0 else 0))%len(district)]
            group=variant//4; step=(variant*3+j*2+(1 if side>0 else 0))%5
            if builder==tower:
                height=21.0+step*2.45
            elif group in (1,4) and builder in (office,modern_apartment,deco):
                height=BASE_HEIGHT[builder]+4.0+step*1.85
            elif group in (0,5):
                low_base={low_rise:5.2,shop:5.6,townhouse:6.4,apartment:8.0,modern_apartment:10.0}
                height=low_base.get(builder,BASE_HEIGHT[builder])+(step%3)*.62
            elif group==3 and builder in (warehouse,shop,low_rise):
                height={warehouse:4.9,shop:6.2,low_rise:5.4}[builder]+(step%3)*.50
            else:
                height=BASE_HEIGHT[builder]+step*.95
            before=set(bpy.context.scene.objects)
            builder(side,y,height,variant+j+(1 if side>0 else 0),depth)
            cut_window_openings()
            wall_mat=recolor_building(before)
            age_building(side,y,height,variant+j+(1 if side>0 else 0),wall_mat)
            setback=[0.0,.28,.62,.15,.82,.40][(variant+j+(1 if side>0 else 0))%6]
            if intersection: setback+=.22
            for o in set(bpy.context.scene.objects)-before: o.location.x+=side*setback
    street_details(variant); background(variant); join_meshes()
    bpy.ops.object.select_all(action='SELECT')
    path=OUT/f'city_hd_{variant:02d}.glb'
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
    if variant%6==0:
        bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/f'district_{variant//4:02d}_master.blend'))
    print('CITY_DISTRICT_EXPORTED',variant,'objects',len(bpy.context.scene.objects))
print('CITY_DISTRICTS_COMPLETE',len(variants))
