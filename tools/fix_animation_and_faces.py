import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets'/'blender'
MODELS=ROOT/'assets'/'models'
RENDERS=ROOT/'renders'

def parent_keep_world(obj,parent):
    world=obj.matrix_world.copy(); obj.parent=parent; obj.matrix_world=world

def get_mat(name,color):
    m=bpy.data.materials.get(name)
    if m: return m
    color=color.lstrip('#'); rgb=tuple(int(color[i:i+2],16)/255 for i in (0,2,4))
    rgba=tuple(c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb)+(1,)
    m=bpy.data.materials.new(name); m.diffuse_color=rgba; m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled'); p.inputs['Base Color'].default_value=rgba
    return m

def sphere(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(get_mat(mat,'302820'))
    for p in o.data.polygons: p.use_smooth=True
    return o

def round_limb(name):
    o=bpy.data.objects.get(name)
    if not o or o.type!='MESH': return
    bpy.context.view_layer.objects.active=o
    bevel=o.modifiers.new('Rounded limb silhouette','BEVEL'); bevel.width=0.045; bevel.segments=3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    sub=o.modifiers.new('Soft arm volume','SUBSURF'); sub.levels=2; sub.render_levels=2
    bpy.ops.object.modifier_apply(modifier=sub.name)
    for p in o.data.polygons: p.use_smooth=True

def render(name):
    scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=40; scene.cycles.use_denoising=True
    scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.20,0.24,0.26,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.6
    for key,loc,power,size in [('Key',(2,-4,5),700,4),('Fill',(-3,-1,3),450,3),('Rim',(1,3,4),500,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        o=bpy.context.object; o.name=key; o.data.energy=power; o.data.size=size
        o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(2.5,-4.5,2.6))
    cam=bpy.context.object; cam.rotation_euler=(Vector((0,-0.05,1.12))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=2.55; scene.camera=cam
    scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(RENDERS/(name+'.png'))
    bpy.ops.render.render(write_still=True)

for asset in ('survivor','survivor_female','zombie_walker','zombie_runner','zombie_brute'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    bpy.context.view_layer.update()
    for side in ('L','R'):
        leg=bpy.data.objects.get('Leg'+side)
        if not leg: continue
        for o in list(bpy.context.scene.objects):
            if o==leg: continue
            is_boot=o.name.startswith('Boot'+side) or o.name.startswith('KneeFold'+side)
            is_detail=(o.name.startswith('DetailBoot') or o.name.startswith('DetailKneePad') or o.name.startswith('DetailCargoPocket')) and (o.location.x<0 if side=='L' else o.location.x>=0)
            if is_boot or is_detail: parent_keep_world(o,leg)
    if asset in ('survivor','survivor_female'):
        for name in ('ArmL','ArmR','ForearmL','ForearmR'): round_limb(name)
        head=bpy.data.objects.get('Head')
        if head:
            for p in head.data.polygons: p.use_smooth=True
            bpy.context.view_layer.objects.active=head
            sub=head.modifiers.new('Smooth facial silhouette','SUBSURF'); sub.levels=2; sub.render_levels=2
            bpy.ops.object.modifier_apply(modifier=sub.name)
        if asset=='survivor':
            sphere('DetailBackHair',(0,0.17,1.77),(0.225,0.105,0.18),'hair')
            for x in (-0.15,-0.05,0.05,0.15): sphere('DetailNape',(x,0.18,1.64),(0.065,0.065,0.10),'hair')
        else:
            # Slimmer smooth face and a lifted fringe that does not hide the eyes.
            if head: head.scale=(0.92,0.95,1.0)
            for o in bpy.context.scene.objects:
                if o.name.startswith('FemaleFringe') and o.type=='MESH':
                    for v in o.data.vertices:
                        if v.co.z<1.83: v.co.z+=0.055
            cheek_mat=get_mat('cheek','c98573')
            for x in (-0.15,0.15):
                o=sphere('DetailCheek',(x,-0.218,1.66),(0.055,0.012,0.026),'cheek')
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(MODELS/(asset+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    print('ANIMATION_HIERARCHY_FIXED',asset)
    if asset in ('survivor','survivor_female'): render(asset)
print('ALL_RIG_HIERARCHIES_FIXED')
