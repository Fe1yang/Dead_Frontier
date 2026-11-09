import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,"assets","models","generated","zombie_jockey_new_hd.glb"))
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=760; sc.render.resolution_y=560
if sc.world is None: sc.world=bpy.data.worlds.new("W")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.6,0.62,0.66,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=1.1
for loc,en in (((3,-4,4),900),((-3.5,-2,2.5),300),((0,4,3),500)):
    L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA")); L.data.energy=en; L.data.size=5; L.location=loc
    L.rotation_euler=(Vector((0,0,0.5))-Vector(loc)).to_track_quat("-Z","Y").to_euler()
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
cam.location=center+Vector((span*0.4,-span*1.2,span*0.15))
cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
sc.render.filepath=os.path.join(ROOT,"tools","jockey_rest.png")
bpy.ops.render.render(write_still=True)
print("REST_RENDER size", tuple(round(v,2) for v in (hi-lo)))