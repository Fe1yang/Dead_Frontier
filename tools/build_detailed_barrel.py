import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'barrel.glb'
TEX=ROOT/'assets'/'textures'/'original'/'barrel_paint_original.png'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials): bpy.data.materials.remove(data)

def material(name,color,metal=0.0,rough=.5,texture=None):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=next((n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled'),None)
    if p is None: p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage'); node.image=bpy.data.images.load(str(texture))
        m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    m.diffuse_color=(*color,1)
    return m

paint=material('Original chipped red and ash paint',(.55,.05,.035),.45,.57,TEX)
red=material('Worn red enamel',(.40,.026,.019),.50,.48)
metal=material('Exposed dark rolled steel',(.075,.065,.056),.78,.40)
cream=material('Aged off-white paint',(.53,.51,.41),.28,.64)
black=material('Warning lettering',(.012,.014,.013),.15,.70)
yellow=material('Faded hazard ochre',(.72,.35,.055),.15,.58)

def assign(obj,mat):
    obj.data.materials.append(mat)
    return obj

def smooth(obj):
    if obj.type=='MESH':
        for p in obj.data.polygons: p.use_smooth=True

def cylinder(name,loc,radius,depth,mat,vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; assign(o,mat)
    b=o.modifiers.new('Machined edge bevel','BEVEL'); b.width=.003; b.segments=3
    smooth(o); return o

def torus(name,z,radius,tube,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,location=(0,0,z),major_radius=radius,minor_radius=tube)
    o=bpy.context.object; o.name=name; assign(o,mat); smooth(o); return o

profile=[
(.380,.020),(.425,.030),(.435,.045),(.435,.073),(.410,.095),(.405,.135),
(.420,.153),(.426,.170),(.422,.183),(.405,.205),(.405,.229),
(.420,.246),(.426,.263),(.422,.277),(.405,.300),(.405,.370),
(.426,.391),(.435,.412),(.435,.435),(.425,.451),(.405,.476),
(.405,.520),(.405,.860),(.405,.878),(.425,.899),(.435,.920),(.435,.941),(.426,.958),(.405,.980),
(.405,1.040),(.420,1.058),(.426,1.075),(.422,1.089),(.405,1.112),
(.405,1.148),(.420,1.165),(.426,1.182),(.422,1.196),(.405,1.220),
(.405,1.286),(.420,1.320),(.430,1.350),(.435,1.376),(.430,1.399),(.400,1.414)]
SEG=96; HEIGHT=1.414
verts=[]; faces=[]
for radius,z in profile:
    for i in range(SEG):
        a=i*math.tau/SEG
        dent=.0022*math.sin(a*5+z*3.1)+.0013*math.sin(a*11-z*4.2)
        r=radius+dent
        verts.append((r*math.cos(a),r*math.sin(a),z))
for j in range(len(profile)-1):
    for i in range(SEG):
        k=j*SEG+i; n=j*SEG+(i+1)%SEG
        faces.append((k,n,n+SEG,k+SEG))
mesh=bpy.data.meshes.new('Spun steel shell with rolled ribs'); mesh.from_pydata(verts,[],faces); mesh.update()
body=bpy.data.objects.new('Barrel',mesh); bpy.context.collection.objects.link(body)
body.data.materials.append(paint)
uv=body.data.uv_layers.new(name='Original barrel UV')
for poly in body.data.polygons:
    j=poly.index//SEG
    for li in poly.loop_indices:
        vi=body.data.loops[li].vertex_index; ring=vi//SEG; seg=vi%SEG
        u=seg/SEG; v=profile[ring][1]/HEIGHT
        # Prevent the wrapped face from interpolating a full-width UV seam.
        if poly.loop_indices[0]==li and seg==0: pass
        uv.data[li].uv=(u,v)
smooth(body)
# Separate seam geometry makes barrel fragments useful for the explosion.
for z in (.048,.423,.930,1.389): torus('Ring',z,.427,.012,metal)
cylinder('Cap', (0,0,1.412),.400,.018,red)
torus('CapOuterRolledLip',1.416,.418,.016,metal)
torus('CapPressedSeam',1.425,.372,.0035,red)
cylinder('BottomPlate',(0,0,.023),.389,.014,metal)
for name,x,y,r in [('CapLargeBung',-.175,-.055,.071),('CapSmallBung',.182,.067,.052)]:
    cylinder(name,(x,y,1.435),r,.026,metal,64)
    cylinder(name+'Inset',(x,y,1.451),r*.74,.006,red,64)
    bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=10,major_radius=r*.86,minor_radius=.004,location=(x,y,1.45))
    o=bpy.context.object; o.name=name+'Seal'; assign(o,metal); smooth(o)
    # Real recessed slot on each screw cap.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,1.456))
    o=bpy.context.object; o.name=name+'Slot'; o.dimensions=(r*.82,.011,.004)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,black)
# Small original hazard plate and lettering on the faded band.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.410,.720))
plate=bpy.context.object; plate.name='BarrelWarningPlate'; plate.dimensions=(.225,.008,.170)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(plate,cream)
b=py=plate.modifiers.new('Rounded plate corners','BEVEL'); b.width=.008; b.segments=3

def text(name,body_text,loc,size,mat):
    curve=bpy.data.curves.new(name,'FONT'); curve.body=body_text; curve.align_x='CENTER'; curve.size=size; curve.extrude=.0005
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); assign(o,mat)
    bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.convert(target='MESH'); o.select_set(False)
text('BarrelWarningText','FLAMMABLE',(0,-.417,.664),.030,black)
# Flame-shaped warning pictogram, modelled instead of using the reference texture.
verts=[(-.043,-.418,.797),(0,-.418,.855),(.043,-.418,.797),(.029,-.418,.768),(-.029,-.418,.768)]
mesh=bpy.data.meshes.new('Hazard diamond'); mesh.from_pydata(verts,[],[(0,1,2,3,4)]); mesh.update()
o=bpy.data.objects.new('BarrelHazardDiamond',mesh); bpy.context.collection.objects.link(o); assign(o,yellow)
text('BarrelHazardMark','!',(0,-.421,.782),.057,black)
# Export only the original asset, never the reference package.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True)
print('DETAILED_BARREL_EXPORTED',OUT,'objects',len(bpy.context.scene.objects))
# Preview rig.
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.mesh.primitive_plane_add(size=200)
ground=bpy.context.object; ground.name='PreviewGround'; assign(ground,material('Preview concrete',(.12,.135,.14),0,.82))
bpy.ops.object.light_add(type='AREA',location=(2,-3,4)); key=bpy.context.object; key.data.energy=500; key.data.shape='DISK'; key.data.size=4
key.rotation_euler=(Vector((0,0,.65))-key.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(-3,-1,2)); fill=bpy.context.object; fill.data.energy=260; fill.data.size=3
fill.rotation_euler=(Vector((0,0,.75))-fill.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.25,-3.15,2.30)); camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.73))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=1.90
scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.world.color=(.12,.12,.12); scene.render.resolution_x=800; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
(ROOT/'diagnostics').mkdir(exist_ok=True)
scene.render.filepath=str(ROOT/'diagnostics'/'barrel_detailed.png')
bpy.ops.render.render(write_still=True)
