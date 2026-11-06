import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'models' / 'motorcycle.glb'

# Apocalypse scrambler: army-green tank, dark frame, rusty exhaust, cargo box on the rear rack.
# Forward is -Z (the way the survivor runs). Ground plane is y=0, wheel radius 0.34 m.

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)

def mat(name, color, rough=0.75, metal=0.0, emit=None, energy=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if emit:
        bsdf.inputs['Emission Color'].default_value = (*emit, 1.0)
        bsdf.inputs['Emission Strength'].default_value = energy
    return m

TIRE = mat('tire', (0.055, 0.055, 0.06), 0.95)
STEEL = mat('frame steel', (0.16, 0.17, 0.18), 0.55, 0.65)
CHROME = mat('fork chrome', (0.42, 0.44, 0.46), 0.3, 0.85)
TANK = mat('tank olive', (0.23, 0.26, 0.16), 0.6, 0.25)
SEAT = mat('seat leather', (0.09, 0.07, 0.055), 0.9)
RUST = mat('exhaust rust', (0.35, 0.19, 0.11), 0.8, 0.3)
LENS = mat('headlight lens', (0.85, 0.9, 0.92), 0.25, 0.1, emit=(1.0, 0.94, 0.78), energy=2.5)
CARGO = mat('cargo green', (0.20, 0.24, 0.17), 0.8, 0.15)
RIM = mat('rim', (0.24, 0.25, 0.26), 0.5, 0.7)

def finish(obj, material):
    if material:
        obj.data.materials.append(material)
    return obj

def box(name, loc, scale, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = o.modifiers.new('soft edges', 'BEVEL')
    bevel.width = min(scale) * 0.18
    bevel.segments = 2
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return finish(o, material)

def cyl(name, loc, radius, depth, material, rot=(0, 0, 0), vertices=14):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot, vertices=vertices)
    o = bpy.context.object
    o.name = name
    return finish(o, material)

def torus(name, loc, major, minor, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=20, minor_segments=8, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    return finish(o, material)

def ball(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=16, ring_count=8, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in o.data.polygons:
        p.use_smooth = True
    return finish(o, material)

WHEEL_R = 0.34
FRONT_Z = -0.60
REAR_Z = 0.58

def build_wheel(label, z):
    pivot = bpy.data.objects.new(label, None)
    bpy.context.scene.collection.objects.link(pivot)
    pivot.location = (0, WHEEL_R, z)
    parts = []
    parts.append(torus(label + '_tire', (0, WHEEL_R, z), WHEEL_R - 0.085, 0.085, TIRE, rot=(0, math.pi / 2, 0)))
    parts.append(cyl(label + '_hub', (0, WHEEL_R, z), 0.045, 0.14, RIM, rot=(0, math.pi / 2, 0)))
    parts.append(torus(label + '_rim', (0, WHEEL_R, z), 0.15, 0.028, RIM, rot=(0, math.pi / 2, 0)))
    for i in range(5):
        a = i * math.tau / 5
        spoke = box(label + '_spoke', (0, WHEEL_R + math.sin(a) * 0.13, z + math.cos(a) * 0.13), (0.03, 0.28, 0.028), RIM, rot=(a, 0, 0))
        parts.append(spoke)
    for p in parts:
        p.parent = pivot
    return pivot

build_wheel('WheelFrontPivot', FRONT_Z)
build_wheel('WheelRearPivot', REAR_Z)

# Frame: down tube, top tube and the rear swingarm.
cyl('frame_top', (0, 0.60, 0.02), 0.035, 0.78, STEEL, rot=(math.pi / 2 - 0.42, 0, 0))
cyl('frame_down', (0, 0.48, -0.28), 0.032, 0.62, STEEL, rot=(math.pi / 2 - 0.95, 0, 0))
for sx in (-0.055, 0.055):
    cyl('swingarm', (sx, 0.42, 0.36), 0.026, 0.62, STEEL, rot=(math.pi / 2 - 0.28, 0, 0))
    cyl('fork', (sx, 0.60, -0.50), 0.026, 0.62, CHROME, rot=(math.pi / 2 - 0.62, 0, 0))

# Engine block, tank, seat.
box('engine', (0, 0.38, 0.02), (0.30, 0.30, 0.42), STEEL)
cyl('engine_fin', (0, 0.30, 0.02), 0.16, 0.26, RIM, vertices=12)
ball('fuel_tank', (0, 0.72, -0.12), (0.30, 0.24, 0.52), TANK)
box('seat', (0, 0.72, 0.26), (0.24, 0.09, 0.52), SEAT)

# Handlebar with grips and a small windshield-less headlight.
cyl('handlebar', (0, 0.95, -0.44), 0.022, 0.56, STEEL, rot=(0, math.pi / 2, 0))
for sx in (-0.28, 0.28):
    cyl('grip', (sx, 0.95, -0.44), 0.032, 0.12, SEAT, rot=(0, math.pi / 2, 0))
cyl('headlight_can', (0, 0.82, -0.56), 0.075, 0.10, STEEL, rot=(math.pi / 2, 0, 0))
cyl('headlight_lens', (0, 0.82, -0.615), 0.062, 0.02, LENS, rot=(math.pi / 2, 0, 0), vertices=16)

# Exhaust running low on the right, rusty with a scorched tip.
cyl('exhaust', (0.13, 0.30, 0.28), 0.045, 0.72, RUST, rot=(math.pi / 2, 0, 0))
cyl('exhaust_tip', (0.13, 0.30, 0.62), 0.055, 0.12, STEEL, rot=(math.pi / 2, 0, 0))

# Fenders: flattened arcs above the wheels.
ball('front_fender', (0, WHEEL_R + 0.24, FRONT_Z - 0.02), (0.16, 0.07, 0.5), TANK)
ball('rear_fender', (0, WHEEL_R + 0.26, REAR_Z + 0.04), (0.17, 0.07, 0.46), TANK)

# Rear rack with a lashed-down ammo crate: this bike is for runs through the dead city.
box('rack', (0, 0.74, 0.62), (0.3, 0.03, 0.34), STEEL)
box('cargo_box', (0, 0.86, 0.62), (0.26, 0.22, 0.3), CARGO)
cyl('cargo_strap', (0, 0.86, 0.62), 0.155, 0.27, SEAT, rot=(0, 0, 0), vertices=12).scale = (1.0, 1.0, 1.0)

# Foot pegs where the rider's boots rest.
for sx in (-0.17, 0.17):
    cyl('peg', (sx, 0.42, 0.12), 0.02, 0.1, STEEL, rot=(0, math.pi / 2, 0))

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT), export_format='GLB', export_apply=True, export_yup=True)
print('MOTORCYCLE_EXPORTED', OUT)
