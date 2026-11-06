import bpy
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'props'
SOURCE=ROOT/'assets'/'blender'/'props'
RENDER=ROOT/'diagnostics'/'nature'
for folder in (OUT,SOURCE,RENDER): folder.mkdir(parents=True,exist_ok=True)
MATS={}


def linear(v):
    v=v/255
    return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4


def material(name,color,rough=.85,metal=0):
    rgb=tuple(linear(int(color[i:i+2],16)) for i in (0,2,4))
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*rgb,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    MATS[name]=m
    return m


def assign(o,mat):
    o.data.materials.append(MATS[mat]); return o


def cube(name,loc,dims,mat,edge=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    assign(o,mat)
    if edge:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=edge; mod.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o


def beam(name,a,b,radius,mat,radius2=None,vertices=12):
    a,b=Vector(a),Vector(b)
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=(b-a).length,location=(a+b)/2)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius2,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); assign(o,mat)
    for p in o.data.polygons: p.use_smooth=True
    return o


def pit(size=1.15):
    cube('Square tree pit soil',(0,0,.15),(size,size,.09),'soil',.025)
    for x in (-size/2-.06,size/2+.06): cube('Square tree pit border',(x,0,.19),(.12,size+.24,.16),'stone',.018)
    for y in (-size/2-.06,size/2+.06): cube('Square tree pit border',(0,y,.19),(size+.24,.12,.16),'stone',.018)


def pine_tree():
    rng=random.Random(713)
    pit(1.10)
    beam('Pine single continuous trunk',(0,0,.20),(0,0,5.28),.15,'bark',.018,18)
    verts=[]; faces=[]; tones=[]
    def needle(base,direction,length):
        axis=direction.normalized()*length
        side=axis.cross(Vector((0,0,1)))
        if side.length<.001: side=Vector((1,0,0))
        side=side.normalized()*.010
        n=len(verts); verts.extend([base-side,base+side,base+axis])
        faces.extend([(n,n+1,n+2),(n+2,n+1,n)])
        tone=rng.choices([0,1],[.58,.42])[0]; tones.extend([tone,tone])
    # One botanical tree: radial woody branches, secondary twigs, then individual needles.
    for level in range(10):
        z=1.30+level*.39; length=1.48*(1-level/12.0)
        count=6 if level<7 else 5
        for k in range(count):
            a=k*math.tau/count+level*.83+rng.uniform(-.14,.14)
            radial=Vector((math.cos(a),math.sin(a),0)); tangent=Vector((-math.sin(a),math.cos(a),0))
            start=Vector((0,0,z)); end=start+radial*length+Vector((0,0,rng.uniform(-.13,.10)))
            beam('Pine woody radial branch',start,end,.040*(1-level*.055),'bark',.007,10)
            for j in range(2,7):
                base=start.lerp(end,j/7)
                for sign in (-1,1):
                    tip=base+radial*rng.uniform(.16,.26)+tangent*sign*rng.uniform(.20,.34)+Vector((0,0,.07))
                    beam('Pine secondary twig',base,tip,.008,'bark',.0025,7)
                    for n in range(13):
                        p=base.lerp(tip,n/13)
                        for s in (-1,1):
                            direction=tangent*s*.65+radial*.35+Vector((0,0,rng.uniform(.15,.65)))
                            needle(p,direction,rng.uniform(.13,.22))
    data=bpy.data.meshes.new('Single pine individual needles mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new('Single pine needle canopy',data); bpy.context.collection.objects.link(o)
    assign(o,'pine_dark'); assign(o,'pine_mid')
    for poly,tone in zip(data.polygons,tones): poly.material_index=tone


def leaf_mesh(name,centers,rng,scale=1.0):
    verts=[]; faces=[]; tones=[]
    for center in centers:
        for i in range(22):
            c=center+Vector((rng.uniform(-.38,.38),rng.uniform(-.38,.38),rng.uniform(-.22,.30)))*scale
            length=rng.uniform(.16,.27)*scale; width=length*.50
            a=rng.uniform(0,math.tau)
            axis=Vector((math.cos(a)*length,math.sin(a)*length,rng.uniform(-.06,.08)*scale))
            side=Vector((-math.sin(a)*width,math.cos(a)*width,0))
            n=len(verts); verts.extend([c-axis*.5,c-side*.5,c+Vector((0,0,.025)),c+side*.5,c+axis*.5])
            faces.extend([(n,n+1,n+2),(n,n+2,n+3),(n+1,n+4,n+2),(n+2,n+4,n+3)])
            tones.extend([rng.randrange(3)]*4)
    data=bpy.data.meshes.new(name+' mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o)
    for mat in ('leaf_dark','leaf_mid','leaf_light'): assign(o,mat)
    for poly,tone in zip(data.polygons,tones): poly.material_index=tone


def sapling():
    rng=random.Random(991)
    pit(.86)
    beam('Sapling trunk',(0,0,.18),(.04,0,2.75),.075,'bark',.020,12)
    centers=[]
    for k in range(9):
        a=k*2.399; z=1.25+k*.15
        start=Vector((.02,0,z)); end=Vector((math.cos(a)*.62,math.sin(a)*.62,z+.55))
        beam('Sapling fine branch',start,end,.025,'bark',.007,9); centers.append(end)
    leaf_mesh('Sapling individual leaves',centers,rng,.85)
    for x in (-.43,.43):
        beam('Sapling support stake',(x,0,.16),(x,0,1.65),.025,'wood',vertices=9)
    beam('Sapling support tie',(-.43,0,1.30),(.43,0,1.30),.018,'wood',vertices=8)


def flowerbed():
    rng=random.Random(552)
    cube('Planter concrete base',(0,0,.23),(1.95,1.10,.30),'stone',.045)
    cube('Planter dark soil',(0,0,.405),(1.68,.83,.07),'soil',.018)
    for x in (-.94,.94): cube('Planter side wall',(x,0,.43),(.15,1.12,.36),'stone',.025)
    for y in (-.49,.49): cube('Planter side wall',(0,y,.43),(1.82,.14,.36),'stone',.025)
    for i in range(11):
        x=-.72+(i%6)*.28+rng.uniform(-.06,.06); y=-.23+(i//6)*.43+rng.uniform(-.07,.07)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.23,location=(x,y,.57))
        o=bpy.context.object; o.name='Planter shrub clump'; o.scale=(1,.8,.72); assign(o,'leaf_dark' if i%2 else 'leaf_mid')
    for i in range(18):
        x=rng.uniform(-.73,.73); y=rng.uniform(-.29,.29); z=rng.uniform(.74,.91)
        beam('Flower stem',(x,y,.52),(x,y,z),.009,'leaf_dark',vertices=6)
        for p in range(5):
            a=p*math.tau/5
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.055,location=(x+math.cos(a)*.047,y+math.sin(a)*.047,z))
            o=bpy.context.object; o.name='Muted flower petal'; o.scale=(1,.7,.35); assign(o,'flower_rust' if i%3 else 'flower_cream')


def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
        for block in list(blocks):
            if block.users==0: blocks.remove(block)
    MATS.clear()
    for args in [('soil','3e392e',1,0),('stone','9a9d96',.92,0),('bark','5c5142',.96,0),('wood','75644d',.85,0),
                 ('pine_dark','263f35',.94,0),('pine_mid','3e5841',.93,0),('leaf_dark','364c35',.95,0),('leaf_mid','566449',.94,0),('leaf_light','7b7951',.93,0),
                 ('flower_rust','9b5c4b',.90,0),('flower_cream','c4b98f',.90,0)]: material(*args)


def render(name):
    scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
    scene.render.resolution_x=700; scene.render.resolution_y=700; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'
    world=bpy.data.worlds.new('Nature preview world'); world.use_nodes=True; scene.world=world
    bg=world.node_tree.nodes.get('Background') or world.node_tree.nodes.new('ShaderNodeBackground'); bg.inputs['Color'].default_value=(.45,.55,.65,1); bg.inputs['Strength'].default_value=.45
    cube('Preview ground',(0,0,-.035),(200,200,.05),'soil',0)
    bpy.ops.object.light_add(type='AREA',location=(3,-4,7)); light=bpy.context.object; light.data.energy=900; light.data.shape='DISK'; light.data.size=5
    light.rotation_euler=(Vector((0,0,1.5))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(6,-8,5)); camera=bpy.context.object; scene.camera=camera
    target=Vector((0,0,2.4 if name=='pine_tree' else (1.35 if name=='sapling' else .45)))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=52
    scene.render.filepath=str(RENDER/(name+'.png')); bpy.ops.render.render(write_still=True)


for name,builder in [('pine_tree',pine_tree),('sapling',sapling),('flowerbed',flowerbed)]:
    clear(); builder()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'.blend')))
    print('NATURE_ASSET_EXPORTED',name)
    render(name)
print('CITY_NATURE_COMPLETE')
