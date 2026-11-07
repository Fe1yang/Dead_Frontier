import bpy
src = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_male_universal.glb"
out = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        for v in ob.data.vertices:
            if v.co.z > 1.42:
                v.co.x *= 0.88
                if v.co.z < 1.52:
                    v.co.x *= 0.82
                if v.co.z > 1.62 and abs(v.co.x) < 0.06:
                    v.co.y += 0.02
        ob.data.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_apply=True)
print("Ken from Mason (high-poly kept)")
