import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'assets' / 'models'
SOURCE = ROOT / 'assets' / 'blender'
RENDERS = ROOT / 'renders'
for folder in (MODELS, SOURCE, RENDERS):
    folder.mkdir(parents=True, exist_ok=True)

MATS = {}

def linear(v):
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

def material(key, color, rough=0.65, metal=0.0):
    rgb = tuple(linear(int(color[i:i+2], 16)) for i in (0, 2, 4))
    m = bpy.data.materials.new(key)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    MATS[key] = m
    return m

material('装备 · 橄榄绿织物', '4f5b46', 0.91)
material('装备 · 深色织带', '202a27', 0.94)
material('装备 · 插板涂层', '34464a', 0.53, 0.12)
material('装备 · 软袋滚边', '66715a', 0.86)
material('通用 · 哑黑橡胶', '151c1c', 0.89)
material('通用 · 磨旧钢件', '858e88', 0.34, 0.72)
material('通用 · 深色金属', '293233', 0.43, 0.63)
material('装备 · 缝线', 'a2aa8c', 0.93)
material('装备 · 识别标记', 'd3dbc2', 0.74)
material('头盔 · 磨砂涂层', '465347', 0.72, 0.06)
material('头盔 · 侧导轨', '252f2c', 0.61, 0.15)
material('医疗包 · 米灰织物', 'c7c9b9', 0.91)
material('医疗包 · 红色十字', 'b63d37', 0.67)
material('医疗包 · 白色贴章', 'e0dfd1', 0.88)
material('弹药箱 · 军绿烤漆', '4b5c43', 0.51, 0.32)
material('弹药箱 · 黄色印字', 'd7b856', 0.62, 0.05)
material('弹药 · 黄铜弹壳', 'b58a43', 0.28, 0.78)
material('弹药 · 铜被甲', 'a9683e', 0.30, 0.72)


def reset():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def assign(o, key):
    o.data.materials.append(MATS[key])
    return o


def smooth(o):
    if o.type == 'MESH':
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def bevel(o, width=0.015, segments=3):
    mod = o.modifiers.new('真实边缘倒角', 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod = o.modifiers.new('加权表面法线', 'WEIGHTED_NORMAL')
    return o


def cube(name, loc, dims, mat, edge=0.015, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rot:
        o.rotation_euler = rot
    assign(o, mat)
    if edge:
        bevel(o, edge, 4)
    return o


def cylinder(name, loc, radius, depth, mat, rot=None, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if rot:
        o.rotation_euler = rot
    assign(o, mat)
    bevel(o, min(0.005, radius * 0.15), 3)
    smooth(o)
    return o


def tube(name, points, radius, mat, cyclic=False):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    spline.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    assign(o, mat)
    return o


def text(name, body, loc, size, mat, rot=(math.pi / 2, 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.0007
    o.data.bevel_depth = 0.0003
    assign(o, mat)
    return o


def mesh_object(name, verts, faces, mat, thickness=0.0, subdiv=1):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    assign(o, mat)
    smooth(o)
    if subdiv:
        mod = o.modifiers.new('柔性曲面细分', 'SUBSURF')
        mod.levels = subdiv
        mod.render_levels = subdiv
    if thickness:
        mod = o.modifiers.new('真实材料厚度', 'SOLIDIFY')
        mod.thickness = thickness
        mod.offset = 0
    bevel(o, 0.006, 3)
    return o


def grid_faces(rows, cols):
    faces = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            a = r * cols + c
            faces.append((a, a + 1, a + 1 + cols, a + cols))
    return faces


def armor_panel(name, front=True, inset=False):
    rows = cols = 11
    verts = []
    for r in range(rows):
        v = r / (rows - 1)
        z = 0.99 + v * (0.39 if inset else 0.54)
        half = (0.205 if inset else 0.275) * (0.83 + 0.17 * math.sin(v * math.pi))
        for c in range(cols):
            u = c / (cols - 1)
            x = (u * 2 - 1) * half
            curve = 0.305 + 0.055 * (1 - (x / max(half, 0.001)) ** 2)
            curve += (0.040 if inset else 0.0) + 0.012 * math.sin(v * math.pi)
            y = -curve if front else curve
            verts.append((x, y, z))
    return mesh_object(name, verts, grid_faces(rows, cols), '装备 · 插板涂层' if inset else '装备 · 橄榄绿织物', 0.045 if inset else 0.065, 1)


def cummerbund(side):
    rows, cols = 4, 15
    verts = []
    for r in range(rows):
        z = 1.07 + r / (rows - 1) * 0.29
        for c in range(cols):
            t = math.radians(52 + c / (cols - 1) * 76)
            theta = side * t
            verts.append((0.34 * math.sin(theta), 0.29 * math.cos(theta), z))
    return mesh_object('ArmorCummerbund', verts, grid_faces(rows, cols), '装备 · 深色织带', 0.035, 1)


def shoulder_strap(side):
    rows, cols = 13, 3
    verts = []
    for r in range(rows):
        t = r / (rows - 1)
        y = -0.29 + 0.58 * t
        z = 1.47 + 0.17 * math.sin(t * math.pi)
        for c in range(cols):
            x = side * 0.215 + (c / (cols - 1) - 0.5) * 0.095
            verts.append((x, y, z))
    return mesh_object('ArmorShoulderWebbing', verts, grid_faces(rows, cols), '装备 · 深色织带', 0.025, 1)


def build_armor():
    armor_panel('ArmorFrontCarrier', True, False)
    armor_panel('ArmorBackCarrier', False, False)
    armor_panel('ArmorFrontPlate', True, True)
    armor_panel('ArmorBackPlate', False, True)
    for side in (-1, 1):
        cummerbund(side)
        shoulder_strap(side)
        cube('ArmorShoulderBuckle', (side * 0.215, -0.315, 1.47), (0.105, 0.035, 0.07), '通用 · 磨旧钢件', 0.012)
        cube('ArmorSideRelease', (side * 0.34, -0.06, 1.22), (0.04, 0.10, 0.075), '通用 · 深色金属', 0.010)
    for z in (1.22, 1.30, 1.38):
        cube('ArmorMolleRow', (0, -0.422, z), (0.46, 0.020, 0.022), '装备 · 深色织带', 0.006)
        for x in (-0.18, -0.09, 0.0, 0.09, 0.18):
            tube('ArmorMolleStitch', [(x, -0.435, z - 0.010), (x, -0.435, z + 0.010)], 0.0014, '装备 · 缝线')
    for x in (-0.175, 0.0, 0.175):
        cube('ArmorMagazinePouch', (x, -0.437, 1.095), (0.155, 0.115, 0.19), '装备 · 橄榄绿织物', 0.025)
        cube('ArmorPouchFlap', (x, -0.501, 1.165), (0.157, 0.025, 0.075), '装备 · 软袋滚边', 0.012)
        cube('ArmorPouchPullTab', (x, -0.520, 1.105), (0.032, 0.015, 0.115), '装备 · 深色织带', 0.006)
        for dx in (-0.052, 0.052):
            tube('ArmorPouchStitch', [(x + dx, -0.503, 1.03), (x + dx, -0.508, 1.09), (x + dx, -0.503, 1.15)], 0.0015, '装备 · 缝线')
    text('ArmorIdentifier', '07', (0, -0.437, 1.315), 0.075, '装备 · 识别标记')
    for side in (-1, 1):
        tube('ArmorShoulderSeam', [(side * 0.25, -0.27, 1.49), (side * 0.25, 0, 1.64), (side * 0.25, 0.27, 1.49)], 0.002, '装备 · 缝线')


def build_helmet():
    rows, cols = 19, 65
    verts = []
    rim = []
    for r in range(rows):
        t = r / (rows - 1)
        for c in range(cols):
            a = c / (cols - 1) * math.tau
            phi_max = 1.62 + 0.17 * (math.sin(a) + 1) * 0.5
            phi = 0.006 + t * (phi_max - 0.006)
            x = 0.148 * math.sin(phi) * math.cos(a)
            y = 0.138 * math.sin(phi) * math.sin(a)
            z = 0.055 + 0.19 * math.cos(phi)
            z += 0.005 * math.cos(a * 2) * math.sin(phi)
            verts.append((x, y, z))
            if r == rows - 1:
                rim.append((x, y, z))
    mesh_object('HelmetBallisticShell', verts, grid_faces(rows, cols), '头盔 · 磨砂涂层', 0.009, 1)
    tube('HelmetRubberRim', rim[::3], 0.005, '通用 · 哑黑橡胶', True)
    cube('HelmetNvgMount', (0, -0.139, 0.155), (0.057, 0.018, 0.067), '通用 · 深色金属', 0.009, (math.radians(-8), 0, 0))
    cube('HelmetNvgInset', (0, -0.151, 0.157), (0.029, 0.009, 0.035), '通用 · 磨旧钢件', 0.004)
    for side in (-1, 1):
        cube('HelmetSideRail', (side * 0.143, 0.005, 0.115), (0.018, 0.158, 0.034), '头盔 · 侧导轨', 0.008, (0, 0, side * math.radians(4)))
        for y in (-0.050, 0.0, 0.050):
            cylinder('HelmetRailScrew', (side * 0.154, y, 0.116), 0.006, 0.005, '通用 · 磨旧钢件', (0, math.pi / 2, 0), 24)
        tube('HelmetChinStrap', [(side * 0.13, -0.035, 0.10), (side * 0.09, -0.055, 0.025), (side * 0.025, -0.075, 0.018)], 0.007, '装备 · 深色织带')


def build_medkit():
    cube('MedkitMainBag', (0, 0, 0.135), (0.46, 0.27, 0.23), '医疗包 · 米灰织物', 0.052)
    cube('MedkitFrontPocket', (0, -0.146, 0.12), (0.33, 0.065, 0.145), '医疗包 · 米灰织物', 0.027)
    cube('MedkitCrossPatch', (0, -0.184, 0.145), (0.125, 0.012, 0.108), '医疗包 · 白色贴章', 0.014)
    cube('MedkitCrossVertical', (0, -0.193, 0.145), (0.030, 0.009, 0.080), '医疗包 · 红色十字', 0.004)
    cube('MedkitCrossHorizontal', (0, -0.194, 0.145), (0.080, 0.009, 0.030), '医疗包 · 红色十字', 0.004)
    tube('MedkitHandle', [(-0.105, 0, 0.245), (-0.085, 0, 0.32), (0.085, 0, 0.32), (0.105, 0, 0.245)], 0.013, '装备 · 深色织带')
    tube('MedkitZipper', [(-0.20, -0.116, 0.22), (0, -0.142, 0.235), (0.20, -0.116, 0.22)], 0.005, '通用 · 深色金属')
    for i in range(19):
        x = -0.18 + i * 0.02
        cube('MedkitZipperTooth', (x, -0.144, 0.235), (0.009, 0.009, 0.009), '通用 · 磨旧钢件', 0.002)
    tube('MedkitZipPull', [(0.15, -0.15, 0.235), (0.17, -0.17, 0.20), (0.18, -0.17, 0.17)], 0.004, '通用 · 深色金属')
    for x in (-0.145, 0.145):
        tube('MedkitPocketStitch', [(x, -0.184, 0.07), (x, -0.187, 0.12), (x, -0.184, 0.18)], 0.0018, '装备 · 缝线')
    for side in (-1, 1):
        cube('MedkitSideBand', (side * 0.225, 0, 0.14), (0.018, 0.22, 0.065), '装备 · 深色织带', 0.008)


def cartridge(name, loc, angle):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    parts = []
    parts.append(cylinder(name + 'Case', (0, 0, 0.034), 0.012, 0.056, '弹药 · 黄铜弹壳', vertices=32))
    parts.append(cylinder(name + 'Rim', (0, 0, 0.005), 0.014, 0.006, '弹药 · 黄铜弹壳', vertices=32))
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.0115, radius2=0.002, depth=0.040, location=(0, 0, 0.082))
    tip = bpy.context.object
    tip.name = name + 'Bullet'
    assign(tip, '弹药 · 铜被甲')
    smooth(tip)
    parts.append(tip)
    for o in parts:
        o.parent = root
    root.location = loc
    root.rotation_euler = (0, angle, 0)
    return root


def build_ammo():
    cube('AmmoCanBody', (0, 0, 0.145), (0.44, 0.26, 0.25), '弹药箱 · 军绿烤漆', 0.022)
    cube('AmmoCanLid', (0, 0, 0.288), (0.458, 0.278, 0.052), '弹药箱 · 军绿烤漆', 0.014)
    cube('AmmoCanFrontLatch', (0, -0.142, 0.205), (0.052, 0.022, 0.105), '通用 · 深色金属', 0.008)
    cylinder('AmmoLatchPin', (0, -0.158, 0.235), 0.009, 0.065, '通用 · 磨旧钢件', (0, math.pi / 2, 0), 32)
    tube('AmmoCarryHandle', [(-0.10, 0, 0.315), (-0.075, 0, 0.37), (0.075, 0, 0.37), (0.10, 0, 0.315)], 0.010, '通用 · 深色金属')
    for x in (-0.145, 0.145):
        cylinder('AmmoLidHinge', (x, 0.142, 0.285), 0.013, 0.075, '通用 · 深色金属', (0, math.pi / 2, 0), 32)
    text('AmmoCaliberMark', '5.56', (0, -0.136, 0.135), 0.055, '弹药箱 · 黄色印字')
    for x in (-0.17, 0.17):
        cube('AmmoCornerWear', (x, -0.134, 0.06), (0.045, 0.004, 0.008), '通用 · 磨旧钢件', 0.002, (0, 0, 0.12))
    for i in range(3):
        cartridge('AmmoLooseRound', (0.29 + i * 0.035, -0.07 + i * 0.055, 0.020), math.pi / 2)


def prepare_and_export(asset_name):
    bpy.ops.object.select_all(action='SELECT')
    for o in list(bpy.context.scene.objects):
        if o.type in {'CURVE', 'TEXT'}:
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.convert(target='MESH')
    for o in list(bpy.context.scene.objects):
        if o.type == 'MESH':
            bpy.context.view_layer.objects.active = o
            for mod in list(o.modifiers):
                bpy.ops.object.modifier_apply(modifier=mod.name)
            smooth(o)
    bpy.ops.object.select_all(action='SELECT')
    source_path = SOURCE / (asset_name + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(source_path))
    bpy.ops.export_scene.gltf(filepath=str(MODELS / (asset_name + '.glb')), export_format='GLB', use_selection=True, export_apply=True, export_animations=False)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    print('ASSET_EXPORTED', asset_name, 'meshes', len(meshes), 'vertices', sum(len(o.data.vertices) for o in meshes))


def render_asset(asset_name, target, camera_loc, ortho):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.16, 0.19, 0.20, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.006))
    floor = bpy.context.object
    floor.name = 'PreviewFloor'
    if 'Preview floor' not in bpy.data.materials:
        m = bpy.data.materials.new('Preview floor')
        m.diffuse_color = (0.075, 0.09, 0.085, 1)
        m.use_nodes = True
        p = next(n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = (0.075, 0.09, 0.085, 1)
        p.inputs['Roughness'].default_value = 0.92
    floor.data.materials.append(bpy.data.materials['Preview floor'])
    for name, loc, power, size, color in [
        ('Key', (2.5, -3.5, 4.5), 500, 3.0, (1.0, 0.88, 0.72)),
        ('Fill', (-2.5, -1.0, 2.5), 260, 2.5, (0.72, 0.84, 1.0)),
        ('Rim', (1.0, 2.5, 3.5), 400, 2.0, (0.86, 0.93, 1.0)),
    ]:
        bpy.ops.object.light_add(type='AREA', location=loc)
        o = bpy.context.object
        o.name = name
        o.data.energy = power
        o.data.shape = 'DISK'
        o.data.size = size
        o.data.color = color
        o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.camera_add(location=camera_loc)
    cam = bpy.context.object
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = ortho
    scene.camera = cam
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(RENDERS / (asset_name + '.png'))
    bpy.ops.render.render(write_still=True)


BUILDERS = [
    ('armor', build_armor, (0, 0, 1.25), (2.4, -4.0, 2.45), 1.22),
    ('helmet', build_helmet, (0, 0, 0.12), (0.55, -0.85, 0.52), 0.48),
    ('medkit', build_medkit, (0, 0, 0.15), (0.75, -1.1, 0.72), 0.74),
    ('ammo_pickup', build_ammo, (0.06, 0, 0.16), (0.85, -1.15, 0.72), 0.83),
]

for name, builder, target, camera, ortho in BUILDERS:
    reset()
    builder()
    prepare_and_export(name)
    render_asset(name, target, camera, ortho)

print('SURVIVAL_PROPS_COMPLETE')
