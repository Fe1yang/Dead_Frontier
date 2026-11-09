# Renders a weapon prop to a square store-art PNG (white background, three-quarter view).
import bpy, sys, math
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:]
SRC, OUT = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
for o in meshes:
    for c in o.bound_box:
        w=o.matrix_world @ Vector(c)
        lo=Vector((min(lo.x,w.x),min(lo.y,w.y),min(lo.z,w.z)))
        hi=Vector((max(hi.x,w.x),max(hi.y,w.y),max(hi.z,w.z)))
ctr=(lo+hi)*0.5; size=max((hi-lo).x,(hi-lo).y,(hi-lo).z)
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=512; sc.render.resolution_y=512
sc.render.film_transparent=True
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.93,0.93,0.93,1)
w.node_tree.nodes["Background"].inputs[1].default_value=1.05
for name,loc,energy in (("key",(1.6,-2.2,2.2),420),("fill",(-2.0,-1.4,1.0),200),("rim",(0.4,2.2,2.0),220)):
    L=bpy.data.objects.new(name,bpy.data.lights.new(name,type="AREA"))
    L.data.energy=energy; L.data.size=2.6
    L.location=loc
    L.rotation_euler=(ctr-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=size*1.25
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
d=size*2.2
cam.location=Vector((ctr.x+d*0.62, ctr.y-d*0.72, ctr.z+d*0.34))
cam.rotation_euler=(ctr-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=OUT
bpy.ops.render.render(write_still=True)
print("ART", OUT)
