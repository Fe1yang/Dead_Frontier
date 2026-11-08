import bpy, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
for name,rel in (("smg","assets/models/weapons/smg.glb"),("rifle","assets/models/rifle.glb")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,rel.replace("/",os.sep)))
    sc=bpy.context.scene
    sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=900; sc.render.resolution_y=420
    if sc.world is None: sc.world=bpy.data.worlds.new("W")
    sc.world.use_nodes=True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.5,0.5,0.53,1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value=1.3
    L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA")); L.data.energy=2500; L.data.size=8
    L.location=(3,-6,5); L.rotation_euler=(Vector((0,0,0))-Vector((3,-6,5))).to_track_quat("-Z","Y").to_euler()
    sc.collection.objects.link(L)
    box=bpy.types.Object
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
    for m in meshes:
        for c in m.bound_box:
            p=m.matrix_world @ Vector(c)
            lo=Vector((min(lo.x,p.x),min(lo.y,p.y),min(lo.z,p.z)))
            hi=Vector((max(hi.x,p.x),max(hi.y,p.y),max(hi.z,p.z)))
    center=(lo+hi)*0.5; span=max(hi.x-lo.x,hi.z-lo.z,0.01)
    cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=span*1.25
    cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
    cam.location=center+Vector((4.0,0,0.0))
    cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=os.path.join(ROOT,"tools","wpn_%s.png"%name)
    bpy.ops.render.render(write_still=True)
    print("RENDERED",name,"span",round(span,2))