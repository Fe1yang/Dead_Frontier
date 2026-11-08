import bpy, os, math
from mathutils import Vector
WORK = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(WORK,"survivor_riley_universal.glb"))
sc = bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=256; sc.render.resolution_y=256
sc.render.film_transparent=True
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.45,0.5,0.55,1)
w.node_tree.nodes["Background"].inputs[1].default_value=1.2
L=bpy.data.objects.new("k",bpy.data.lights.new("k",type="AREA")); L.data.energy=600; L.data.size=3
L.location=(1.5,-2.5,2.2); L.rotation_euler=(Vector((0,0,1.5))-Vector(L.location)).to_track_quat("-Z","Y").to_euler()
sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=0.95
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
for ang,name in ((0,"0"),(90,"90"),(180,"180"),(270,"270")):
    r=math.radians(ang)
    pos=Vector((math.sin(r)*-3.0, math.cos(r)*-3.0, 1.55))
    cam.location=pos
    cam.rotation_euler=(Vector((0,0,1.5))-pos).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=os.path.join(WORK,"angle_%s.png"%name)
    bpy.ops.render.render(write_still=True)
    print("ANGLE", name)