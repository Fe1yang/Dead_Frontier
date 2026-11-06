import bpy
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "assets" / "models"
SOURCE = ROOT / "assets" / "blender"
RENDERS = ROOT / "renders"
for folder in (MODELS, SOURCE, RENDERS):
    folder.mkdir(parents=True, exist_ok=True)
random.seed(73)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials):
    bpy.data.materials.remove(data)

MATS = {}
def mat(key, color, rough=0.72, metal=0.0, emission=0.0):
    if key in MATS:
        return MATS[key]
    color = color.lstrip('#')
    srgb = tuple(int(color[i:i+2], 16)/255 for i in (0,2,4))
    rgba = tuple(c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4 for c in srgb) + (1,)
    m = bpy.data.materials.new(key)
    m.diffuse_color = rgba
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = rgba
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emission:
        p.inputs['Emission Color'].default_value = rgba
        p.inputs['Emission Strength'].default_value = emission
    MATS[key] = m
    return m

mat('ink','17221f'); mat('boot','101714'); mat('pants','293c35')
mat('lime','b8dd3f'); mat('lime_dark','6f8d30'); mat('skin','d6a070')
mat('cap','1b2923'); mat('bag','3e5243'); mat('strap','222d27')
mat('gun','222b2a',0.3,0.65); mat('gun_edge','65736d',0.35,0.6)
mat('wood','594b36'); mat('zskin','8ca568'); mat('zskin_dark','627c50')
mat('shirt','45574d'); mat('shirt2','74473e'); mat('blood','692d28')
mat('eye','ff5b35',0.4,0,3.0); mat('bone','c6caa2')
mat('red','b8422e',0.5,0.25); mat('yellow','e5bd3f'); mat('rust','763b27')
mat('asphalt','303b38'); mat('concrete','788077'); mat('line','d6d3ad')
mat('crack','151e1b'); mat('car','47665d',0.45,0.25); mat('glass','213a3b',0.2,0.35)

def assign(obj, material):
    obj.data.materials.append(MATS[material] if isinstance(material,str) else material)
    return obj

def cube(name, loc, dims, material, bevel=0.025, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rot: o.rotation_euler=rot
    assign(o,material)
    if bevel:
        b=o.modifiers.new('Edge bevel','BEVEL'); b.width=bevel; b.segments=1
    return o

def sphere(name, loc, scale, material, segments=12, rings=6):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o,material)
    for p in o.data.polygons: p.use_smooth=False
    return o

def cyl(name, loc, radius, depth, material, vertices=12, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    if rot: o.rotation_euler=rot
    assign(o,material)
    b=o.modifiers.new('Edge bevel','BEVEL'); b.width=0.018; b.segments=1
    return o

def beam(name, a, b, width, material, bevel=0.025):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,(width,width,(b-a).length),material,bevel)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def limb(name, joint, length, width, material):
    # Origin remains at the hip/shoulder so Godot can rotate this mesh directly.
    o=cube(name,(0,0,0),(width,width,length),material,0.035)
    for v in o.data.vertices: v.co.z -= length/2
    o.location=joint
    return o

def muzzle():
    o=bpy.data.objects.new('Muzzle',None); bpy.context.collection.objects.link(o)
    o.location=(0,-1.12,1.32)
    return o

def player():
    for side,x in [('L',-0.18),('R',0.18)]:
        cube('Boot'+side,(x,-0.06,0.12),(0.25,0.43,0.22),'boot',0.05)
        limb('Leg'+side,(x,0,0.83),0.63,0.24,'pants')
    cube('Belt',(0,0,0.88),(0.62,0.38,0.16),'strap')
    cube('Torso',(0,0,1.18),(0.68,0.42,0.62),'lime',0.09)
    cube('Vest',(0,-0.23,1.2),(0.51,0.12,0.44),'lime_dark',0.04)
    cube('Backpack',(0,0.28,1.19),(0.52,0.25,0.5),'bag',0.06)
    for x in (-0.24,0.24): cube('Strap',(x,-0.31,1.22),(0.065,0.06,0.48),'strap',0.015)
    cube('Neck',(0,0,1.52),(0.19,0.18,0.18),'skin')
    sphere('Head',(0,-0.015,1.71),(0.25,0.23,0.28),'skin')
    cube('Cap',(0,0.01,1.9),(0.52,0.44,0.16),'cap',0.07)
    cube('CapBill',(0,-0.28,1.86),(0.45,0.28,0.06),'cap',0.04)
    cube('Nose',(0,-0.245,1.7),(0.09,0.1,0.1),'skin',0.025)
    # Bent arms grip the rifle.
    beam('ArmL',(-0.37,0,1.42),(-0.42,-0.28,1.18),0.22,'lime')
    beam('ForearmL',(-0.42,-0.28,1.18),(-0.15,-0.58,1.29),0.18,'skin')
    beam('ArmR',(0.37,0,1.42),(0.43,-0.22,1.21),0.22,'lime')
    beam('ForearmR',(0.43,-0.22,1.21),(0.15,-0.77,1.31),0.18,'skin')
    cube('GunStock',(0,-0.22,1.32),(0.18,0.46,0.2),'gun',0.025)
    cube('GunReceiver',(0,-0.57,1.34),(0.2,0.42,0.2),'gun_edge',0.025)
    cube('GunBody',(0,-0.69,1.35),(0.17,0.52,0.16),'gun',0.02)
    cyl('GunBarrel',(0,-1.00,1.36),0.045,0.46,'gun_edge',10,(math.pi/2,0,0))
    cube('Magazine',(0,-0.56,1.15),(0.15,0.2,0.31),'gun',0.025,(0.18,0,0))
    cube('Sight',(0,-0.62,1.49),(0.11,0.2,0.09),'ink',0.015)
    muzzle()

def female_player():
    mat('jacket_red','b84e42'); mat('jacket_dark','71362f'); mat('hair','302820'); mat('hair_edge','4a3828')
    for side,x in [('L',-0.16),('R',0.16)]:
        cube('Boot'+side,(x,-0.08,0.12),(0.23,0.43,0.23),'boot',0.05)
        cube('BootStrap'+side,(x,-0.20,0.18),(0.24,0.055,0.06),'gun_edge',0.01)
        limb('Leg'+side,(x,0,0.84),0.64,0.21,'pants')
        cube('KneePad'+side,(x,-0.13,0.53),(0.20,0.08,0.20),'ink',0.035)
    cube('Belt',(0,0,0.89),(0.55,0.35,0.14),'strap')
    cube('BeltBuckle',(0,-0.195,0.89),(0.11,0.045,0.09),'gun_edge',0.012)
    cube('Torso',(0,0,1.19),(0.58,0.37,0.60),'jacket_red',0.08)
    cube('Shirt',(0,-0.20,1.25),(0.30,0.08,0.40),'ink',0.025)
    cube('VestHarness',(0,-0.255,1.18),(0.48,0.08,0.09),'jacket_dark',0.02)
    for x in (-0.22,0.22):
        cube('ShoulderStrap',(x,-0.23,1.27),(0.055,0.05,0.44),'strap',0.012)
        cube('JacketPocket',(x,-0.24,1.07),(0.16,0.06,0.15),'jacket_dark',0.02)
    cube('Backpack',(0,0.25,1.19),(0.43,0.22,0.44),'bag',0.055)
    cyl('Bedroll',(0,0.29,1.47),0.11,0.50,'pants',10,(0,math.pi/2,0))
    cube('Neck',(0,0,1.52),(0.17,0.16,0.18),'skin')
    sphere('Head',(0,-0.015,1.72),(0.235,0.215,0.275),'skin',16,8)
    for side in (-1,1): sphere('Ear',(side*0.235,-0.01,1.72),(0.05,0.04,0.085),'skin',10,5)
    sphere('Nose',(0,-0.235,1.70),(0.055,0.075,0.07),'skin',10,5)
    for x in (-0.085,0.085):
        sphere('EyeWhite',(x,-0.218,1.77),(0.052,0.018,0.026),'bone',12,6)
        sphere('Pupil',(x,-0.237,1.77),(0.016,0.009,0.019),'ink',8,4)
        beam('Brow',(x-0.05,-0.22,1.82),(x+0.05,-0.22,1.82),0.022,'hair')
    cube('Mouth',(0,-0.225,1.59),(0.12,0.025,0.025),'blood',0.01)
    # Swept hair, separate fringe and a long curved ponytail.
    sphere('HairMass',(0,0.025,1.86),(0.25,0.22,0.16),'hair',16,8)
    for i in range(8):
        x=-0.19+i*0.053
        hair_lock('FemaleFringe',[(x,-0.10,1.89),(x+0.035,-0.22,1.85),(x+0.055,-0.235,1.77-(i%3)*0.025)],[0.045,0.035,0.002],'hair')
    sphere('PonyTie',(0,0.245,1.80),(0.11,0.07,0.08),'jacket_red',10,5)
    hair_lock('Ponytail',[(0,0.24,1.83),(0.04,0.43,1.67),(0.10,0.48,1.40),(0.17,0.42,1.22)],[0.13,0.12,0.085,0.008],'hair')
    hair_lock('PonyHighlight',[(0.04,0.31,1.81),(0.10,0.48,1.62),(0.14,0.50,1.39)],[0.035,0.03,0.003],'hair_edge')
    beam('ArmL',(-0.33,0,1.42),(-0.39,-0.28,1.18),0.20,'jacket_red')
    beam('ForearmL',(-0.39,-0.28,1.18),(-0.14,-0.58,1.29),0.16,'skin')
    beam('ArmR',(0.33,0,1.42),(0.39,-0.22,1.21),0.20,'jacket_red')
    beam('ForearmR',(0.39,-0.22,1.21),(0.14,-0.77,1.31),0.16,'skin')
    cube('GunStock',(0,-0.22,1.32),(0.18,0.46,0.2),'gun',0.025)
    cube('GunReceiver',(0,-0.57,1.34),(0.2,0.42,0.2),'gun_edge',0.025)
    cube('GunBody',(0,-0.69,1.35),(0.17,0.52,0.16),'gun',0.02)
    cyl('GunBarrel',(0,-1.00,1.36),0.045,0.46,'gun_edge',10,(math.pi/2,0,0))
    cube('Magazine',(0,-0.56,1.15),(0.15,0.2,0.31),'gun',0.025,(0.18,0,0))
    cube('Sight',(0,-0.62,1.49),(0.11,0.2,0.09),'ink',0.015)
    cube('Foregrip',(0,-0.83,1.20),(0.10,0.12,0.23),'gun',0.02)
    for i in range(5): cube('Rail',(0,-0.48-i*0.10,1.45),(0.15,0.045,0.035),'gun_edge',0.005)
    muzzle()

def hair_lock(name, points, radii, material):
    # Curved, tapered six-sided locks: a real silhouette rather than a helmet.
    points=[Vector(p) for p in points]
    verts=[]; faces=[]; sides=6
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        ref=Vector((0,1,0))
        u=tangent.cross(ref).normalized()
        if u.length<0.1: u=tangent.cross(Vector((1,0,0))).normalized()
        v=tangent.cross(u).normalized()
        for j in range(sides):
            a=math.tau*j/sides
            verts.append(p+(u*math.cos(a)+v*math.sin(a))*radii[i])
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j; b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(range(sides-1,-1,-1)))
    faces.append(tuple((len(points)-1)*sides+j for j in range(sides)))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); assign(o,material)
    return o

def add_hair(kind,w,h):
    mat('hair','302820'); mat('hair_edge','4a3828'); mat('hair_gray','606150')
    hair='hair_gray' if kind=='brute' else 'hair'
    # Scalp sits behind the forehead; individual locks create the hairline.
    sphere('HairMass',(0.04,0.015,1.86*h),(0.275*w,0.235*w,0.16*h),hair,16,8)
    if kind=='runner':
        for i in range(7):
            y=-0.17+i*0.055
            hair_lock('Mohawk',[(0.04,y,1.91*h),(0.04,y+0.02,2.10*h),(0.04,y+0.07,2.18*h)],[0.065,0.052,0.003],'hair_edge')
    else:
        count=11 if kind=='walker' else 7
        for i in range(count):
            x=-0.21*w+i*(0.43*w/(count-1))
            lift=0.10+0.045*math.sin(i*1.7)
            hair_lock('CrownLock',[(x,0.02,1.88*h),(x+0.025,-0.015,(1.98+lift)*h),(x+0.07,-0.10,(2.00+lift)*h)],[0.065*w,0.05*w,0.003],hair)
        for i in range(6):
            x=-0.20*w+i*0.08*w
            drop=0.07+0.05*(i%3)
            hair_lock('Fringe',[(x,-0.14,1.91*h),(x+0.025,-0.245,1.87*h),(x+0.04,-0.265,(1.84-drop)*h)],[0.06*w,0.045*w,0.002],hair)
        for side in (-1,1):
            hair_lock('Sideburn',[(0.04+side*0.24*w,-0.02,1.85*h),(0.04+side*0.25*w,-0.08,1.70*h),(0.04+side*0.23*w,-0.11,1.63*h)],[0.055,0.04,0.004],hair)

def zombie(kind='walker'):
    brute=kind=='brute'; runner=kind=='runner'
    w=1.28 if brute else (0.88 if runner else 1.0)
    h=1.12 if brute else 1.0
    shirt='shirt2' if runner else 'shirt'
    mat('hair','302820'); mat('hair_edge','4a3828'); mat('hair_gray','606150')
    for side,x in [('L',-0.17*w),('R',0.17*w)]:
        cube('Boot'+side,(x,-0.08,0.1),(0.25*w,0.43,0.20),'boot',0.045)
        leg=limb('Leg'+side,(x,0,0.77*h),0.62*h,0.23*w,'pants')
        if side=='L': leg.rotation_euler.x=0.1
        cube('KneeFold'+side,(x,-0.125,0.48*h),(0.19*w,0.035,0.055),'ink',0.012,(0,0,0.15 if side=='L' else -0.15))
    cube('Torso',(0,0.03,1.12*h),(0.65*w,0.4*w,0.65*h),shirt,0.075,(0.07 if runner else 0,0,0))
    # Seams, folds, a torn pocket and an asymmetric hem.
    cube('CollarL',(-0.13*w,-0.205*w,1.40*h),(0.22,0.045,0.16),'ink',0.015,(0,0,-0.5))
    cube('CollarR',(0.15*w,-0.205*w,1.40*h),(0.22,0.045,0.16),'ink',0.015,(0,0,0.5))
    cube('Pocket',(-0.16*w,-0.205*w,1.18*h),(0.19,0.035,0.17),shirt,0.015,(0,0,-0.08))
    for i in range(4):
        cube('ClothFold',(-0.21*w+i*0.14*w,-0.215*w,1.02*h),(0.025,0.025,0.28),'ink',0.008,(0,0,-0.25+i*0.16))
    for i,x in enumerate((-0.25,-0.08,0.10,0.26)):
        cube('Tear',(x*w,-0.02,(0.79+(i%2)*0.05)*h),(0.13*w,0.4*w,0.19),shirt,0.008,(0,0,x*0.6))
    # Faceted skull with cheekbones, jaw, ears and a projecting nose.
    sphere('Head',(0.04,-0.06,1.67*h),(0.27*w,0.25*w,0.29*h),'zskin',16,8)
    cube('Jaw',(0.04,-0.18,1.51*h),(0.36*w,0.25,0.17),'zskin_dark',0.055)
    for side in (-1,1):
        sphere('Ear',(0.04+side*0.27*w,-0.055,1.67*h),(0.065,0.05,0.10),'zskin_dark',10,5)
        cube('Cheek',(0.04+side*0.17*w,-0.245,1.61*h),(0.12,0.07,0.08),'zskin',0.025,(0,0,side*0.18))
    sphere('NoseBridge',(0.04,-0.29,1.68*h),(0.055,0.075,0.12),'zskin',10,5)
    sphere('NoseTip',(0.04,-0.355,1.62*h),(0.075,0.07,0.055),'zskin_dark',10,5)
    # Almond eyes are recessed under sculpted brows, not standalone dots.
    for i,x in enumerate((-0.105,0.135)):
        sphere('EyeSocket',(x*w,-0.277*w,1.735*h),(0.092*w,0.025,0.058),'zskin_dark',12,6)
        sphere('EyeWhite',(x*w,-0.300*w,1.733*h),(0.065*w,0.018,0.027),'bone',12,6)
        sphere('Pupil',((x+(-0.015 if i==0 else 0.01))*w,-0.319*w,1.733*h),(0.018,0.009,0.022),'eye',8,4)
        beam('Brow',((x-0.08)*w,-0.29*w,1.80*h),((x+0.075)*w,-0.29*w,1.79*h+(0.02 if i==0 else -0.01)),0.035,'hair')
    # Open mouth, individual teeth and lower lip.
    cube('MouthCavity',(0.04,-0.316*w,1.52*h),(0.23*w,0.038,0.10),'blood',0.035)
    for i in range(5):
        cube('Tooth',(-0.065*w+i*0.047*w,-0.340*w,1.555*h),(0.035,0.022,0.045),'bone',0.007,(0,0,(i-2)*0.035))
    cube('LowerLip',(0.04,-0.325*w,1.47*h),(0.24*w,0.032,0.035),'zskin_dark',0.014)
    add_hair(kind,w,h)
    # Arms, hands and four separate curled fingers per hand.
    for side,x in [('L',-0.4*w),('R',0.4*w)]:
        shoulder=(x,0,1.39*h)
        elbow=(x*1.15,-0.38,1.25*h+(0.1 if side=='L' else -0.03))
        hand=(x*1.05,-0.76,1.29*h)
        beam('Arm'+side,shoulder,elbow,0.21*w,shirt)
        sphere('Elbow'+side,elbow,(0.12*w,0.12,0.12),'zskin',10,5)
        beam('Forearm'+side,elbow,hand,0.17*w,'zskin')
        sphere('Hand'+side,hand,(0.13*w,0.16,0.09),'zskin',10,5)
        for f in range(4):
            fx=hand[0]+(f-1.5)*0.047*w
            hair_lock('Finger'+side,[(fx,hand[1]-0.08,hand[2]),(fx,hand[1]-0.19,hand[2]-0.025),(fx,hand[1]-0.22,hand[2]-0.09)],[0.024,0.021,0.012],'zskin')
    # A chest tear exposes skin and ribs.
    sphere('ChestWound',(0.17*w,-0.218*w,1.23*h),(0.13,0.025,0.18),'blood',10,5)
    for i in range(3):
        beam('Rib',(0.10*w,-0.248*w,(1.16+i*0.065)*h),(0.23*w,-0.248*w,(1.19+i*0.065)*h),0.025,'bone',0.006)
    if brute:
        for x in (-0.43,0.43): sphere('Shoulder',(x,0,1.52),(0.24,0.28,0.2),'zskin_dark')
        beam('Rebar',(-0.36,0.12,1.50),(0.28,0.20,1.95),0.045,'rust')

def barrel():
    cyl('Barrel',(0,0,0.47),0.35,0.9,'red',16)
    for z in (0.08,0.26,0.68,0.87): cyl('Ring',(0,0,z),0.37,0.07,'rust',16)
    cyl('WarningBand',(0,0,0.48),0.356,0.19,'yellow',16)
    cyl('Cap',(0,0,0.94),0.08,0.05,'gun',10)
    cube('Hazard',(0,-0.357,0.48),(0.19,0.025,0.12),'ink',0.01,(0,0,0.0))

def barrier():
    for x in (-0.85,0.85):
        cube('Foot',(x,0,0.09),(0.45,0.65,0.18),'concrete',0.04)
        cube('Post',(x,0,0.63),(0.16,0.18,1.05),'rust',0.025)
    board=cube('Board',(0,0,0.78),(2.15,0.17,0.46),'yellow',0.035)
    for x in (-0.75,-0.25,0.25,0.75):
        cube('Stripe',(x,-0.095,0.78),(0.22,0.025,0.46),'ink',0.005,(0,0,-0.35))

def streetlight():
    cyl('Base',(0,0,0.13),0.24,0.25,'concrete')
    cyl('Pole',(0,0,1.75),0.055,3.4,'gun',10)
    beam('Arm',(0,0,3.4),(0.6,0,3.4),0.09,'gun')
    cube('Lamp',(0.64,0,3.35),(0.45,0.28,0.15),'gun_edge',0.04)
    cube('Glow',(0.64,0,3.26),(0.35,0.2,0.025),'yellow',0.01)

def car():
    cube('Chassis',(0,0,0.48),(1.65,3.0,0.55),'car',0.13)
    cube('Cabin',(0,0.15,1.0),(1.42,1.55,0.7),'car',0.11)
    cube('Windshield',(0,-0.65,1.05),(1.2,0.05,0.45),'glass',0.03,(0.22,0,0))
    cube('RearGlass',(0,0.96,1.04),(1.18,0.05,0.4),'glass',0.03,(-0.18,0,0))
    for x in (-0.84,0.84):
        for y in (-0.95,0.95): cyl('Wheel',(x,y,0.37),0.34,0.2,'boot',12,(0,math.pi/2,0))
    for x in (-0.55,0.55): cube('Headlight',(x,-1.515,0.56),(0.32,0.035,0.18),'line',0.03)
    cube('RustPatch',(0.45,-0.5,0.77),(0.45,0.6,0.025),'rust',0.02,(0.1,0.2,0))

def road():
    cube('Road',(0,0,-0.12),(8,16,0.24),'asphalt',0.02)
    for x in (-4.25,4.25):
        cube('Curb',(x,0,0.04),(0.48,16,0.28),'concrete',0.035)
        cube('EdgeLine',(math.copysign(3.72,x),0,0.012),(0.09,16,0.025),'line',0)
    for y in (-6,-2,2,6): cube('Dash',(0,y,0.015),(0.10,1.8,0.025),'line',0)
    for i in range(12):
        x=random.uniform(-3.3,3.3); y=random.uniform(-7.5,7.5)
        length=random.uniform(0.35,1.2)
        cube('Crack',(x,y,0.017),(0.025,length,0.012),'crack',0,(0,0,random.uniform(-0.8,0.8)))

def dead_tree():
    cyl('Trunk',(0,0,1.0),0.12,2.0,'wood',8)
    beam('BranchL',(0,0,1.3),(-0.7,0,2.0),0.13,'wood')
    beam('BranchR',(0,0,1.55),(0.55,0.15,2.3),0.11,'wood')
    beam('Twig',(-0.55,0,1.86),(-0.8,0.05,2.3),0.07,'wood')

def setup_render(name):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=32
    scene.cycles.use_denoising=True
    scene.world.color=(0.18,0.18,0.18)
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.20,0.23,0.22,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.5
    bpy.ops.object.light_add(type='AREA', location=(2,-4,5))
    key=bpy.context.object; key.name='Key'; key.data.energy=650; key.data.shape='DISK'; key.data.size=4
    key.rotation_euler=(Vector((0,0,1))-key.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.light_add(type='AREA', location=(-3,-1,3))
    fill=bpy.context.object; fill.name='Fill'; fill.data.energy=350; fill.data.size=3
    fill.rotation_euler=(Vector((0,0,1))-fill.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(3.2,-5.2,2.8))
    cam=bpy.context.object; cam.name='Camera'
    cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=2.8; cam.data.clip_end=100
    scene.camera=cam
    scene.render.resolution_x=640; scene.render.resolution_y=640; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(RENDERS/(name+'.png'))

def export_model(name, builder, render=False):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    builder()
    # Apply bevels before saving/exporting for predictable mobile geometry.
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':
            bpy.context.view_layer.objects.active=o
            for mod in list(o.modifiers):
                bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(MODELS/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'.blend')))
    print('MODEL_EXPORTED',name,len([o for o in bpy.context.scene.objects if o.type=='MESH']))
    if render:
        setup_render(name)
        bpy.ops.render.render(write_still=True)

export_model('survivor',player,True)
export_model('survivor_female',female_player,True)
export_model('zombie_walker',lambda: zombie('walker'),True)
export_model('zombie_runner',lambda: zombie('runner'),True)
export_model('zombie_brute',lambda: zombie('brute'),True)
export_model('barrel',barrel,True)
export_model('barrier',barrier)
export_model('streetlight',streetlight)
export_model('car',car)
export_model('road',road)
export_model('dead_tree',dead_tree)
print('ALL_ASSETS_DONE')
