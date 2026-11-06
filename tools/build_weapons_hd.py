import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'weapons'
PREVIEW=ROOT/'diagnostics'/'weapons_hd'
for p in (OUT,PREVIEW): p.mkdir(parents=True,exist_ok=True)

def material(name,color,metal=0.0,rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def finish(o,name,mat,edge=0.0):
    o.name=name; o.data.materials.append(mat)
    if edge:
        b=o.modifiers.new('Machined radii','BEVEL'); b.width=edge; b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,dims,mat,edge=0.008,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    return finish(o,name,mat,edge)

def profile(name,points,width,mat,edge=0.008,x=0):
    # Extrude a purposeful YZ silhouette; the muzzle points toward -Y.
    n=len(points)
    verts=[(x-width/2,y,z) for y,z in points]+[(x+width/2,y,z) for y,z in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o)
    return finish(o,name,mat,edge)

def cylinder(name,loc,radius,depth,mat,axis='Y',vertices=32,edge=0.003):
    rot={'Y':(math.pi/2,0,0),'X':(0,math.pi/2,0),'Z':(0,0,0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object
    for p in o.data.polygons: p.use_smooth=True
    return finish(o,name,mat,edge)

def tube(name,y,z,outer,inner,length,mat,x=0,vertices=40):
    verts=[]
    for yy,rr in ((y-length/2,outer),(y+length/2,outer),(y-length/2,inner),(y+length/2,inner)):
        for i in range(vertices):
            a=i*math.tau/vertices; verts.append((x+rr*math.cos(a),yy,z+rr*math.sin(a)))
    faces=[]
    for i in range(vertices):
        j=(i+1)%vertices
        faces.extend([(i,j,j+vertices,i+vertices),(i+2*vertices,i+3*vertices,j+3*vertices,j+2*vertices),(i,i+2*vertices,j+2*vertices,j),(i+vertices,j+vertices,j+3*vertices,i+3*vertices)])
    mesh=bpy.data.meshes.new(name+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o)
    for p in mesh.polygons: p.use_smooth=True
    return finish(o,name,mat,0.002)

def line(name,points,radius,mat):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'; curve.resolution_u=16; curve.bevel_depth=radius; curve.bevel_resolution=3
    spline=curve.splines.new('BEZIER'); spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o); o.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.convert(target='MESH')
    return bpy.context.object

def screw(x,y,z,mat,dark,side=1):
    cylinder('Torx fastener',(x,y,z),0.014,0.009,mat,'X',16,0.001)
    box('Fastener socket',(x+side*0.005,y,z),(0.003,0.012,0.003),dark,0.001)

def rail(y0,y1,z,mat,width=0.14):
    box('Rail spine',(0,(y0+y1)/2,z-0.012),(width,y1-y0,0.025),mat,0.003)
    count=max(2,int((y1-y0)/0.045))
    for i in range(count): box('Picatinny lug',(0,y0+i*(y1-y0)/(count-1),z+0.012),(width+0.025,0.025,0.025),mat,0.003)

def grip_texture(x,y,z,height,mat,side=1,rows=7):
    for i in range(rows):
        box('Grip checkering',(x,y,z-height/2+i*height/(rows-1)),(0.008,0.105,0.009),mat,0.002,rot=(0.08,0,0))

def mats():
    return {
        'steel':material('Gun / satin gunmetal',(0.055,0.066,0.075),0.78,0.32),
        'edge':material('Gun / brushed steel',(0.25,0.28,0.30),0.82,0.27),
        'black':material('Gun / black oxide',(0.014,0.018,0.021),0.50,0.42),
        'poly':material('Gun / textured polymer',(0.035,0.043,0.044),0.06,0.68),
        'rubber':material('Gun / soft rubber',(0.017,0.021,0.021),0.0,0.88),
        'wood':material('Gun / oiled walnut',(0.24,0.095,0.039),0.0,0.40),
        'brass':material('Gun / brass',(0.55,0.32,0.085),0.72,0.28),
        'glass':material('Gun / coated optic',(0.025,0.15,0.18),0.62,0.12),
        'red':material('Gun / fiber optic',(0.65,0.035,0.015),0.1,0.28),
    }

def pistol(m):
    profile('Slide sculpted', [(-0.36,0.105),(-0.355,0.17),(-0.31,0.20),(0.10,0.20),(0.15,0.155),(0.14,0.075),(-0.31,0.075)],0.145,m['steel'],0.012)
    profile('Frame ergonomic',[(-0.29,0.065),(0.13,0.065),(0.16,-0.035),(0.05,-0.09),(-0.15,-0.07),(-0.29,-0.015)],0.132,m['poly'],0.012)
    profile('Grip angled',[(0.015,-0.045),(0.16,-0.02),(0.205,-0.30),(0.16,-0.37),(0.035,-0.35),(-0.015,-0.14)],0.14,m['poly'],0.022)
    profile('Grip inset',[(0.045,-0.12),(0.145,-0.10),(0.17,-0.29),(0.13,-0.32),(0.055,-0.30)],0.148,m['rubber'],0.008)
    for side in (-1,1):
        for i in range(5): box('Slide serration',(side*0.075,0.045+i*0.018,0.14),(0.008,0.007,0.085),m['black'],0.001,rot=(0.15,0,0))
        grip_texture(side*0.077,0.11,-0.225,0.15,m['edge'],side,6)
    tube('Barrel crown',-0.358,0.137,0.033,0.019,0.07,m['edge'])
    cylinder('Dark bore',(0,-0.397,0.137),0.018,0.006,m['black'])
    line('Trigger guard',[(0,-0.17,-0.035),(0,-0.18,-0.16),(0,-0.08,-0.18),(0,0.005,-0.09)],0.013,m['poly'])
    line('Trigger blade',[(0,-0.065,-0.06),(0,-0.083,-0.12),(0,-0.055,-0.14)],0.009,m['edge'])
    box('Ejection port',(0.076,-0.08,0.17),(0.007,0.13,0.052),m['black'],0.004)
    box('Front sight',(0,-0.29,0.214),(0.026,0.044,0.027),m['black'],0.003)
    box('Front fiber',(0,-0.294,0.229),(0.010,0.020,0.008),m['red'],0.002)
    for x in (-0.045,0.045): box('Rear sight',(x,0.105,0.211),(0.032,0.037,0.030),m['black'],0.003)
    box('Magazine base',(0,0.105,-0.363),(0.16,0.18,0.035),m['black'],0.007)
    screw(0.077,0.06,-0.01,m['edge'],m['black'])

def smg(m):
    profile('Upper receiver',[(-0.31,0.02),(-0.33,0.16),(-0.25,0.22),(0.20,0.22),(0.29,0.15),(0.26,0.02)],0.19,m['steel'],0.018)
    profile('Lower receiver',[(-0.19,0.02),(0.25,0.02),(0.23,-0.12),(0.05,-0.18),(-0.17,-0.10)],0.17,m['poly'],0.016)
    profile('Vented handguard',[(-0.59,-0.015),(-0.62,0.13),(-0.54,0.18),(-0.27,0.17),(-0.26,-0.015)],0.20,m['poly'],0.024)
    for side in (-1,1):
        for i in range(4): box('Handguard vent',(side*0.102,-0.52+i*0.065,0.09),(0.008,0.040,0.050),m['black'],0.008)
        screw(side*0.102,-0.22,0.10,m['edge'],m['black'],side)
    tube('Barrel',-0.69,0.085,0.032,0.018,0.22,m['edge'])
    tube('Muzzle compensator',-0.83,0.085,0.052,0.021,0.12,m['steel'])
    for side in (-1,1):
        for y in (-0.855,-0.81): box('Muzzle port',(side*0.052,y,0.085),(0.008,0.022,0.040),m['black'],0.004)
    profile('Curved magazine',[(0.015,-0.12),(0.15,-0.12),(0.16,-0.34),(0.23,-0.52),(0.12,-0.55),(0.045,-0.37)],0.115,m['steel'],0.014)
    for z in (-0.23,-0.30,-0.37): box('Magazine rib',(0.061,0.10,z),(0.012,0.10,0.018),m['edge'],0.003)
    profile('Pistol grip',[(0.15,-0.09),(0.27,-0.06),(0.30,-0.32),(0.23,-0.38),(0.14,-0.33),(0.10,-0.18)],0.135,m['poly'],0.022)
    line('Trigger guard',[(0,-0.08,-0.06),(0,-0.10,-0.22),(0,0.055,-0.23),(0,0.12,-0.12)],0.014,m['poly'])
    line('Trigger',[(0,0.035,-0.08),(0,0.01,-0.15),(0,0.04,-0.18)],0.010,m['edge'])
    for x in (-0.065,0.065): line('Stock rod',[(x,0.23,0.13),(x,0.60,0.12)],0.023,m['edge'])
    profile('Stock shoulder pad',[(0.52,-0.04),(0.64,-0.04),(0.67,0.22),(0.54,0.24)],0.18,m['rubber'],0.025)
    profile('Vertical foregrip',[(-0.52,-0.02),(-0.38,-0.02),(-0.39,-0.29),(-0.48,-0.34),(-0.55,-0.29)],0.10,m['poly'],0.023)
    rail(-0.52,0.20,0.24,m['black'],0.13)
    box('Red dot base',(0,-0.04,0.29),(0.14,0.15,0.07),m['black'],0.008)
    tube('Red dot housing',-0.06,0.39,0.077,0.060,0.12,m['steel'])
    cylinder('Red dot lens',(0,-0.125,0.39),0.058,0.008,m['glass'])
    box('Charging handle',(0.14,0.12,0.18),(0.11,0.05,0.035),m['edge'],0.006)

def shotgun(m):
    profile('Forged receiver',[(-0.24,-0.04),(-0.27,0.13),(-0.18,0.18),(0.22,0.17),(0.28,0.07),(0.20,-0.09)],0.18,m['steel'],0.022)
    profile('Walnut stock',[(0.16,0.10),(0.31,0.13),(0.70,0.04),(0.76,-0.10),(0.65,-0.20),(0.46,-0.13),(0.25,-0.08)],0.17,m['wood'],0.035)
    profile('Recoil pad',[(0.68,-0.20),(0.79,-0.18),(0.82,0.04),(0.73,0.07)],0.19,m['rubber'],0.018)
    tube('Barrel',-0.71,0.10,0.037,0.023,0.94,m['edge'])
    tube('Magazine tube',-0.60,-0.015,0.035,0.022,0.68,m['steel'])
    profile('Pump walnut forend',[(-0.70,-0.095),(-0.73,0.07),(-0.66,0.12),(-0.39,0.11),(-0.34,0.03),(-0.38,-0.10)],0.19,m['wood'],0.035)
    for side in (-1,1):
        for i in range(7): box('Pump groove',(side*0.098,-0.67+i*0.043,0.005),(0.010,0.012,0.14),m['black'],0.003)
    box('Heat shield',(0,-0.59,0.145),(0.105,0.55,0.035),m['steel'],0.008)
    for side in (-1,1):
        for i in range(6): cylinder('Heat shield vent',(side*0.055,-0.79+i*0.083,0.145),0.018,0.008,m['black'],'X',16,0.001)
    line('Trigger guard',[(0,-0.06,-0.06),(0,-0.07,-0.22),(0,0.10,-0.23),(0,0.18,-0.10)],0.014,m['steel'])
    line('Trigger',[(0,0.055,-0.07),(0,0.025,-0.15),(0,0.055,-0.18)],0.010,m['edge'])
    box('Shell saddle',(0.115,0.04,0.035),(0.065,0.37,0.12),m['poly'],0.015)
    for y in (-0.09,0.015,0.12):
        cylinder('Shotgun shell',(0.148,y,0.04),0.024,0.105,m['brass'],'Y',20)
        cylinder('Shell hull',(0.148,y-0.056,0.04),0.023,0.055,m['red'],'Y',20)
    cylinder('Front bead',(0,-1.18,0.15),0.018,0.025,m['brass'],'Z',16)
    for y in (-0.14,0.14): screw(0.096,y,0.04,m['edge'],m['black'])

def sniper(m):
    profile('Precision receiver',[(-0.27,-0.04),(-0.29,0.13),(-0.20,0.19),(0.26,0.18),(0.31,0.08),(0.22,-0.09)],0.18,m['steel'],0.016)
    profile('Adjustable stock',[(0.16,0.10),(0.38,0.13),(0.78,0.05),(0.84,-0.17),(0.70,-0.25),(0.57,-0.12),(0.28,-0.09)],0.18,m['poly'],0.025)
    profile('Stock recoil pad',[(0.76,-0.24),(0.88,-0.22),(0.90,0.06),(0.80,0.08)],0.21,m['rubber'],0.022)
    profile('Cheek rest',[(0.25,0.16),(0.32,0.27),(0.68,0.24),(0.72,0.13)],0.17,m['poly'],0.023)
    profile('Long forestock',[(-0.78,-0.08),(-0.82,0.08),(-0.70,0.13),(-0.22,0.13),(-0.18,-0.07)],0.18,m['poly'],0.026)
    for side in (-1,1):
        for i in range(5): box('Forestock inset',(side*0.093,-0.68+i*0.10,-0.005),(0.010,0.065,0.055),m['black'],0.009)
    tube('Heavy free floated barrel',-1.02,0.075,0.036,0.020,0.60,m['edge'])
    tube('Muzzle brake',-1.37,0.075,0.062,0.023,0.16,m['steel'])
    for side in (-1,1):
        for y in (-1.41,-1.35): box('Brake side port',(side*0.063,y,0.075),(0.008,0.035,0.062),m['black'],0.006)
    profile('Box magazine',[(-0.10,-0.07),(0.08,-0.07),(0.10,-0.30),(-0.07,-0.32)],0.13,m['steel'],0.012)
    line('Trigger guard',[(0,0.07,-0.07),(0,0.06,-0.23),(0,0.20,-0.23),(0,0.26,-0.10)],0.013,m['steel'])
    line('Trigger',[(0,0.15,-0.08),(0,0.12,-0.16),(0,0.15,-0.19)],0.009,m['edge'])
    rail(-0.25,0.24,0.22,m['black'],0.13)
    for y in (-0.18,0.14):
        box('Scope mount',(0,y,0.27),(0.11,0.065,0.13),m['edge'],0.008)
        tube('Scope ring',y,0.39,0.073,0.058,0.06,m['black'])
    tube('Scope main tube',-0.02,0.39,0.056,0.043,0.48,m['steel'])
    tube('Scope objective',-0.30,0.39,0.092,0.073,0.16,m['steel'])
    cylinder('Objective lens',(0,-0.386,0.39),0.071,0.008,m['glass'])
    tube('Scope ocular',0.27,0.39,0.078,0.060,0.13,m['black'])
    cylinder('Ocular lens',(0,0.339,0.39),0.058,0.008,m['glass'])
    cylinder('Elevation turret',(0,-0.01,0.48),0.040,0.075,m['edge'],'Z',28)
    cylinder('Windage turret',(0.083,-0.01,0.39),0.035,0.06,m['edge'],'X',28)
    for i in range(16):
        a=i*math.tau/16
        box('Turret knurl',(0.040*math.cos(a),-0.01+0.040*math.sin(a),0.48),(0.012,0.012,0.055),m['black'],0.002)
    for side in (-1,1): line('Folded bipod',[(side*0.07,-0.63,-0.08),(side*0.12,-0.42,-0.16),(side*0.12,-0.17,-0.12)],0.018,m['steel'])

BUILDERS={'pistol':pistol,'smg':smg,'shotgun':shotgun,'sniper':sniper}

def preview(name):
    scene=bpy.context.scene
    world=bpy.data.worlds.new('Preview world'); world.use_nodes=True
    background=next(n for n in world.node_tree.nodes if n.bl_idname=='ShaderNodeBackground')
    background.inputs[0].default_value=(0.055,0.065,0.075,1)
    background.inputs[1].default_value=0.45; scene.world=world
    for loc,power,size in [((1.5,-1.5,3),700,3),((-2,-0.5,1.5),450,2),((0,2,2.2),550,2)]:
        bpy.ops.object.light_add(type='AREA',location=loc); light=bpy.context.object; light.data.energy=power; light.data.shape='DISK'; light.data.size=size
        light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(2.2,-2.4,1.65))
    camera=bpy.context.object; camera.rotation_euler=(Vector((0,-0.15,0))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'; camera.data.ortho_scale={'pistol':1.05,'smg':1.95,'shotgun':2.45,'sniper':2.75}[name]; scene.camera=camera
    scene.render.engine='CYCLES'; scene.cycles.samples=24
    scene.render.resolution_x=900; scene.render.resolution_y=600; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(PREVIEW/(name+'.png'))
    bpy.ops.render.render(write_still=True)

args=__import__('sys').argv
selected=args[args.index('--')+1:] if '--' in args else list(BUILDERS)
for name in selected:
    builder=BUILDERS[name]
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for data in list(bpy.data.materials): bpy.data.materials.remove(data)
    builder(mats())
    bpy.ops.object.select_all(action='SELECT')
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':
            bpy.context.view_layer.objects.active=o
            for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    print('HD_WEAPON_EXPORTED',name)
    preview(name)
print('HD_WEAPONS_COMPLETE')
