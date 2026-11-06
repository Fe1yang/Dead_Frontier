import bpy, sys

# Inspect pursuer_abomination.glb: material base-color factors, vertex-color use, textures.
path = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\pursuer_abomination.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)

print("=== MATERIALS ===")
for mat in bpy.data.materials:
    if not mat.use_nodes:
        print(mat.name, "no nodes")
        continue
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bc = bsdf.inputs["Base Color"]
        print(mat.name, "| base factor:", [round(c, 3) for c in bc.default_value], "| linked:", bc.is_linked)
        if bc.is_linked:
            src = bc.links[0].from_node
            print("   linked from:", src.type, getattr(src, "image", None).name if src.type == "TEX_IMAGE" and src.image else "")
            # walk through mix/multiply nodes that could darken
            n = src
            while n and n.type != "TEX_IMAGE":
                if n.type == "MIX":
                    print("   MIX fac:", round(n.inputs["Factor"].default_value, 3))
                n = n.inputs[1].links[0].from_node if n.inputs[1].is_linked else None
    vc = [n for n in mat.node_tree.nodes if n.type == "VERTEX_COLOR"]
    for n in vc:
        print("   VERTEX COLOR node:", n.name, "layer:", n.layer_name)

print("=== VERTEX COLOR LAYERS ===")
for ob in bpy.data.objects:
    if ob.type == "MESH":
        me = ob.data
        cas = list(me.color_attributes)
        if cas:
            # average luminance of the first color attribute
            ca = cas[0]
            total = [0.0, 0.0, 0.0]
            n = len(me.loops)
            step = max(1, n // 2000)
            cnt = 0
            data = ca.data
            for i in range(0, n, step):
                c = data[i].color
                total[0] += c[0]; total[1] += c[1]; total[2] += c[2]; cnt += 1
            print(ob.name, "| attr:", ca.name, "| avg rgb:", [round(t / cnt, 3) for t in total])
        else:
            print(ob.name, "| no color attributes")

print("=== IMAGES ===")
for img in bpy.data.images:
    print(img.name, img.size[0], "x", img.size[1], "| packed:", img.packed_file is not None)
