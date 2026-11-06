import bpy
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'models'/'rifle.glb'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color,metal):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=0.42
    return m
steel=material('Blued steel',(0.035,0.045,0.052),0.75)
edge=material('Worn metal',(0.20,0.23,0.24),0.65)
polymer=material('Polymer',(0.055,0.065,0.060),0.05)

def box(name,loc,dims,mat,bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
    b=o.modifiers.new('Bevel','BEVEL'); b.width=bevel; b.segments=3
    return o

def cylinder(name,loc,radius,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=loc,rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=name; o.data.materials.append(mat)
    b=o.modifiers.new('Bevel','BEVEL'); b.width=0.008; b.segments=2
    return o

box('Receiver',(0,0,0),(0.19,0.43,0.17),steel)
box('Stock',(0,0.32,0.015),(0.17,0.32,0.19),polymer)
box('Handguard',(0,-0.34,0),(0.17,0.30,0.14),polymer)
box('TopRail',(0,-0.06,0.115),(0.13,0.55,0.045),edge,0.007)
box('Sight',(0,-0.12,0.18),(0.10,0.13,0.10),steel)
box('Magazine',(0,0.06,-0.19),(0.13,0.17,0.28),polymer,0.025)
box('Foregrip',(0,-0.32,-0.14),(0.10,0.11,0.20),polymer,0.02)
cylinder('Barrel',(0,-0.61,0.015),0.035,0.32,edge)
cylinder('Muzzle',(0,-0.79,0.015),0.052,0.09,steel)
for y in (-0.42,-0.34,-0.26): box('HandguardVent',(0.088,y,0),(0.012,0.045,0.055),steel,0.003)
for i in range(7): box('RailTooth',(0,-0.30+i*0.08,0.15),(0.15,0.035,0.025),edge,0.004)
bpy.ops.object.select_all(action='SELECT')
for o in bpy.context.scene.objects:
    bpy.context.view_layer.objects.active=o
    for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True)
print('WEAPON_EXPORTED',OUT)
