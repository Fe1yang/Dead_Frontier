import bpy, math, os
from mathutils import Vector
ROOT=r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
OUT=os.path.join(ROOT,"tools","weapon_sheet.png")
items=[("rifle", "assets/models/rifle.glb"),("smg","assets/models/weapons/smg.glb"),
       ("shotgun","assets/models/weapons/shotgun.glb"),("sniper","assets/models/weapons/sniper.glb"),
       ("pistol","assets/models/weapons/pistol.glb"),("launcher","assets/models/weapons/launcher.glb")]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.render.engine="BLENDER_EEVEE"; sc.render.resolution_x=1000; sc.render.resolution_y=560
sc.render.film_transparent=False
if sc.world is None: sc.world=bpy.data.worlds.new("W")
sc.world.use_nodes=True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.55,0.55,0.58,1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=1.2
L=bpy.data.objects.new("L",bpy.data.lights.new("L",type="AREA")); L.data.energy=2000; L.data.size=8
L.location=(4,-6,6); L.rotation_euler=(Vector((0,0,0))-Vector((4,-6,6))).to_track_quat("-Z","Y").to_euler()
sc.collection.objects.link(L)
cd=bpy.data.cameras.new("c"); cd.type="ORTHO"; cd.ortho_scale=2.2
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
cam.location=Vector((0,-6,1.0)); cam.rotation_euler=(Vector((0,0,0.4))-cam.location).to_track_quat("-Z","Y").to_euler()
# grid: 3 columns x 2 rows, each weapon scaled to ~1.6 m long
for idx,(name,rel) in enumerate(items):
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,rel.replace("/",os.sep)))
    new=[o for o in bpy.context.scene.objects if o.type=="MESH" and o.name.startswith("Cube")==False]
    # take whatever meshes appeared last
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    meshes=[m for m in meshes if not m.name.startswith("L")]
    obj=meshes[-1] if meshes else None
    if obj is None: continue
    col=idx%3; row=idx//3
    box=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    size=max(max(p.x for p in box)-min(p.x for p in box),
             max(p.z for p in box)-min(p.z for p in box), 0.001)
    k=1.7/size
    obj.scale=obj.scale*k
    obj.location=Vector(((col-1)*1.9, 0.0, 0.9-(row*1.0)))
    print("PLACED",name)
sc.render.filepath=OUT
bpy.ops.render.render(write_still=True)
print("SHEET",OUT)