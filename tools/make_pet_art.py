import bpy, os, math
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC=os.path.join(ROOT,"assets","models","pets","czech_wolfdog.glb")
OUT=os.path.join(ROOT,"assets","models","pets","_wolf_art.png")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=760; sc.render.resolution_y=708
sc.render.film_transparent=True
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.5,0.52,0.55,1)
w.node_tree.nodes["Background"].inputs[1].default_value=0.9
import mathutils
for name,loc,energy,size in (("key",(2.4,-2.8,2.6),900,3.0),("fill",(-2.6,-1.8,1.6),350,3.0),("rim",(0.5,3.2,2.4),500,2.0)):
    L=bpy.data.objects.new(name,bpy.data.lights.new(name,type="AREA"))
    L.data.energy=energy; L.data.size=size
    L.location=loc
    L.rotation_euler=(Vector((0,0,0.55))-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L)
box=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo=Vector((min(p.x for p in box),min(p.y for p in box),min(p.z for p in box)))
hi=Vector((max(p.x for p in box),max(p.y for p in box),max(p.z for p in box)))
center=(lo+hi)*0.5; size=max((hi-lo).x,(hi-lo).z)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=size*1.35
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
dir3=Vector((0.85,-1.0,0.35)).normalized()
cam.location=center+dir3*4.0
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=OUT
bpy.ops.render.render(write_still=True)
print("ART_RENDERED", OUT)
