import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        for v in ob.data.vertices:
            if v.co.z > 1.5:  # head/face region: warm the skin a touch
                v.co.x *= 0.97
        # dark en-bloc hair mass on top (short black crop) via material swap
        for slot in ob.data.materials:
            if slot and "Hair" in slot.name:
                slot.diffuse_color = (0.02, 0.02, 0.02, 1.0)
        ob.data.update()
        for slot in ob.material_slots:
            mat = slot.material
            if mat and "Jacket" in mat.name:
                mat.diffuse_color = (0.10, 0.16, 0.28, 1.0)  # navy courier jacket
                mat.use_nodes = True
                for n in mat.node_tree.nodes:
                    if n.type == "BSDF_PRINCIPLED":
                        n.inputs["Base Color"].default_value = (0.10, 0.16, 0.28, 1.0)
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("Ken recolored")
