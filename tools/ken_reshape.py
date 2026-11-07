import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        for v in ob.data.vertices:
            # head region: narrow the jaw, widen the eye line slightly
            if v.co.z > 1.42:
                v.co.x *= 0.88
                # taper lower face (jaw)
                if v.co.z < 1.52:
                    v.co.x *= 0.82
                # lift brow a touch, soften nose ridge
                if v.co.z > 1.62 and abs(v.co.x) < 0.06:
                    v.co.y += 0.02
        ob.data.update()
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("Ken reshaped")
