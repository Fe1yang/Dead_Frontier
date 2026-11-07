
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
obj = bpy.data.objects.get("Safe_wood")
mw = obj.matrix_world
dark_i = 1
groups = collections.defaultdict(lambda: [0,0])
bbox = collections.defaultdict(lambda: [9,9,9,-9,-9,-9])
for poly in obj.data.polygons:
    c = mw @ poly.center
    if not (0.3<=c.x<=2.8 and 0.8<=c.z<=2.8): continue
    key = (round(c.y*4)/4,)
    slot = "DARK" if poly.material_index==dark_i else "pale"
    groups[(key[0],slot)][0]+=1
    b=bbox[(key[0],slot)]
    b[0]=min(b[0],c.x); b[1]=min(b[1],c.y); b[2]=min(b[2],c.z)
    b[3]=max(b[3],c.x); b[4]=max(b[4],c.y); b[5]=max(b[5],c.z)
for k in sorted(groups):
    b=bbox[k]
    print("ROW y=%.2f %s n=%d x %.2f..%.2f z %.2f..%.2f" % (k[0],k[1],groups[k][0],b[0],b[3],b[2],b[5]))
