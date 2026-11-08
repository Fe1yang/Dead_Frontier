import bpy, math, sys
from mathutils import Vector
OUT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\tools\cabin_preview.png"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\environment\survival_cabin.glb")
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=540; sc.render.resolution_y=960
sc.render.film_transparent=False
if sc.world is None: sc.world=bpy.data.worlds.new("W")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.05,0.06,0.07,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=0.4
# the glTF import is Y-up rotated: work in world space, camera at -Z? just try the open side
for loc,energy in (((0,0,3.2),900),((0,-2,2.4),500),((0,2,2.4),500)):
    L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA")); L.data.energy=energy; L.data.size=4
    L.location=loc; L.rotation_euler=(Vector((0,0,1.4))-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.lens=35
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
target=Vector((0,0,1.4))
for tag,pos in (("A",(0,7.2,1.7)),("B",(0,-7.2,1.7))):
    pos=Vector(pos)
    cam.location=pos
    cam.rotation_euler=(target-pos).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=OUT.replace(".png","_%s.png"%tag)
    bpy.ops.render.render(write_still=True)
    print("RENDERED",tag,sc.render.filepath)