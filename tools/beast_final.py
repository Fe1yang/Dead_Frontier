import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,"assets","models","actors","pursuer_abomination.glb"))
arm=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"][0]
if arm.animation_data and arm.animation_data.action:
    print("ACTION", arm.animation_data.action.name)
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=520; sc.render.resolution_y=680
if sc.world is None: sc.world=bpy.data.worlds.new("W")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.6,0.62,0.66,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=1.1
for loc,en in (((3,-4,4),800),((-3.5,-2,2.5),260),((0,4,3),420)):
    L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA")); L.data.energy=en; L.data.size=5; L.location=loc
    L.rotation_euler=(Vector((0,0,1.4))-Vector(loc)).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L)
lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
for m in [o for o in bpy.context.scene.objects if o.type=="MESH"]:
    for c in m.bound_box:
        q=m.matrix_world @ Vector(c)
        lo=Vector((min(lo.x,q.x),min(lo.y,q.y),min(lo.z,q.z)))
        hi=Vector((max(hi.x,q.x),max(hi.y,q.y),max(hi.z,q.z)))
center=(lo+hi)*0.5; span=max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z)*1.05
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=span
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
cam.location=center+Vector((span*0.3,-span*1.15,span*0.2))
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=os.path.join(ROOT,"tools","beast_final.png")
bpy.ops.render.render(write_still=True)
print("FINAL_RENDER size", tuple(round(v,2) for v in (hi-lo)))