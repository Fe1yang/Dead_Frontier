import bpy
glb = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        for mat in ob.data.materials:
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Roughness"].default_value = 0.45
                    # subtle orange-peel via bump from noise
                    tex = mat.node_tree.nodes.new("ShaderNodeTexNoise")
                    tex.inputs["Scale"].default_value = 8.0
                    bump = mat.node_tree.nodes.new("ShaderNodeBump")
                    mat.node_tree.links.new(tex.outputs["Fac"], bump.inputs["Height"])
                    mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, export_apply=True)
print("Ken detail added")
