import bpy
import math
import random
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'assets'/'models'/'coin_stack.glb'
SOURCE=ROOT/'assets'/'blender'/'coin_stack.blend'
RENDER=ROOT/'diagnostics'/'coin-stack-model.png'
for folder in (MODEL.parent,SOURCE.parent,RENDER.parent): folder.mkdir(parents=True,exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for blocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
    for block in list(blocks):
        if block.users==0: blocks.remove(block)

def linear(v):
    v=v/255
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4

def material(name,color,roughness,metallic):
    rgb=tuple(linear(int(color[i:i+2],16)) for i in (0,2,4))
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    return m

GOLD=material('Coin warm gold','a97924',.48,.58)
EDGE=material('Coin fine edge','8e6222',.50,.55)
RELIEF=material('Coin raised rim','c49a3c',.44,.62)
STAMP=material('Coin stamped star','73501f',.52,.48)

def finish(o,mat,bevel=0):
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Minted soft edge','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted mint normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,radius,depth,loc,mat,vertices=72,bevel=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; finish(o,mat,bevel)
    for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
    return o

def ring(name,radius,minor,z,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=72,minor_segments=8,location=(0,0,z),major_radius=radius,minor_radius=minor)
    o=bpy.context.object; o.name=name; finish(o,mat)
    for p in o.data.polygons: p.use_smooth=True
    return o

def fine_reeding(radius=.145,depth=.020):
    # Tiny flush milling marks, not protruding vertical bars.
    verts=[]; faces=[]
    for i in range(72):
        a=math.tau*i/72; tangent=Vector((-math.sin(a),math.cos(a),0)); radial=Vector((math.cos(a),math.sin(a),0))
        center=radial*radius+Vector((0,0,depth*.5)); n=len(verts)
        for zz in (-depth*.31,depth*.31):
            for rr,tt in ((-.0003,-.00055),(.0007,-.00055),(.0007,.00055),(-.0003,.00055)):
                verts.append(center+radial*rr+tangent*tt+Vector((0,0,zz)))
        faces.extend([tuple(n+j for j in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))])
    data=bpy.data.meshes.new('Flush coin milling mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new('Fine flush edge milling',data); bpy.context.collection.objects.link(o); finish(o,EDGE)

def stamped_star(z=.021):
    points=[]
    for i in range(10):
        a=math.pi/2+math.tau*i/10; r=.061 if i%2==0 else .028
        points.append(Vector((r*math.cos(a),r*math.sin(a),0)))
    verts=[(p.x,p.y,z+dz) for dz in (0,.0025) for p in points]
    faces=[tuple(range(9,-1,-1))]
    for tri in tessellate_polygon([points]):
        # Blender 5.2 returns indices; older releases returned the original vectors.
        faces.append(tuple(10+(v if isinstance(v,int) else min(range(10),key=lambda i:(points[i]-v).length_squared)) for v in tri))
    for i in range(10): faces.append((i,(i+1)%10,(i+1)%10+10,i+10))
    data=bpy.data.meshes.new('Star stamp mesh'); data.from_pydata(verts,[],faces); data.update()
    o=bpy.data.objects.new('Recessed five point star',data); bpy.context.collection.objects.link(o); finish(o,STAMP,.0007)

def make_coin(index,loc,tilt):
    before=set(bpy.context.scene.objects)
    body=cylinder('Coin body',.145,.020,(0,0,.010),GOLD,72,.0018)
    body.data.materials.append(EDGE)
    for poly in body.data.polygons:
        if len(poly.vertices)==4: poly.material_index=1
    fine_reeding(); ring('Fine raised rim',.122,.0018,.0205,RELIEF); stamped_star()
    assembly=bpy.data.objects.new('CoinAssembly_%02d'%index,None); bpy.context.collection.objects.link(assembly)
    for o in set(bpy.context.scene.objects)-before:
        if o!=assembly: o.parent=assembly
    assembly.location=loc; assembly.rotation_euler=tilt

# A low, irregular pile: separate coins overlap at different angles rather than forming a tower.
placements=[
    ((-.18,-.10,.003),(0.03,-.05,.25)),
    (( .02,-.15,.004),(-.03,.04,1.10)),
    (( .19,-.05,.006),(.04,.02,2.05)),
    ((-.13,.10,.009),(-.04,.05,2.75)),
    (( .10,.12,.012),(.05,-.03,.65)),
    ((-.015,.005,.030),(.11,-.08,1.65)),
    (( .035,.045,.051),(-.08,.10,2.35)),
]
for i,(loc,tilt) in enumerate(placements): make_coin(i,loc,tilt)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(MODEL),export_format='GLB',use_selection=True,export_apply=True,export_animations=False)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))

scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.cycles.use_denoising=True
scene.render.resolution_x=700; scene.render.resolution_y=700; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
world=bpy.data.worlds.new('Coin preview world'); world.use_nodes=True; scene.world=world
background=world.node_tree.nodes.get('Background') or world.node_tree.nodes.new('ShaderNodeBackground')
background.inputs['Color'].default_value=(.20,.25,.32,1); background.inputs['Strength'].default_value=.45
output=world.node_tree.nodes.get('World Output') or world.node_tree.nodes.new('ShaderNodeOutputWorld')
world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
floor_mat=material('Preview charcoal','24292d',.88,0)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004)); bpy.context.object.data.materials.append(floor_mat)
for loc,power,size in (((.6,-.7,1.2),145,.8),((-.8,-.1,.7),85,.7),((.3,.8,1.0),110,.6)):
    bpy.ops.object.light_add(type='AREA',location=loc); light=bpy.context.object; light.data.energy=power; light.data.shape='DISK'; light.data.size=size
    light.rotation_euler=(Vector((0,0,.02))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.58,-.78,.68)); camera=bpy.context.object; scene.camera=camera
camera.rotation_euler=(Vector((0,0,.02))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.lens=58
scene.view_settings.view_transform='AgX'; scene.render.filepath=str(RENDER); bpy.ops.render.render(write_still=True)
print('COIN_ASSET_COMPLETE',MODEL,RENDER)
