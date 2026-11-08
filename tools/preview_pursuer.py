import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\pursuer_abomination.glb")
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=420; sc.render.resolution_y=420
if sc.world is None: sc.world=bpy.data.worlds.new("W")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.6,0.62,0.65,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=1.0
L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA")); L.data.energy=1500; L.data.size=6; L.location=(3,-4,5)
sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=4.2
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
for tag,z in (("minusZ",-6.0),("plusZ",6.0)):
    cam.location=Vector((0,z,1.9)); cam.rotation_euler=(Vector((0,0,1.7))-cam.location).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\tools\pursuer_%s.png"%tag
    bpy.ops.render.render(write_still=True)
    print("RENDERED",tag)