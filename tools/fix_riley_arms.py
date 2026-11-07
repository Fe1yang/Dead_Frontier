import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_riley_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        for v in ob.data.vertices:
            # restore front-back depth on torso (was flattened 0.88)
            if v.co.z > 0.6 and v.co.z < 1.9:
                v.co.y *= 1.12
            # lengthen forearms slightly: pull hand verts further down
            if v.co.z < 0.75 and abs(v.co.x) > 0.22:
                v.co.z *= 1.12
        ob.data.update()
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("Riley depth+forearm fixed")
