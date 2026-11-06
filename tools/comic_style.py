import bpy
import bmesh
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets'/'blender'
MODELS=ROOT/'assets'/'models'
RENDERS=ROOT/'renders'
RENDERS.mkdir(exist_ok=True)

INK=(0.012,0.016,0.018,1)

def linear_hex(value):
    value=value.lstrip('#')
    rgb=tuple(int(value[i:i+2],16)/255 for i in (0,2,4))
    return tuple(c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb)+(1,)

def material(name,color):
    m=bpy.data.materials.get(name)
    if not m:
        m=bpy.data.materials.new(name); m.use_nodes=True
    rgba=linear_hex(color)
    m.diffuse_color=rgba
    p=next((n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled'),None)
    if p:
        p.inputs['Base Color'].default_value=rgba
        p.inputs['Roughness'].default_value=0.82
    return m

def assign(o,m):
    o.data.materials.clear(); o.data.materials.append(m)

def smooth_mesh(o,bevel=0.025,sub=1):
    if o.type!='MESH': return
    bpy.context.view_layer.objects.active=o
    if bevel:
        mod=o.modifiers.new('Comic rounded silhouette','BEVEL'); mod.width=bevel; mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if sub:
        mod=o.modifiers.new('Organic comic volume','SUBSURF'); mod.levels=sub; mod.render_levels=sub
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons: p.use_smooth=True

def stroke(name,points,radius=0.007,mat=None,parent=None):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'; curve.resolution_u=2
    curve.bevel_depth=radius; curve.bevel_resolution=2
    spline=curve.splines.new('POLY'); spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o)
    if mat: curve.materials.append(mat)
    if parent:
        bpy.context.view_layer.update(); world=o.matrix_world.copy(); o.parent=parent; o.matrix_world=world
    return o

def add_ink_details(asset,ink):
    # Graphic-novel crease lines are geometry, so they also survive glTF export.
    for side in (-1,1):
        x=side*0.15
        stroke('ComicCheek',[(x*0.65,-0.239,1.70),(x,-0.247,1.675),(x*1.12,-0.224,1.65)],0.006,ink)
        stroke('ComicBrowInk',[(x-0.052,-0.249,1.818),(x,-0.254,1.84),(x+0.052,-0.239,1.825)],0.008,ink)
        stroke('ComicJacketFold',[(side*0.28,-0.205,1.37),(side*0.24,-0.227,1.26),(side*0.27,-0.223,1.18)],0.008,ink)
        stroke('ComicElbowFold',[(side*0.37,-0.33,1.23),(side*0.33,-0.36,1.20)],0.007,ink)
        leg=bpy.data.objects.get('LegL' if side<0 else 'LegR')
        stroke('ComicTrouserSeam',[(side*0.265,-0.07,0.78),(side*0.26,-0.09,0.48),(side*0.25,-0.10,0.24)],0.006,ink,leg)
    stroke('ComicNoseInk',[(-0.045,-0.272,1.70),(0,-0.286,1.68),(0.045,-0.272,1.70)],0.005,ink)
    if asset.startswith('zombie'):
        stroke('ComicFaceWound',[(-0.16,-0.22,1.84),(-0.11,-0.25,1.76),(-0.15,-0.24,1.69)],0.012,material('wound_ink','541d20'))
        for i in range(3):
            stroke('ComicRibInk',[(-0.18+i*0.13,-0.256,1.30),(-0.14+i*0.13,-0.267,1.17)],0.009,ink)
    if asset=='survivor_female':
        for i in range(5):
            x=-0.17+i*0.085
            stroke('ComicHairInk',[(x,-0.11,2.00),(x*0.85,-0.21,1.92),(x*0.8,-0.23,1.86)],0.006,ink)
    if asset=='survivor':
        for i in range(7):
            x=-0.13+i*0.043
            stroke('ComicStubble',[(x,-0.232,1.60),(x+0.006,-0.237,1.575)],0.004,ink)

def toon_material(original):
    name=original.name+'_COMIC'
    if bpy.data.materials.get(name): return bpy.data.materials[name]
    m=bpy.data.materials.new(name); m.use_nodes=True
    base=tuple(original.diffuse_color)
    m.diffuse_color=base
    n=m.node_tree.nodes; n.clear(); l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial'); out.location=(620,40)
    emission=n.new('ShaderNodeEmission'); emission.location=(420,40); emission.inputs['Strength'].default_value=1.0
    diffuse=n.new('ShaderNodeBsdfDiffuse'); diffuse.location=(-560,100); diffuse.inputs['Color'].default_value=(0.8,0.8,0.8,1)
    diffuse.inputs['Roughness'].default_value=0.8
    rgb=n.new('ShaderNodeShaderToRGB'); rgb.location=(-360,100)
    ramp=n.new('ShaderNodeValToRGB'); ramp.location=(-160,100); ramp.color_ramp.interpolation='CONSTANT'
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    stops=[(0.0,0.25),(0.23,0.52),(0.56,0.82),(0.82,1.0)]
    ramp.color_ramp.elements[0].position=stops[0][0]; ramp.color_ramp.elements[0].color=(stops[0][1],)*3+(1,)
    for pos,value in stops[1:]:
        e=ramp.color_ramp.elements.new(pos); e.color=(value,value,value,1)
    mix=n.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1.0; mix.inputs[2].default_value=base; mix.location=(180,40)
    l.new(diffuse.outputs[0],rgb.inputs[0]); l.new(rgb.outputs[0],ramp.inputs[0]); l.new(ramp.outputs[0],mix.inputs[1]); l.new(mix.outputs[0],emission.inputs[0]); l.new(emission.outputs[0],out.inputs[0])
    return m

def outline_material():
    m=bpy.data.materials.new('COMIC_OUTLINE'); m.use_nodes=True; m.diffuse_color=INK
    m.use_backface_culling=True
    n=m.node_tree.nodes; n.clear(); out=n.new('ShaderNodeOutputMaterial'); em=n.new('ShaderNodeEmission'); em.inputs[0].default_value=INK; em.inputs[1].default_value=1.0
    m.node_tree.links.new(em.outputs[0],out.inputs[0]); return m

def add_outline(o,mat,thickness=0.012):
    if o.type!='MESH' or max(o.dimensions)<0.13: return
    if o.name.startswith(('ComicInk','ComicCheek','ComicBrow','ComicNose','ComicStubble','ComicHair','ComicRib')): return
    dup=o.copy(); dup.data=o.data.copy(); dup.name='INK_HULL_'+o.name; bpy.context.collection.objects.link(dup)
    dup.data.materials.clear(); dup.data.materials.append(mat)
    for v in dup.data.vertices: v.co+=v.normal*thickness
    bm=bmesh.new(); bm.from_mesh(dup.data); bmesh.ops.reverse_faces(bm,faces=list(bm.faces)); bm.to_mesh(dup.data); bm.free()
    for p in dup.data.polygons: p.use_smooth=False

def setup_render(asset):
    scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.15,0.18,0.20,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0.5
    bpy.ops.object.light_add(type='SUN',location=(2,-4,6)); sun=bpy.context.object; sun.name='ComicSun'; sun.data.energy=2.0; sun.data.angle=0.06
    sun.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-28))
    bpy.ops.object.camera_add(location=(2.7,-5.2,2.65)); cam=bpy.context.object
    cam.rotation_euler=(Vector((0,-0.08,1.07))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO'; cam.data.ortho_scale=2.55; scene.camera=cam
    scene.render.resolution_x=720; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'; scene.view_settings.exposure=0; scene.view_settings.gamma=1
    scene.render.filepath=str(RENDERS/(asset+'_comic.png'))

for asset in ('survivor','survivor_female','zombie_walker'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    # Mature, muted graphic-novel palette instead of toy-like saturated plastic.
    palette={'lime':'8b9b63','lime_dark':'58654c','skin':'c58e68','jacket':'824e48','jacket_dark':'533a3a','hair':'352d29','zskin':'82936b','zskin_dark':'58684f'}
    for name,color in palette.items():
        if bpy.data.materials.get(name): material(name,color)
    for o in list(bpy.context.scene.objects):
        if o.name.startswith('Comic'): bpy.data.objects.remove(o,do_unlink=True)
    for name in ('Torso','LegL','LegR','HairMass','Ponytail','ArmL','ArmR','ForearmL','ForearmR'):
        o=bpy.data.objects.get(name)
        if o: smooth_mesh(o,0.018 if name.startswith(('Leg','Arm','Fore')) else 0.028,1)
    ink=material('comic_ink','171a1c')
    add_ink_details(asset,ink)
    # Convert the new ink curves and apply all remaining modifiers for mobile glTF.
    bpy.ops.object.select_all(action='DESELECT')
    for o in list(bpy.context.scene.objects):
        if o.type not in ('MESH','CURVE'): continue
        bpy.context.view_layer.objects.active=o; o.select_set(True)
        if o.type=='CURVE': bpy.ops.object.convert(target='MESH')
        for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
        o.select_set(False)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(MODELS/(asset+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(asset+'.blend')))
    base_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in base_meshes:
        if not o.data.materials or o.data.materials[0] is None:
            assign(o,material('comic_fallback','6b7069'))
        original=o.data.materials[0]
        assign(o,toon_material(original))
    outline=outline_material()
    for o in base_meshes: add_outline(o,outline,0.009 if o.name.startswith('Detail') else 0.013)
    setup_render(asset)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/('comic_'+asset+'.blend')))
    bpy.ops.render.render(write_still=True)
    print('COMIC_RENDERED',asset)
print('COMIC_SAMPLES_DONE')
