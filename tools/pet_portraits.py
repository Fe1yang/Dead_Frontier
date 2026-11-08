import bpy, math, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
OUTDIR=os.path.join(ROOT,"assets","ui","pets")
JOBS=[("white_tiger","assets/models/pets/white_tiger.glb"),("lion","assets/models/pets/lion.glb")]
for name,rel in JOBS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,rel.replace("/",os.sep)))
    sc=bpy.context.scene
    sc.render.engine="BLENDER_EEVEE"
    sc.render.resolution_x=760; sc.render.resolution_y=708
    sc.render.film_transparent=True
    sc.render.image_settings.color_mode="RGBA"
    sc.view_settings.exposure=-0.2
    try: sc.view_settings.look="AgX - Punchy"
    except Exception: pass
    if sc.world is None: sc.world=bpy.data.worlds.new("W")
    sc.world.use_nodes=True
    sc.world.node_tree.nodes["Background"].inputs[1].default_value=0.9
    for loc,en,sz in (((2.2,-2.6,2.4),600,4.0),((-2.4,-1.6,1.8),200,4.5),((-0.6,2.6,2.2),320,3.0)):
        L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA"))
        L.data.energy=en; L.data.size=sz; L.location=loc
        L.rotation_euler=(Vector((0,0,0.6))-Vector(loc)).to_track_quat("-Z","Y").to_euler()
        sc.collection.objects.link(L)
    lo=Vector((1e9,1e9,1e9)); hi=Vector((-1e9,-1e9,-1e9))
    for m in [o for o in bpy.context.scene.objects if o.type=="MESH"]:
        for c in m.bound_box:
            p=m.matrix_world @ Vector(c)
            lo=Vector((min(lo.x,p.x),min(lo.y,p.y),min(lo.z,p.z)))
            hi=Vector((max(hi.x,p.x),max(hi.y,p.y),max(hi.z,p.z)))
    center=(lo+hi)*0.5
    span=max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z)*1.18
    cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=span
    cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
    # 3/4 view: to the front-left and slightly above
    cam.location=center+Vector((span*0.55,-span*0.95,span*0.35))
    cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=os.path.join(OUTDIR,name+".png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED",name)