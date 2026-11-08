import bpy, os, math
from mathutils import Vector
WORK = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(WORK,"survivor_riley_universal.glb"))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=1024; sc.render.resolution_y=1024
sc.render.film_transparent=True; sc.render.image_settings.color_mode="RGBA"
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.5,0.55,0.6,1)
w.node_tree.nodes["Background"].inputs[1].default_value=1.25
def light(name,loc,energy,size,target=(0,0,1.45)):
    L=bpy.data.objects.new(name,bpy.data.lights.new(name,type="AREA"))
    L.data.energy=energy; L.data.size=size; L.location=loc
    L.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L); return L
light("key",(1.8,-2.2,2.4),700,3.0)
light("fill",(-2.2,-1.0,1.6),260,3.5)
light("rim",(-0.6,2.6,2.2),420,2.5)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=2.0
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
r=math.radians(90)
pos=Vector((math.sin(r)*-3.0, math.cos(r)*-3.0, 0.95))
cam.location=pos
cam.rotation_euler=(Vector((0,0,0.95))-pos).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=os.path.join(WORK,"riley_front_full.png")
bpy.ops.render.render(write_still=True)
print("FRONT_RENDERED")