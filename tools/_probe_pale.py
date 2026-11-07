
import bpy, collections
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
obj = bpy.data.objects.get("Safe_wood")
mw = obj.matrix_world
for poly in obj.data.polygons:
    if poly.material_index == 1: continue
    c = mw @ poly.center
    if 0.3<=c.x<=2.8 and 0.5<=c.z<=1.2 and 1.5<=c.y<=3.6:
        print("PALEFACE x %.2f y %.2f z %.2f" % (c.x,c.y,c.z))
