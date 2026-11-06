import bpy
import numpy as np
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODELS=ROOT/'assets'/'models'
SOURCE=ROOT/'assets'/'blender'
TEXTURES=ROOT/'assets'/'textures'
for p in (MODELS,SOURCE,TEXTURES): p.mkdir(parents=True,exist_ok=True)
random.seed(311)
MATS={}

def rgba(color):
    color=color.lstrip('#'); vals=[int(color[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in vals)+(1,)

def mat(name,color,texture=None):
    if name in MATS: return MATS[name]
    m=bpy.data.materials.new(name); m.diffuse_color=rgba(color); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=rgba(color); p.inputs['Roughness'].default_value=0.94
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage'); node.image=texture; m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
        m.diffuse_color=(1,1,1,1)
    MATS[name]=m; return m

def cube(name,loc,dims,material,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Small painted bevel','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def asphalt_image():
    path=TEXTURES/'asphalt_comic.png'
    rng=np.random.default_rng(93); size=512
    coarse=rng.normal(0,4.0,(32,32))
    noise=np.repeat(np.repeat(coarse,16,axis=0),16,axis=1)+rng.normal(0,3.2,(size,size))
    base=np.zeros((size,size,4),dtype=np.float32)
    for c,v in enumerate((74,79,80)): base[:,:,c]=np.clip((v+noise)/255,0,1)
    base[:,:,3]=1
    # Tiny aggregate flecks, deliberately no long black cracks.
    for _ in range(2100):
        x=int(rng.integers(0,size)); y=int(rng.integers(0,size)); r=int(rng.integers(1,3))
        value=float(rng.choice([-1,1])*rng.uniform(8,18))
        for c in range(3): base[max(0,y-r):min(size,y+r),max(0,x-r):min(size,x+r),c]=np.clip(base[max(0,y-r):min(size,y+r),max(0,x-r):min(size,x+r),c]+value/255,0,1)
    image=bpy.data.images.new('asphalt_comic',width=size,height=size,alpha=True)
    image.pixels.foreach_set(base.ravel()); image.filepath_raw=str(path); image.file_format='PNG'; image.save(); image.pack()
    return image

def road(texture):
    o=cube('Road',(0,0,-0.11),(8,16,0.22),mat('asphalt_comic','#4a4f50',texture),0.015)
    uv=o.data.uv_layers.active
    for poly in o.data.polygons:
        for li in poly.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(co.x/4.0,co.y/4.0)
    line=mat('road_paint','c8c7ad')
    curb=mat('curb','85857b'); walk=mat('sidewalk','6f716c'); seam=mat('sidewalk_ink','4a4e4c')
    for side in (-1,1):
        cube('Curb',(side*4.22,0,0.04),(0.42,16,0.28),curb,0.025)
        cube('Sidewalk',(side*6.20,0,-0.005),(3.55,16,0.19),walk,0.015)
        cube('EdgeLine',(side*3.72,0,0.012),(0.09,16,0.018),line)
        for y in (-8,-4,0,4,8): cube('PavementJoint',(side*6.20,y,0.096),(3.45,0.025,0.008),seam)
    for y in (-6,-2,2,6): cube('Dash',(0,y,0.015),(0.12,3.2,0.025),line)

def building(side,y,width,depth,height,color,index):
    wall=mat('wall_'+color,color); dark=mat('window_ink','283337'); glass=mat('window_glass','50666b')
    frame=mat('window_frame','a09a88'); roof=mat('roof_'+color,color); metal=mat('painted_metal','525b5d')
    x=side*(8.1+width/2)
    cube('Building',(x,y,height/2+0.1),(width,depth,height),wall,0.045)
    # Flat roof and a normal parapet: no floating or tilted fragments.
    cube('Roof',(x,y,height+0.10),(width+0.08,depth+0.08,0.20),roof,0.02)
    for xx in (x-width/2,x+width/2): cube('Parapet',(xx,y,height+0.34),(0.14,depth,0.42),wall,0.015)
    for yy in (y-depth/2,y+depth/2): cube('Parapet',(x,yy,height+0.34),(width,0.14,0.42),wall,0.015)
    cube('RoofVent',(x-side*0.6,y+0.7,height+0.46),(0.9,1.1,0.65),metal,0.035)
    for k in range(4): cube('VentSlat',(x-side*1.06,y+0.35+k*0.20,height+0.47),(0.025,0.09,0.40),dark)
    front_x=side*8.08
    rows=max(2,int((height-1.8)/1.65)); cols=max(2,int(depth/1.6))
    for row in range(rows):
        z=2.25+row*1.55
        for col in range(cols):
            yy=y-depth*0.39+col*(depth*0.78/max(1,cols-1))
            cube('WindowFrame',(front_x,yy,z),(0.08,0.80,1.00),frame,0.01)
            cube('Window',(front_x-side*0.048,yy,z),(0.035,0.65,0.84),dark if (row+col+index)%4==0 else glass,0.008)
            cube('WindowMullion',(front_x-side*0.07,yy,z),(0.025,0.035,0.84),frame)
    # Front-facing facade windows make the streets read as buildings, not slabs.
    for row in range(rows):
        for col in range(2):
            xx=x+(col-0.5)*width*0.42; z=2.25+row*1.55
            cube('EndWindowFrame',(xx,y+depth/2+0.018,z),(0.78,0.06,1.0),frame,0.01)
            cube('EndWindow',(xx,y+depth/2+0.055,z),(0.63,0.025,0.83),glass if (row+col)%3 else dark)
    cube('DoorFrame',(front_x-side*0.025,y,1.18),(0.12,1.25,2.20),frame,0.01)
    cube('Door',(front_x-side*0.09,y,1.15),(0.05,1.05,2.0),dark,0.01)
    cube('DoorGlass',(front_x-side*0.125,y,1.48),(0.025,0.74,0.83),glass)
    # A few boarded windows and wall marks, not random geometry on the roof.
    if index%2==0:
        for dz in (-0.15,0.15):
            o=cube('Board',(front_x-side*0.13,y-depth*0.39,2.25+dz),(0.07,0.91,0.13),mat('old_wood','665747'),0.008)
            o.rotation_euler.x=0.16 if dz>0 else -0.13

def join_by_material():
    groups={}
    for o in list(bpy.context.scene.objects):
        if o.type!='MESH': continue
        key=o.data.materials[0].name if o.data.materials else 'none'
        groups.setdefault(key,[]).append(o)
    for key,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects: o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1: bpy.ops.object.join()
        bpy.context.object.name='CITY_'+key

texture=asphalt_image()
for variant in range(3):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    MATS.clear()
    road(texture)
    heights=[8.5,11.0,12.0,8.0,9.5,13.5]
    colors=['74766f','6b7476','82766b','69716e']
    for side in (-1,1):
        for j,y in enumerate((-4.05,4.05)):
            h=heights[(variant+j+(1 if side>0 else 0))%3]+(0.7 if side>0 else 0)
            building(side,y,random.uniform(4.0,5.8),7.45,h,colors[(variant*2+j+(1 if side>0 else 0))%len(colors)],variant+j)
    join_by_material()
    name='city_block_'+chr(97+variant)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(MODELS/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(name+'.blend')))
    print('CITY_BLOCK_EXPORTED',name,len(bpy.context.scene.objects))
print('COMIC_ENVIRONMENT_DONE')
