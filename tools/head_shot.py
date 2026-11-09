# Centred head-and-shoulders render of a T-pose actor, white background.
import bpy, sys, os
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:]
SRC, OUT = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
arm.data.pose_position="REST"
body=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]
bpy.context.view_layer.update()
head_i=arm.data.bones.find("Head")
head=arm.matrix_world @ arm.data.bones[head_i].head_local
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"
sc.render.resolution_x=512; sc.render.resolution_y=512
sc.render.film_transparent=True
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
w.node_tree.nodes["Background"].inputs[0].default_value=(0.86,0.86,0.86,1)
w.node_tree.nodes["Background"].inputs[1].default_value=1.1
for name,loc,energy,size in (("key",(1.2,-2.0,head.z+0.35),260,2.4),
                             ("fill",(-1.4,-1.6,head.z+0.15),120,2.4),
                             ("rim",(0.2,1.8,head.z+0.5),140,2.0)):
    L=bpy.data.objects.new(name,bpy.data.lights.new(name,type="AREA"))
    L.data.energy=energy; L.data.size=size
    L.location=loc
    L.rotation_euler=(head-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=0.62
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
target=head+Vector((0,0,-0.10))
cam.location=Vector((head.x, head.y-2.0, head.z-0.02))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=OUT
bpy.ops.render.render(write_still=True)
print("SHOT", OUT)

