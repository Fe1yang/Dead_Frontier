import bpy, mathutils
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
# find mesh
mesh=None
for ob in bpy.context.scene.objects:
    if ob.type=="MESH" and ob.name=="HighDetailCharacter":
        mesh=ob
        break
# Build vertex -> dominant group map via vertex_groups
# For each finger group, get its vertices, rotate them around knuckle pivot toward palm
# Finger groups and pivots: use group's vertex centroid closest to wrist as pivot proxy
# Curl axis: world X (lateral) -> rotates tip in Y-Z plane. Palm is -Y for both hands (front of character is -Y in Blender import)
# We curl toward +Y or -Y? Character faces -Y? Let's curl toward -Y (fingertips toward palm front). Sign test by render.
# Use angle 28deg proximal group whole finger as rigid around proximal knuckle
hand_groups = {
  "l": ["index_01_l","middle_01_l","ring_01_l","pinky_01_l","index_02_l","middle_02_l","ring_02_l","pinky_02_l","index_03_l","middle_03_l","ring_03_l","pinky_03_l","index_04_leaf_l","middle_04_leaf_l","ring_04_leaf_l","pinky_04_leaf_l"],
  "r": ["index_01_r","middle_01_r","ring_01_r","pinky_01_r","index_02_r","middle_02_r","ring_02_r","pinky_02_r","index_03_r","middle_03_r","ring_03_r","pinky_03_r","index_04_leaf_r","middle_04_leaf_r","ring_04_leaf_r","pinky_04_leaf_r"],
}
def group_verts(ob, gname):
    if gname not in ob.vertex_groups: return []
    g=ob.vertex_groups[gname]
    return [v for v in ob.data.vertices if g.index in [gg.group for gg in v.groups]]
# get hand joint head positions from armature
arm=None
for ob in bpy.context.scene.objects:
    if ob.type=="ARMATURE": arm=ob
axis=mathutils.Vector((1,0,0))
for side, glist in hand_groups.items():
    # pivot: median head of *_01 bones
    pivots=[]
    for n in glist:
        if n.startswith("index_01") or n.startswith("middle_01") or n.startswith("ring_01") or n.startswith("pinky_01"):
            b=arm.pose.bones.get(n)
            if b: pivots.append(b.head.copy())
    if not pivots: continue
    pivot=sum(pivots, mathutils.Vector())/len(pivots)
    print(side,"pivot",list(pivot))
    for gn in glist:
        for v in group_verts(mesh, gn):
            # rotate toward -Y (palm). Rotating direction vector around X by +angle moves -Z toward -Y? Let's apply -28deg
            # direction from pivot to vert
            d=v.co - pivot
            # Rodrigues around X
            angle=-0.49  # -28 deg
            c=mathutils.Euler((angle,0,0)).to_matrix()
            v.co = pivot + c @ d
        # end
mesh.data.update()
print("curled")
bpy.ops.export_scene.gltf(filepath=r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\renders\riley_test_curl.glb", export_format="GLB", export_yup=True, export_apply=True)
print("exported test")
