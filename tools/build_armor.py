import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
MODELS=ROOT/'assets'/'models'
SOURCE=ROOT/'assets'/'blender'
RENDERS=ROOT/'renders'
for folder in (MODELS,SOURCE,RENDERS): folder.mkdir(parents=True,exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials): bpy.data.materials.remove(data)
MATS={}

def mat(key,color,rough=0.62,metal=0.0):
    color=color.lstrip('#')
    rgb=tuple(int(color[i:i+2],16)/255 for i in (0,2,4))
    rgba=tuple(c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb)+(1,)
    m=bpy.data.materials.new(key); m.diffuse_color=rgba; m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=rgba; p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal; MATS[key]=m

mat('ceramic','344d56',0.48,0.18); mat('edge','172a31',0.72)
mat('webbing','72806b',0.88); mat('buckles','a7b3a5',0.36,0.65)
mat('mark','d8e5ce',0.65); mat('scratch','627984',0.52,0.25)

def assign(o,key):
    o.data.materials.append(MATS[key]); return o

def cube(name,loc,dims,key,bevel=0.025,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot: o.rotation_euler=rot
    assign(o,key)
    if bevel:
        mod=o.modifiers.new('Rounded armor edges','BEVEL'); mod.width=bevel; mod.segments=3
        mod=o.modifiers.new('Weighted plate normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,radius,depth,key,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name
    if rot: o.rotation_euler=rot
    assign(o,key)
    mod=o.modifiers.new('Edge glint','BEVEL'); mod.width=0.006; mod.segments=2
    return o

def text(name,body,loc,size,key):
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=name; o.data.body=body; o.data.align_x='CENTER'; o.data.align_y='CENTER'
    o.data.size=size; o.data.extrude=0.003; o.data.bevel_depth=0.001; assign(o,key)

# The vest uses the same Blender coordinates as both survivor source models.
# Front faces -Y; glTF export converts it to the survivor's Godot forward axis.
cube('ArmorFrontPlate',(0,-0.315,1.235),(0.55,0.14,0.49),'ceramic',0.055)
cube('ArmorFrontInset',(0,-0.394,1.25),(0.43,0.026,0.32),'edge',0.025)
cube('ArmorChestRidge',(0,-0.414,1.31),(0.36,0.026,0.055),'scratch',0.012)
cube('ArmorBackPlate',(0,0.345,1.24),(0.54,0.13,0.48),'ceramic',0.05)
cube('ArmorBackInset',(0,0.418,1.25),(0.39,0.025,0.30),'edge',0.02)
for side in (-1,1):
    cube('ArmorSide', (side*0.318,0,1.20),(0.095,0.53,0.31),'edge',0.035)
    cube('ArmorShoulderStrap',(side*0.225,0,1.49),(0.095,0.55,0.075),'webbing',0.022)
    cube('ArmorShoulderGuard',(side*0.37,0,1.445),(0.23,0.43,0.13),'ceramic',0.055)
    cube('ArmorFrontBuckle',(side*0.225,-0.322,1.46),(0.12,0.07,0.10),'buckles',0.018)
    cube('ArmorBackBuckle',(side*0.225,0.318,1.46),(0.12,0.07,0.10),'buckles',0.018)
    for z in (1.08,1.19):
        cube('ArmorSideStrap',(side*0.358,0,z),(0.055,0.48,0.055),'webbing',0.014)
    for y in (-0.15,0.15):
        cyl('ArmorRivet',(side*0.20,y,1.535),0.022,0.018,'buckles')
for x in (-0.19,0.19):
    for z in (1.08,1.39): cyl('ArmorPlateBolt',(x,-0.419,z),0.018,0.018,'buckles',(math.pi/2,0,0))
text('ArmorMark','07',(0,-0.432,1.20),0.12,'mark')
for i in range(3):
    cube('ArmorWear',(0.10+i*0.045,-0.431,1.34-i*0.035),(0.12,0.008,0.012),'scratch',0.003,(0,0,-0.35))

bpy.ops.object.select_all(action='SELECT')
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
armor_path=SOURCE/'armor.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(armor_path))
bpy.ops.export_scene.gltf(filepath=str(MODELS/'armor.glb'),export_format='GLB',use_selection=True,export_apply=True)

def render_scene(path,camera_loc,target,scale=2.4):
    scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
    scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.12,0.16,0.18,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.55
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-0.02))
    floor=bpy.context.object; floor.name='PreviewFloor'
    preview_mat=bpy.data.materials.new('Preview floor'); preview_mat.diffuse_color=(0.10,0.13,0.13,1)
    floor.data.materials.append(preview_mat)
    for key,loc,power,size in [('Key',(2,-4,5),650,4),('Fill',(-3,-1,3),400,3),('Rim',(1,3,4),550,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        o=bpy.context.object; o.name=key; o.data.energy=power; o.data.size=size
        o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=camera_loc)
    cam=bpy.context.object; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=scale; scene.camera=cam
    scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)

render_scene(RENDERS/'armor.png',(2.4,-4.0,2.7),(0,0,1.25),1.35)
for asset in ('survivor','survivor_female'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    with bpy.data.libraries.load(str(armor_path),link=False) as (data_from,data_to):
        data_to.objects=[name for name in data_from.objects if name.startswith('Armor')]
    for obj in data_to.objects:
        if obj: bpy.context.collection.objects.link(obj)
    render_scene(RENDERS/(asset+'_armored.png'),(2.5,-4.5,2.6),(0,-0.05,1.12),2.55)
print('ARMOR_MODEL_AND_PREVIEWS_DONE')
