import bpy
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'weapons'; OUT.mkdir(parents=True,exist_ok=True)

def material(name,color,metal=0.0,rough=0.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def box(name,loc,dims,mat,bevel=0.012,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Bevel','BEVEL'); b.width=bevel; b.segments=3
    return o

def cyl(name,loc,radius,depth,mat,axis='Y',vertices=24):
    rot=(math.pi/2,0,0) if axis=='Y' else ((0,math.pi/2,0) if axis=='X' else (0,0,0))
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat)
    b=o.modifiers.new('Bevel','BEVEL'); b.width=0.006; b.segments=2
    return o

def rail(start,end,z,mat):
    count=max(2,int((end-start)/0.07))
    for i in range(count): box('RailTooth',(0,start+i*(end-start)/(count-1),z),(0.13,0.032,0.025),mat,0.004)

def base_materials():
    return {
        'steel':material('Blued steel',(0.035,0.045,0.055),0.75),
        'edge':material('Edge steel',(0.23,0.26,0.27),0.72),
        'poly':material('Black polymer',(0.045,0.052,0.050),0.08,0.65),
        'wood':material('Walnut',(0.25,0.105,0.045),0.0,0.52),
        'brass':material('Brass',(0.55,0.34,0.09),0.65),
        'glass':material('Scope glass',(0.035,0.15,0.18),0.35,0.15),
    }

def pistol(m):
    box('Slide',(0,-0.10,0.06),(0.15,0.44,0.14),m['steel'])
    box('Frame',(0,-0.04,-0.035),(0.14,0.34,0.08),m['poly'])
    box('Grip',(0,0.08,-0.19),(0.14,0.18,0.28),m['poly'],0.025,(0.18,0,0))
    cyl('Barrel',(0,-0.345,0.07),0.032,0.12,m['edge'])
    box('FrontSight',(0,-0.28,0.15),(0.035,0.04,0.035),m['edge'],0.004)
    box('RearSight',(0,0.08,0.15),(0.12,0.035,0.035),m['edge'],0.004)
    box('TriggerGuard',(0,-0.09,-0.12),(0.11,0.16,0.035),m['steel'],0.01)
    cyl('Trigger',(0,-0.07,-0.10),0.018,0.08,m['edge'],'X',12)

def smg(m):
    box('Receiver',(0,0,0.03),(0.20,0.48,0.20),m['steel'])
    box('UpperReceiver',(0,-0.03,0.16),(0.16,0.46,0.08),m['poly'])
    box('Handguard',(0,-0.34,0.04),(0.18,0.25,0.16),m['poly'])
    cyl('Barrel',(0,-0.54,0.06),0.036,0.20,m['edge'])
    cyl('MuzzleBrake',(0,-0.65,0.06),0.055,0.08,m['steel'])
    box('Magazine',(0,0.02,-0.25),(0.13,0.16,0.37),m['poly'],0.018,(0.12,0,0))
    box('Foregrip',(0,-0.30,-0.14),(0.11,0.12,0.23),m['poly'],0.02)
    box('StockRod',(0,0.35,0.08),(0.07,0.30,0.07),m['edge'])
    box('StockPad',(0,0.51,0.06),(0.18,0.08,0.23),m['poly'])
    rail(-0.22,0.18,0.225,m['edge'])
    box('RedDot',(0,-0.06,0.29),(0.12,0.13,0.12),m['steel'])

def shotgun(m):
    box('Receiver',(0,0.02,0),(0.19,0.43,0.18),m['steel'])
    box('WoodenStock',(0,0.40,-0.015),(0.18,0.43,0.20),m['wood'],0.04)
    box('StockPad',(0,0.63,-0.015),(0.21,0.07,0.23),m['poly'],0.02)
    cyl('Barrel',(0,-0.52,0.055),0.044,0.68,m['edge'])
    cyl('MagazineTube',(0,-0.49,-0.055),0.038,0.56,m['steel'])
    box('Pump',(0,-0.38,-0.025),(0.20,0.28,0.17),m['wood'],0.035)
    for y in (-0.47,-0.42,-0.37,-0.32): box('PumpGroove',(0.103,y,-0.025),(0.012,0.018,0.13),m['poly'],0.002)
    box('BeadSight',(0,-0.84,0.12),(0.035,0.035,0.045),m['brass'],0.005)
    box('TriggerGuard',(0,0.02,-0.15),(0.12,0.18,0.04),m['steel'])
    box('ShellHolder',(0.12,0.08,0.02),(0.06,0.30,0.12),m['poly'])
    for y in (-0.02,0.07,0.16): cyl('Shell',(0.15,y,0.02),0.027,0.10,m['brass'],'Y',12)

def sniper(m):
    box('Receiver',(0,0.02,0),(0.18,0.46,0.17),m['steel'])
    box('LongStock',(0,0.43,-0.02),(0.17,0.48,0.18),m['poly'],0.03)
    box('CheekRest',(0,0.33,0.13),(0.16,0.27,0.10),m['poly'],0.025)
    box('StockPad',(0,0.70,-0.02),(0.20,0.07,0.23),m['poly'])
    box('Forestock',(0,-0.43,-0.015),(0.16,0.48,0.13),m['poly'])
    cyl('HeavyBarrel',(0,-0.91,0.02),0.038,0.54,m['edge'])
    cyl('MuzzleBrake',(0,-1.21,0.02),0.065,0.12,m['steel'])
    box('Magazine',(0,0.02,-0.16),(0.14,0.18,0.22),m['steel'])
    rail(-0.20,0.20,0.13,m['edge'])
    cyl('ScopeTube',(0,-0.03,0.28),0.065,0.45,m['steel'])
    cyl('ScopeFront',(0,-0.28,0.28),0.09,0.10,m['steel'])
    cyl('ScopeLens',(0,-0.335,0.28),0.072,0.012,m['glass'])
    for y in (-0.15,0.10): box('ScopeMount',(0,y,0.18),(0.08,0.06,0.13),m['edge'])
    cyl('ScopeDial',(0,-0.01,0.37),0.035,0.05,m['edge'],'Z',16)

BUILDERS={'pistol':pistol,'smg':smg,'shotgun':shotgun,'sniper':sniper}
for name,builder in BUILDERS.items():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for data in list(bpy.data.materials): bpy.data.materials.remove(data)
    builder(base_materials())
    bpy.ops.object.select_all(action='SELECT')
    for o in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    path=OUT/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
    print('WEAPON_EXPORTED',name,path)
