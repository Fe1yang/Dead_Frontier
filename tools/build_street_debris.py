import bpy
import math
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'props'
TEX=ROOT/'assets'/'textures'/'street_debris'
OUT.mkdir(parents=True,exist_ok=True)
random.seed(741103)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)


def mat(name,color,texture=None,rough=0.85,metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    if texture:
        t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(TEX/texture),check_existing=True)
        m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    return m

concrete=mat('Debris · fractured neutral concrete',(0.48,0.50,0.49),'fractured_concrete.png',0.94)
brick=mat('Debris · broken muted brick',(0.38,0.20,0.15),'broken_brick.png',0.91)
wood=mat('Debris · weathered splintered wood',(0.28,0.21,0.14),'weathered_wood.png',0.88)
paper=mat('Debris · printed evacuation newspaper',(0.7,0.68,0.60),'evacuation_newspaper.png',0.96)
metal=mat('Debris · crushed dull aluminium',(0.42,0.46,0.45),None,0.38,0.78)
label=mat('Debris · faded red can label',(0.30,0.075,0.055),None,0.62,0.18)
dark=mat('Debris · rusty nails',(0.09,0.07,0.05),None,0.66,0.60)


def apply_mod(o,mod):
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=mod.name)


def finish(o,name):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    if o.type=='MESH' and not o.data.uv_layers:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=0.02); bpy.ops.object.mode_set(mode='OBJECT')
    o.name='Debris'
    path=OUT/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
    print('DEBRIS_EXPORTED',name,'verts',len(o.data.vertices),'faces',len(o.data.polygons))
    o.select_set(False)
    return o


def chunk(name,size,material,seed):
    rng=random.Random(seed)
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    be=o.modifiers.new('Chipped edges','BEVEL'); be.width=min(size)*0.15; be.segments=3; apply_mod(o,be)
    su=o.modifiers.new('Fracture tessellation','SUBSURF'); su.subdivision_type='SIMPLE'; su.levels=2; apply_mod(o,su)
    tex=bpy.data.textures.new(name+' fracture',type='CLOUDS'); tex.noise_scale=0.09; tex.noise_depth=2
    dis=o.modifiers.new('Broken irregular surface','DISPLACE'); dis.texture=tex; dis.strength=min(size)*0.22; dis.mid_level=0.52; apply_mod(o,dis)
    de=o.modifiers.new('Remove invisible density','DECIMATE'); de.ratio=0.52; apply_mod(o,de)
    minz=min(v.co.z for v in o.data.vertices)
    for v in o.data.vertices: v.co.z-=minz
    return finish(o,name)


def broken_board():
    rng=random.Random(28)
    length=.84; width=.155; thick=.024
    verts=[]; faces=[]; n=15
    for i in range(n):
        y=-length/2+length*i/(n-1)
        end=(i in (0,n-1))
        half=width/2*(rng.uniform(.58,1.0) if end else rng.uniform(.94,1.02))
        shift=rng.uniform(-.015,.015) if end else 0
        bend=.012*math.sin(i*.42)
        verts.extend([(-half+shift,y,bend),(half+shift,y,bend+.003),(-half+shift,y,bend+thick),(half+shift,y,bend+thick)])
    for i in range(n-1):
        a=i*4; b=(i+1)*4
        faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    faces.extend([(0,1,3,2),((n-1)*4,(n-1)*4+2,(n-1)*4+3,(n-1)*4+1)])
    mesh=bpy.data.meshes.new('Splintered plank mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new('Broken board',mesh); bpy.context.collection.objects.link(o); mesh.materials.append(wood)
    be=o.modifiers.new('Worn splinter edges','BEVEL'); be.width=.0025; be.segments=2; apply_mod(o,be)
    parts=[o]
    for yy in (-.25,.23):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.008,depth=.009,location=(-.035,yy,.030))
        nail=bpy.context.object; nail.data.materials.append(dark); parts.append(nail)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active=o; bpy.ops.object.join()
    return finish(o,'debris_board')


def crushed_can():
    rng=random.Random(82); seg=40; rings=11; h=.145
    verts=[]; faces=[]; mi=[]
    for j in range(rings):
        t=j/(rings-1); z=t*h
        for i in range(seg):
            a=math.tau*i/seg
            dent=.010*math.sin(a*3+t*8)+.005*math.sin(a*7-t*4)
            radius=.044+dent*math.sin(math.pi*t)**1.2
            verts.append((radius*math.cos(a)+.006*math.sin(t*5),radius*math.sin(a),z))
    for j in range(rings-1):
        for i in range(seg):
            a=j*seg+i; b=j*seg+(i+1)%seg; c=(j+1)*seg+(i+1)%seg; d=(j+1)*seg+i
            faces.append((a,b,c,d)); mi.append(1 if 2<=j<=7 else 0)
    faces.append(tuple(reversed(tuple(range(seg))))); mi.append(0)
    faces.append(tuple((rings-1)*seg+i for i in range(seg))); mi.append(0)
    mesh=bpy.data.meshes.new('Crushed can mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new('Crushed can',mesh); bpy.context.collection.objects.link(o)
    mesh.materials.append(metal); mesh.materials.append(label)
    for p,idx in zip(mesh.polygons,mi): p.material_index=idx; p.use_smooth=True
    uv=mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index; j=vi//seg; i=vi%seg
            uv.data[li].uv=(i/seg,j/(rings-1))
    parts=[o]
    for z in (.004,h-.004):
        bpy.ops.mesh.primitive_torus_add(major_radius=.039,minor_radius=.004,major_segments=40,minor_segments=8,location=(0,0,z))
        rim=bpy.context.object; rim.data.materials.append(metal); parts.append(rim)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active=o; bpy.ops.object.join()
    return finish(o,'debris_can')


def newspaper():
    nx=14; ny=18; verts=[]; faces=[]
    for j in range(ny):
        v=j/(ny-1)
        for i in range(nx):
            u=i/(nx-1); x=(u-.5)*.29; y=(v-.5)*.39
            if i in (0,nx-1): x+=random.uniform(-.007,.007)
            if j in (0,ny-1): y+=random.uniform(-.008,.008)
            z=.003+.017*(abs(u-.5)*2)**5+.014*max(0,(v-.72)/.28)**2+.003*math.sin(u*9+v*4)
            verts.append((x,y,z))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i; faces.append((a,a+1,a+1+nx,a+nx))
    mesh=bpy.data.meshes.new('Curled newspaper mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new('Newspaper',mesh); bpy.context.collection.objects.link(o); mesh.materials.append(paper)
    uv=mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index; uv.data[li].uv=((vi%nx)/(nx-1),(vi//nx)/(ny-1))
    for p in mesh.polygons: p.use_smooth=True
    so=o.modifiers.new('Paper thickness','SOLIDIFY'); so.thickness=.0008; apply_mod(o,so)
    return finish(o,'debris_newspaper')

objects=[]
objects.append(chunk('debris_concrete_00',(.29,.23,.14),concrete,10))
objects.append(chunk('debris_concrete_01',(.20,.34,.11),concrete,22))
objects.append(chunk('debris_brick',(.23,.115,.075),brick,35))
objects.append(broken_board())
objects.append(crushed_can())
objects.append(newspaper())
for i,o in enumerate(objects): o.location=(i*.65,0,0)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets'/'blender'/'street_debris.blend'))
print('STREET_DEBRIS_COMPLETE')
