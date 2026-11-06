import bpy
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'props'
SOURCE=ROOT/'assets'/'blender'/'props'
RENDER=ROOT.parent/'diagnostics'/'street-assets'
for folder in (OUT,SOURCE,RENDER): folder.mkdir(parents=True,exist_ok=True)
MATS={}


def linear(v):
    v=v/255
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4


def material(name,color,rough=.7,metal=0.0,alpha=1.0,emission=0.0):
    if name in MATS: return MATS[name]
    rgb=tuple(linear(int(color[i:i+2],16)) for i in (0,2,4))
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,alpha); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*rgb,alpha)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    p.inputs['Alpha'].default_value=alpha
    if alpha<1.0:
        m.surface_render_method='DITHERED'; m.use_transparency_overlap=False
    if emission:
        p.inputs['Emission Color'].default_value=(*rgb,1); p.inputs['Emission Strength'].default_value=emission
    m.use_backface_culling=False
    MATS[name]=m
    return m


def assign(o,mat):
    o.data.materials.append(MATS[mat] if isinstance(mat,str) else mat)
    return o


def bevel(o,width=.025,segments=3):
    if width<=0: return
    mod=o.modifiers.new('Manufactured soft edges','BEVEL'); mod.width=width; mod.segments=segments
    o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')


def cube(name,loc,dims,mat,edge=.02,rot=None):
    x,y,z=(d*.5 for d in dims)
    verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.location=loc
    if rot: o.rotation_euler=rot
    assign(o,mat); bevel(o,edge)
    return o


def cylinder(name,loc,radius,depth,mat,axis='Z',vertices=32,radius2=None):
    rot={'Z':(0,0,0),'Y':(math.pi/2,0,0),'X':(0,math.pi/2,0)}[axis]
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius2,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; assign(o,mat); bevel(o,.006,2)
    for p in o.data.polygons: p.use_smooth=True
    return o


def torus(name,loc,major,minor,mat,axis='X'):
    rot={'Z':(0,0,0),'Y':(math.pi/2,0,0),'X':(0,math.pi/2,0)}[axis]
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=40,minor_segments=12,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; assign(o,mat)
    for p in o.data.polygons: p.use_smooth=True
    return o


def beam(name,a,b,radius,mat,radius2=None,vertices=16):
    a,b=Vector(a),Vector(b)
    o=cylinder(name,(a+b)/2,radius,(b-a).length,mat,vertices=vertices,radius2=radius2)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o


def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name+' mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); assign(o,mat)
    return o


def text(name,body,loc,size,mat,rotation=(0,0,0),align='CENTER'):
    curve=bpy.data.curves.new(name,'FONT'); curve.body=body; curve.size=size; curve.align_x=align; curve.align_y='CENTER'; curve.extrude=.0015; curve.bevel_depth=.0005
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rotation; assign(o,mat)
    return o


def make_palette():
    values=[
        ('police_white','d5d5ce',.36,.38),('police_black','182126',.34,.48),('police_grey','727c7e',.42,.55),
        ('steel','899295',.30,.78),('darkmetal','252c2e',.48,.62),('rubber','151919',.94,.02),
        ('glass','6e8b96',.16,.28,.46),('glass_dark','263d47',.22,.30,.68),('headlight','d9e2d5',.18,.25),
        ('tail_red','8f2926',.24,.22),('light_red','c84136',.20,.18,1,.35),('light_blue','326fa5',.20,.18,1,.35),
        ('rust','705344',.91,.08),('dirt','615f50',.96,0),('plate','d4d2bd',.55,.12),
        ('station_frame','37474b',.40,.65),('station_roof','56666a',.46,.55),('station_glass','9db7ba',.20,.12,.28),
        ('wood','796650',.72,.08),('poster','b9b29a',.78,0),('poster_teal','3f696d',.66,.08),
        ('bark','625849',.96,0),('bark_light','7b705e',.94,0),('soil','413c31',1,0),
        ('leaf_dark','30372a',.94,0),('leaf_mid','4c5134',.93,0),('leaf_light','706b42',.91,0),
    ]
    for args in values: material(*args)


def police_car():
    # Real-size sedan, 4.72 m long. Blender +Y is the front; glTF exports it as Godot -Z.
    cube('Police underbody',(0,0,.43),(1.72,4.35,.26),'darkmetal',.09)
    cube('Police main body',(0,0,.70),(1.91,4.62,.58),'police_black',.14)
    cube('Police hood',(0,1.42,.99),(1.80,1.48,.18),'police_black',.09)
    cube('Police rear deck',(0,-1.70,.98),(1.78,1.10,.17),'police_black',.07)
    # Trapezoidal cabin instead of another box.
    verts=[(-.84,-1.02,1.00),(.84,-1.02,1.00),(.84,.88,1.00),(-.84,.88,1.00),
           (-.67,-.72,1.64),(.67,-.72,1.64),(.67,.43,1.64),(-.67,.43,1.64)]
    mesh('Police cabin shell',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'police_white')
    bevel(bpy.context.scene.objects['Police cabin shell'],.035,3)
    cube('Police roof',(0,-.15,1.655),(1.38,1.22,.10),'police_white',.05)
    # Windshield and rear glass sit on the sloped cabin faces.
    mesh('Police windshield',[(-.73,.885,1.06),(.73,.885,1.06),(.61,.46,1.59),(-.61,.46,1.59)],[(0,1,2,3)],'glass_dark')
    mesh('Police rear windshield',[(-.72,-1.025,1.07),(-.60,-.75,1.58),(.60,-.75,1.58),(.72,-1.025,1.07)],[(0,1,2,3)],'glass_dark')
    for side in (-1,1):
        x=side*.852
        # Separate front/rear side glazing and a visible B pillar.
        mesh('Police front side window',[(x,.73,1.07),(x,.03,1.07),(side*.686,.03,1.57),(side*.686,.39,1.57)],[(0,1,2,3)],'glass')
        mesh('Police rear side window',[(x,-.88,1.07),(x,-.05,1.07),(side*.686,-.05,1.57),(side*.686,-.65,1.57)],[(0,1,2,3)],'glass')
        cube('Police B pillar',(side*.85,-.015,1.31),(.045,.09,.57),'police_black',.008)
        # White door panels, black lower rubbing strip, handles and mirrors.
        cube('Police front door paint',(side*.963,.37,.79),(.035,.92,.43),'police_white',.025)
        cube('Police rear door paint',(side*.963,-.68,.79),(.035,1.00,.43),'police_white',.025)
        cube('Police side rubbing strip',(side*.982,-.05,.53),(.035,2.45,.075),'darkmetal',.012)
        for y in (-.42,.55): cube('Police door handle',(side*.994,y,.96),(.045,.20,.045),'steel',.012)
        beam('Police mirror stalk',(side*.84,.62,1.13),(side*1.06,.59,1.14),.025,'darkmetal')
        cube('Police wing mirror',(side*1.08,.57,1.17),(.22,.30,.14),'police_black',.055)
        # Text is authored on both doors, not baked into a low-resolution texture.
        rot=(math.pi/2,0,side*math.pi/2)
        text('Police door lettering','POLICE',(side*1.002,-.04,.80),.205,'police_black',rot)
        text('Police unit number','09',(side*.998,-1.42,.80),.13,'plate',rot)
    # Wheel arches, detailed tyres, rims, five spokes and hub bolts.
    for x in (-.97,.97):
        for y in (-1.48,1.48):
            torus('Police tyre',(x,y,.45),.30,.105,'rubber')
            cylinder('Police rim',(x,y,.45),.265,.16,'steel','X',40)
            cylinder('Police rim inset',(x+(.085 if x>0 else -.085),y,.45),.205,.018,'darkmetal','X',36)
            outer=x+(.102 if x>0 else -.102)
            for k in range(5):
                a=k*math.tau/5
                beam('Police wheel spoke',(outer,y,.45),(outer,y+.19*math.cos(a),.45+.19*math.sin(a)),.022,'steel',vertices=10)
            cylinder('Police wheel hub',(outer,y,.45),.065,.035,'steel','X',24)
    # Front fascia, push bar, lights and plates.
    cube('Police front bumper',(0,2.33,.55),(1.84,.17,.20),'darkmetal',.05)
    cube('Police rear bumper',(0,-2.33,.55),(1.84,.16,.18),'darkmetal',.04)
    cube('Police grille',(0,2.337,.83),(.79,.045,.28),'darkmetal',.025)
    for x in [-.30,-.20,-.10,0,.10,.20,.30]: cube('Police grille slat',(x,2.367,.83),(.025,.025,.24),'steel',.004)
    for x in (-.66,.66):
        cube('Police headlamp',(x,2.322,.89),(.43,.075,.23),'headlight',.045)
        cube('Police tail lamp',(x,-2.323,.86),(.38,.065,.25),'tail_red',.035)
    cube('Police front plate',(0,2.432,.53),(.48,.025,.14),'plate',.012)
    text('Police front plate text','DF  009',(0,2.449,.53),.085,'police_black',(math.pi/2,0,math.pi))
    for x in (-.53,.53):
        beam('Police push bar upright',(x,2.43,.46),(x,2.43,1.04),.045,'steel')
    beam('Police push bar cross',(-.58,2.45,.77),(.58,2.45,.77),.045,'steel')
    # Roof light bar and aerial.
    cube('Police lightbar base',(0,-.12,1.77),(1.22,.31,.075),'darkmetal',.025)
    cube('Police red lightbar',(-.36,-.12,1.85),(.48,.28,.15),'light_red',.035)
    cube('Police blue lightbar',(.36,-.12,1.85),(.48,.28,.15),'light_blue',.035)
    cube('Police clear lightbar centre',(0,-.12,1.85),(.20,.27,.13),'headlight',.025)
    beam('Police aerial',(.55,-.62,1.70),(.57,-.68,2.10),.009,'darkmetal',vertices=8)
    # Restrained wear: scratches, a cracked windshield and dusty lower panels.
    for side in (-1,1):
        for i in range(6):
            y=-1.75+i*.53
            cube('Police lower body dirt',(side*.966,y,.51),(.008,.25,.055),'dirt',.004,rot=(.08*math.sin(i),0,.04))
    for i in range(4):
        a=(.12+i*.12,.891,1.13+i*.07)
        b=(a[0]+.13,a[1]-.055,a[2]+.12)
        beam('Police windshield crack',a,b,.0035,'plate',vertices=6)
    cube('Police bent hood edge',(.55,1.93,1.095),(.55,.12,.055),'police_grey',.015,rot=(.09,.03,-.04))


def bus_stop():
    # Right-side shelter: open front faces -X, length runs along Y.
    cube('Station concrete base',(0,0,.12),(1.65,4.15,.20),'police_grey',.045)
    for x in (-.63,.63):
        for y in (-1.83,1.83):
            cube('Station steel post',(x,y,1.43),(.095,.095,2.58),'station_frame',.015)
            cube('Station bolted foot',(x,y,.27),(.22,.22,.08),'steel',.012)
            for dx in (-.065,.065): cylinder('Station anchor bolt',(x+dx,y,.323),.018,.025,'darkmetal',vertices=10)
    cube('Station roof',(0,0,2.77),(1.78,4.30,.18),'station_roof',.065)
    cube('Station roof front fascia',(-.87,0,2.72),(.08,4.25,.26),'station_frame',.018)
    for y in (-1.85,1.85): cube('Station side top rail',(0,y,2.56),(1.34,.08,.10),'station_frame',.012)
    # Transparent back and one glazed windbreak, with physical frames.
    cube('Station back glass',(.635,0,1.48),(.028,3.48,1.96),'station_glass',.008)
    for y in (-1.75,0,1.75): cube('Station back glazing mullion',(.61,y,1.49),(.065,.055,2.03),'station_frame',.008)
    for z in (.48,2.49): cube('Station back horizontal rail',(.61,0,z),(.07,3.58,.07),'station_frame',.009)
    cube('Station end glass',(0,1.825,1.48),(1.17,.026,1.95),'station_glass',.008)
    # Slatted bench and supports.
    for x in (-.12,.06,.24,.42): cube('Station bench wooden slat',(x,0,.73),(.15,2.75,.075),'wood',.018)
    for z in (1.00,1.17,1.34): cube('Station bench backrest slat',(.51,0,z),(.07,2.75,.13),'wood',.018)
    for y in (-1.05,1.05):
        beam('Station bench front leg',(-.12,y,.27),(-.12,y,.70),.035,'station_frame')
        beam('Station bench rear leg',(.47,y,.27),(.47,y,1.42),.035,'station_frame')
    # A side advertising panel with simple geometric layout, not an empty black box.
    cube('Station poster frame',(.54,-1.10,1.55),(.16,.88,1.68),'station_frame',.025)
    cube('Station poster face',(.448,-1.10,1.55),(.022,.76,1.54),'poster',.008)
    cube('Station poster colour band',(.432,-1.10,1.83),(.012,.70,.52),'poster_teal',.004)
    text('Station poster title','CITY',(.415,-1.10,1.89),.18,'plate',(math.pi/2,0,-math.pi/2))
    text('Station poster subtitle','TRANSIT',(.415,-1.10,1.62),.085,'police_black',(math.pi/2,0,-math.pi/2))
    # Roadside totem, route numbers and a small timetable.
    cylinder('Station sign pole',(-1.00,-2.12,1.46),.045,2.70,'station_frame',vertices=24)
    cube('Station sign housing',(-1.00,-2.12,2.64),(.16,.58,.78),'station_frame',.045)
    cube('Station sign face',(-1.092,-2.12,2.66),(.018,.50,.65),'poster_teal',.012)
    text('Station BUS lettering','BUS',(-1.107,-2.12,2.80),.17,'plate',(math.pi/2,0,-math.pi/2))
    text('Station route numbers','12  24',(-1.108,-2.12,2.55),.078,'plate',(math.pi/2,0,-math.pi/2))
    cube('Station timetable case',(.55,.96,1.48),(.13,.50,.70),'station_frame',.018)
    cube('Station timetable paper',(.473,.96,1.48),(.015,.42,.60),'plate',.005)
    for i in range(6): cube('Station timetable printed line',(.461,.96,1.68-i*.075),(.008,.31,.012),'police_grey',.002)
    cube('Station roof light',(0,0,2.64),(.36,1.50,.055),'headlight',.015)


def street_tree(seed=9):
    rng=random.Random(seed)
    cube('Tree pit dry soil',(0,0,.17),(1.16,1.16,.10),'soil',.035)
    for x in (-.62,.62): cube('Tree pit stone border',(x,0,.20),(.12,1.35,.18),'police_grey',.025)
    for y in (-.62,.62): cube('Tree pit stone border',(0,y,.20),(1.35,.12,.18),'police_grey',.025)
    # Neglected but living street tree: upright trunk, exposed dead limbs and an uneven crown.
    # Keep the trunk vertical on both pavements; damage belongs in the branches, not a tilted base.
    trunk=[Vector((0,0,z)) for z in (.24,1.10,2.05,2.95,3.65,4.30)]
    radii=[.20,.155,.12,.085,.045]
    for i in range(5): beam('Tree tapered trunk',trunk[i],trunk[i+1],radii[i],'bark',radii[i]*.72,18)
    for k in range(6):
        a=k*math.tau/6
        beam('Tree root flare',(0,0,.43),(.34*math.cos(a),.34*math.sin(a),.23),.075,'bark',.025,12)
    for a,z in ((.35,2.75),(3.75,3.15)):
        start=Vector((0,0,z)); end=start+Vector((math.cos(a)*.82,math.sin(a)*.82,.48))
        beam('Tree broken dead limb',start,end,.055,'bark_light',.018,12)
    endpoints=[Vector((0,0,4.40)),Vector((.35,.15,4.15)),Vector((-.30,-.20,4.10))]
    for k in range(11):
        a=k*2.399+rng.uniform(-.18,.18)
        start=trunk[2 if k<4 else 3]
        length=rng.uniform(1.00,1.55)
        end=start+Vector((math.cos(a)*length,math.sin(a)*length,rng.uniform(.80,1.40)))
        mid=start.lerp(end,.55)+Vector((0,0,.16))
        beam('Tree primary branch',start,mid,.070,'bark',.042,14)
        beam('Tree primary branch',mid,end,.042,'bark',.018,12)
        for j in range(2):
            aa=a+(-.55 if j==0 else .55)
            tip=end+Vector((math.cos(aa)*.42,math.sin(aa)*.42,rng.uniform(.12,.45)))
            beam('Tree fine branch',end,tip,.020,'bark_light',.006,10)
            endpoints.append(tip)
        endpoints.append(end)
    verts=[]; faces=[]; indices=[]
    for center in endpoints:
        if rng.random()<.16: continue # whole bare sprays break the healthy rounded silhouette
        for i in range(32):
            if rng.random()<.12: continue
            theta=rng.uniform(0,math.tau); u=rng.uniform(-1,1); rr=rng.random()**(1/3)
            offset=Vector((math.sqrt(1-u*u)*math.cos(theta)*.68,math.sqrt(1-u*u)*math.sin(theta)*.68,u*.54))*rr
            c=center+offset
            length=rng.uniform(.24,.40); width=length*rng.uniform(.42,.62)
            axis=Vector((rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-.45,.65))).normalized()*length
            side=axis.cross(Vector((0,0,1))).normalized()*width
            if side.length<.01: side=Vector((width,0,0))
            base=len(verts)
            verts.extend([c-axis*.5,c-side*.5,c+Vector((0,0,.025)),c+side*.5,c+axis*.5])
            faces.extend([(base,base+1,base+2),(base,base+2,base+3),(base+1,base+4,base+2),(base+2,base+4,base+3)])
            tone=rng.choices([0,1,2],[.36,.48,.16])[0]; indices.extend([tone]*4)
    leaves=mesh('Tree individual folded leaves',verts,faces,'leaf_mid')
    leaves.data.materials.append(MATS['leaf_dark']); leaves.data.materials.append(MATS['leaf_light'])
    for poly,tone in zip(leaves.data.polygons,indices): poly.material_index=tone


def clear_scene():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
        for block in list(blocks):
            if block.users==0: blocks.remove(block)
    MATS.clear(); make_palette()


def asset_objects():
    return [o for o in bpy.context.scene.objects if o.type in {'MESH','FONT','CURVE'}]


def export_asset(name,builder):
    clear_scene(); builder()
    bpy.ops.object.select_all(action='DESELECT')
    for o in asset_objects(): o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'.blend')))
    print('STREET_ASSET_EXPORTED',name,len(asset_objects()))


def setup_render():
    scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
    scene.render.resolution_x=960; scene.render.resolution_y=640; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.world.color=(.18,.18,.18)
    world=bpy.data.worlds.new('Soft daylight') if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world=world; world.use_nodes=True
    bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.58,.68,.78,1); bg.inputs['Strength'].default_value=.45
    bpy.ops.object.light_add(type='AREA',location=(1,-4,8)); key=bpy.context.object; key.name='Large softbox'; key.data.energy=1400; key.data.shape='DISK'; key.data.size=7
    key.rotation_euler=(Vector((0,0,1.5))-key.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.light_add(type='SUN',location=(4,3,8)); sun=bpy.context.object; sun.data.energy=2.0; sun.data.angle=.12
    sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(145))
    bpy.ops.object.camera_add(); camera=bpy.context.object; camera.data.clip_end=250; scene.camera=camera
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.03)); ground=bpy.context.object; ground.name='Preview ground'; assign(ground,'soil')
    scene.view_settings.view_transform='AgX'
    try: scene.view_settings.look='AgX - Medium High Contrast'
    except Exception: pass


def point_camera(location,target,lens=48):
    camera=bpy.context.scene.camera; camera.location=location; camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=lens


def render_asset_views(name):
    setup_render()
    shots=[((6,7,4.2),(0,0,1.0)),((-6,7,4.0),(0,0,1.0)),((6,-7,4.0),(0,0,1.0)),((-6,-7,4.2),(0,0,1.0)),((0,.1,12),(0,0,0))]
    if name=='street_tree': shots=[((8,9,6),(0,0,2.5)),((-8,9,6),(0,0,2.5)),((8,-9,6),(0,0,2.5)),((-8,-9,6),(0,0,2.5)),((0,.1,15),(0,0,1.5))]
    if name=='bus_stop': shots=[((-7,7,4.5),(0,0,1.3)),((-7,-7,4.5),(0,0,1.3)),((6,7,4.5),(0,0,1.3)),((6,-7,4.5),(0,0,1.3)),((0,.1,13),(0,0,0))]
    for i,(loc,target) in enumerate(shots):
        point_camera(loc,target,52)
        bpy.context.scene.render.filepath=str(RENDER/(name+'-%02d.png'%i)); bpy.ops.render.render(write_still=True)


for name,builder in [('police_car',police_car),('bus_stop',bus_stop),('street_tree',street_tree)]:
    export_asset(name,builder)
    render_asset_views(name)
print('STREET_ASSETS_COMPLETE')
