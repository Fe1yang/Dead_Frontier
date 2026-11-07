import bpy
src = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
out = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models\actors\survivor_ken_universal.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
arm = None
for ob in bpy.context.scene.objects:
    if ob.type == "ARMATURE":
        arm = ob
        break
# delete old meshes, keep armature + actions
for ob in list(bpy.context.scene.objects):
    if ob.type == "MESH":
        bpy.data.objects.remove(ob, do_unlink=True)
# --- new cartoon body, correct proportions (head ~1/7.5) ---
def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
    return m

skin = mat("KenSkin", (0.98, 0.76, 0.60))
hair = mat("KenHair", (0.03, 0.03, 0.03))
jacket = mat("KenJacket", (0.10, 0.16, 0.28))
pants = mat("KenPants", (0.16, 0.18, 0.20))
boots = mat("KenBoots", (0.05, 0.04, 0.04))

def add(name, obj, material):
    obj.name = name
    obj.data.materials.append(material)
    if obj.name not in bpy.context.collection.all_objects:
        bpy.context.collection.objects.link(obj)
    return obj

# head: stretched sphere, Asian jaw (narrow chin)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0, 0, 1.62))
head = bpy.context.active_object
head.scale = (1.0, 1.05, 1.25)
add("KenHead", head, skin)
bpy.ops.mesh.primitive_cube_add(size=0.16, location=(0, 0.06, 1.72))
hak = bpy.context.active_object
add("KenHairTop", hak, hair)
# torso
bpy.ops.mesh.primitive_cube_add(size=0.34, location=(0, 0, 1.12))
torso = bpy.context.active_object
torso.scale = (1.05, 0.62, 1.55)
add("KenTorso", torso, jacket)
# limbs as tapered cylinders
for side, x in (("L", -0.21), ("R", 0.21)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.62, location=(x, 0, 1.38))
    arm = bpy.context.active_object
    add(f"KenArm{side}", arm, jacket)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.85, location=(x * 0.55, 0, 0.55))
    leg = bpy.context.active_object
    add(f"KenLeg{side}", leg, pants)
    bpy.ops.mesh.primitive_cube_add(size=0.09, location=(x * 0.55, 0.04, 0.045))
    ft = bpy.context.active_object
    add(f"KenFoot{side}", ft, boots)
# simple weight paint: each new mesh to nearest plausible bone
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        # assign all verts to head bone for head, spine for torso, limbs crude
        vg = "head" if "Head" in ob.name or "Hair" in ob.name else "spine_02"
        ob.vertex_groups.new(name=vg)
        for v in ob.data.vertices:
            ob.vertex_groups[vg].add([v.index], 1.0, "REPLACE")
        bpy.ops.object.select_all(action="DESELECT")
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_apply=True)
print("Ken rebuilt")
