"""Shared geometry, material and texture helpers for the cabin set."""

import bpy
import bmesh
import math
import os
import random
import numpy as np
from math import pi, sin, cos, tau, radians
from mathutils import Vector, Matrix, Euler

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78"
TEX_DIR = os.path.join(ROOT, "assets", "textures", "cabin")
ENV_DIR = os.path.join(ROOT, "assets", "models", "environment")
SRC_DIR = os.path.join(ROOT, "assets", "models", "source")
OUT_GLB = os.path.join(ENV_DIR, "cabin_interior.glb")
OUT_BLEND = os.path.join(SRC_DIR, "cabin_interior.blend")
os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(ENV_DIR, exist_ok=True)
os.makedirs(SRC_DIR, exist_ok=True)

MAT = {}


def rr(a, b):
    return random.uniform(a, b)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------------------------------
# generated textures
# ---------------------------------------------------------------------------------------

def _save_rgba_image(name, path, rgba, width, height):
    img = bpy.data.images.new(name, width=width, height=height, alpha=True)
    img.pixels[:] = rgba.ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def generate_textures():
    """End-grain discs and a night sky, both cheap to generate and impossible to tile."""
    end_path = os.path.join(TEX_DIR, "endgrain.png")
    if not os.path.exists(end_path):
        w = h = 512
        yy, xx = np.mgrid[0:h, 0:w]
        cx = cy = 255.5
        dx = xx - cx
        dy = yy - cy
        r = np.sqrt(dx * dx + dy * dy) / 256.0
        a = np.arctan2(dy, dx)
        rings = 0.5 + 0.5 * np.sin(r * 58.0 + 1.6 * np.sin(a * 3.0 + 0.7) + 0.7 * np.sin(a * 7.0))
        rings = 0.55 + 0.45 * rings
        grain = 0.86 + 0.14 * np.sin(r * 240.0 + 2.0 * np.sin(a * 5.0))
        cracks = np.ones_like(r)
        for ang in (0.4, 2.1, 3.4, 5.3):
            d = np.abs(np.sin((a - ang) * 0.5))
            crack = np.clip((0.012 - d) * 140.0, 0.0, 1.0)
            cracks *= (1.0 - 0.65 * crack * np.clip((r - 0.12) * 2.0, 0.0, 1.0))
        tone = rings * grain * cracks
        base = np.stack([
            0.34 * tone + 0.035,
            0.20 * tone + 0.022,
            0.10 * tone + 0.013,
        ], axis=-1)
        base = np.clip(base, 0.0, 1.0)
        rgba = np.concatenate([base, np.ones((h, w, 1))], axis=-1)
        _save_rgba_image("CabinEndGrain", end_path, rgba, w, h)

    sky_path = os.path.join(TEX_DIR, "night_sky.png")
    if not os.path.exists(sky_path):
        w, h = 1024, 1024
        yy, xx = np.mgrid[0:h, 0:w]
        u = xx / (w - 1)
        v = yy / (h - 1)  # bottom (0) to top (1)
        top = np.array([0.012, 0.022, 0.055])
        horizon = np.array([0.10, 0.15, 0.20])
        t = np.clip(v * 1.15, 0.0, 1.0)[..., None]
        sky = horizon * (1.0 - t) + top * t
        # moon and its glow, upper left of the visible window
        mx, my = 0.30, 0.70
        d = np.sqrt(((u - mx) * 1.0) ** 2 + ((v - my) * 1.0) ** 2)
        glow = np.exp(-(d / 0.16) ** 2) * 0.36
        halo = np.exp(-(d / 0.055) ** 2) * 0.65
        disc = (d < 0.032).astype(np.float32)
        sky += glow[..., None] * np.array([0.35, 0.48, 0.70])
        sky += halo[..., None] * np.array([0.55, 0.66, 0.82])
        sky += disc[..., None] * np.array([0.92, 0.95, 1.0])
        # thin cloud bands
        cloud = 0.5 + 0.5 * np.sin(u * 11.0 + np.sin(v * 7.0) * 0.8 + v * 19.0)
        cloud *= 0.5 + 0.5 * np.sin(u * 23.0 - v * 5.0)
        cloud = np.clip(cloud, 0.0, 1.0) * 0.055 * np.clip((v - 0.2) / 0.8, 0.0, 1.0)
        sky += cloud[..., None] * np.array([0.35, 0.42, 0.52])
        # stars, more in the upper half
        rng = np.random.default_rng(4702)
        stars = rng.random((h, w))
        star_mask = (stars > 0.9985) & (v > 0.25)
        star_val = rng.random((h, w)) * 0.7 + 0.3
        sky += (star_mask[..., None] * star_val[..., None]) * np.array([0.8, 0.86, 1.0])
        rgba = np.concatenate([np.clip(sky, 0.0, 1.0), np.ones((h, w, 1))], axis=-1)
        _save_rgba_image("CabinNightSky", sky_path, rgba, w, h)


# ---------------------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------------------

def _image(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def _blend(mat):
    try:
        mat.surface_render_method = "BLENDED"
    except Exception:
        pass
    try:
        mat.blend_method = "BLEND"
    except Exception:
        pass


def plain(name, color, rough=0.8, metal=0.0, emission=None, emission_strength=0.0,
          alpha=1.0, backface_cull=True):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        _blend(mat)
    mat.diffuse_color = (*color, alpha)
    mat.use_backface_culling = backface_cull
    MAT[name] = mat
    return mat


def pbr(name, diff_file, nor_file=None, rough_file=None, metal=0.0,
        normal_strength=1.0, backface_cull=True):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(os.path.join(TEX_DIR, diff_file))
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if rough_file:
        rt = nt.nodes.new("ShaderNodeTexImage")
        rt.image = _image(os.path.join(TEX_DIR, rough_file), True)
        nt.links.new(rt.outputs["Color"], bsdf.inputs["Roughness"])
    if nor_file:
        nt_ = nt.nodes.new("ShaderNodeTexImage")
        nt_.image = _image(os.path.join(TEX_DIR, nor_file), True)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = normal_strength
        nt.links.new(nt_.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Metallic"].default_value = metal
    mat.use_backface_culling = backface_cull
    MAT[name] = mat
    return mat


def emissive_tex(name, tex_file, strength=1.0, backface_cull=True):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _image(os.path.join(TEX_DIR, tex_file))
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Emission Strength"].default_value = strength
    mat.use_backface_culling = backface_cull
    MAT[name] = mat
    return mat


def build_materials():
    generate_textures()
    M = MAT
    M["floor"] = pbr("FloorOldOak", "floor_diff.jpg", "floor_nor.jpg", "floor_rough.jpg", normal_strength=0.85)
    M["wall"] = pbr("CabinPlanks", "wall_diff.jpg", "wall_nor.jpg", "wall_rough.jpg", normal_strength=0.9)
    M["stone"] = pbr("CabinStone", "stone_diff.jpg", "stone_nor.jpg", "stone_rough.jpg", normal_strength=1.0)
    M["stone_dark"] = pbr("CabinStoneSoot", "stone_diff.jpg", "stone_nor.jpg", "stone_rough.jpg", normal_strength=1.0)
    M["rust"] = pbr("CabinRust", "rust_diff.jpg", "rust_nor.jpg", "rust_rough.jpg", metal=0.55, normal_strength=1.0)
    M["leather"] = pbr("CabinLeather", "leather_diff.jpg", "leather_nor.jpg", "leather_rough.jpg", normal_strength=0.8)
    M["rug"] = pbr("CabinRug", "rug_diff.jpg", "rug_nor.jpg", "rug_rough.jpg", normal_strength=1.0, backface_cull=False)
    M["burlap"] = pbr("CabinBurlap", "burlap_diff.jpg", "burlap_nor.jpg", "burlap_rough.jpg", normal_strength=1.0, backface_cull=False)
    M["bark"] = pbr("CabinBark", "bark_diff.jpg", "bark_nor.jpg", "bark_rough.jpg", normal_strength=1.0)
    M["wool"] = pbr("CabinWool", "wool_diff.jpg", "wool_nor.jpg", "wool_rough.jpg", normal_strength=1.0, backface_cull=False)
    M["endgrain"] = pbr("CabinEndGrain", "endgrain.png")
    M["night"] = emissive_tex("CabinNightSky", "night_sky.png", 1.2, backface_cull=False)
    M["iron"] = plain("CabinIron", (0.035, 0.037, 0.040), rough=0.42, metal=0.95)
    M["iron_dark"] = plain("CabinIronDark", (0.014, 0.015, 0.016), rough=0.68, metal=0.85)
    M["brass"] = plain("CabinBrass", (0.52, 0.34, 0.10), rough=0.30, metal=0.95)
    M["copper"] = plain("CabinCopper", (0.36, 0.18, 0.08), rough=0.38, metal=0.9)
    M["steel"] = plain("CabinSteel", (0.22, 0.23, 0.24), rough=0.28, metal=1.0)
    M["paper"] = plain("CabinPaper", (0.63, 0.58, 0.46), rough=0.92, backface_cull=False)
    M["paper_old"] = plain("CabinPaperOld", (0.46, 0.39, 0.27), rough=0.96, backface_cull=False)
    M["card"] = plain("CabinCard", (0.34, 0.27, 0.18), rough=0.95)
    M["label_red"] = plain("CabinLabelRed", (0.36, 0.045, 0.035), rough=0.62)
    M["label_green"] = plain("CabinLabelGreen", (0.07, 0.16, 0.08), rough=0.64)
    M["label_cream"] = plain("CabinLabelCream", (0.68, 0.59, 0.41), rough=0.72)
    M["label_blue"] = plain("CabinLabelBlue", (0.09, 0.15, 0.23), rough=0.62)
    M["ceramic"] = plain("CabinEnamel", (0.76, 0.76, 0.71), rough=0.24)
    M["ceramic_blue"] = plain("CabinEnamelBlue", (0.12, 0.22, 0.29), rough=0.26)
    M["clay"] = plain("CabinClay", (0.32, 0.16, 0.09), rough=0.78)
    M["bone"] = plain("CabinBone", (0.58, 0.52, 0.39), rough=0.75)
    M["wax"] = plain("CabinWax", (0.82, 0.75, 0.58), rough=0.66)
    M["char"] = plain("CabinChar", (0.020, 0.018, 0.015), rough=0.98)
    M["ash"] = plain("CabinAsh", (0.28, 0.27, 0.25), rough=1.0)
    M["soot"] = plain("CabinSoot", (0.010, 0.009, 0.008), rough=1.0)
    M["rope"] = plain("CabinRope", (0.44, 0.37, 0.24), rough=0.98)
    M["cord"] = plain("CabinCord", (0.05, 0.05, 0.045), rough=0.95)
    M["snow"] = plain("CabinSnow", (0.68, 0.75, 0.82), rough=0.88)
    M["pine"] = plain("CabinPine", (0.020, 0.045, 0.040), rough=1.0)
    M["pine_snow"] = plain("CabinPineSnow", (0.40, 0.48, 0.54), rough=0.9)
    M["glass"] = plain("CabinGlass", (0.62, 0.73, 0.80), rough=0.08, alpha=0.16, backface_cull=False)
    M["glass_green"] = plain("CabinGlassGreen", (0.09, 0.22, 0.11), rough=0.14, alpha=0.62)
    M["glass_amber"] = plain("CabinGlassAmber", (0.30, 0.13, 0.035), rough=0.14, alpha=0.62)
    M["ember"] = plain("CabinEmber", (0.30, 0.055, 0.005), rough=0.9, emission=(1.0, 0.20, 0.025), emission_strength=4.5)
    M["flame"] = plain("CabinFlame", (1.0, 0.35, 0.04), rough=0.9, emission=(1.0, 0.42, 0.06), emission_strength=7.0, alpha=0.72, backface_cull=False)
    M["lamp_glow"] = plain("CabinLampGlow", (1.0, 0.72, 0.36), rough=0.4, emission=(1.0, 0.62, 0.28), emission_strength=4.0)
    M["moon"] = plain("CabinMoon", (0.8, 0.88, 1.0), rough=0.5, emission=(0.8, 0.9, 1.0), emission_strength=8.0)
    M["door_glow"] = plain("CabinDoorGlow", (0.25, 0.38, 0.55), rough=0.6, emission=(0.25, 0.38, 0.55), emission_strength=2.0)
    M["ink"] = plain("CabinInk", (0.025, 0.025, 0.02), rough=1.0)
    return M


# ---------------------------------------------------------------------------------------
# one mesh per material
# ---------------------------------------------------------------------------------------

class Group:
    def __init__(self, name, material):
        self.name = name
        self.mat = material
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def finish(self):
        bm = self.bm
        bm.normal_update()
        smooth = [f.smooth for f in bm.faces]
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(self.mat)
        if smooth:
            me.polygons.foreach_set("use_smooth", smooth)
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.collection.objects.link(ob)
        return ob


def _uv_for_face(loop, layer, co, n, tile, grain, off):
    ax = max(range(3), key=lambda i: abs(n[i]))
    rem = [i for i in range(3) if i != ax]
    gi = {"X": 0, "Y": 1, "Z": 2}[grain]
    if gi in rem:
        rem.remove(gi)
        order = [rem[0], gi]
    else:
        order = rem
    loop[layer].uv = (co[order[0]] / tile + off[0], co[order[1]] / tile + off[1])


def _rand_off():
    return (rr(0.0, 20.0), rr(0.0, 20.0))


def _rrot(amount=0.0):
    return (rr(-amount, amount), rr(-amount, amount), rr(-amount, amount))


# ---------------------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------------------

def box(g, center, size, rot=(0, 0, 0), bevel=0.0, seg=2, tile=1.0, grain="X",
        off=None, smooth=False, jitter=0.0):
    """A bevelled box. Grain runs along `grain` in the UV layout."""
    if off is None:
        off = _rand_off()
    bm = g.bm
    R = Euler(rot, "XYZ").to_matrix()
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    local = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
             (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    vs = [bm.verts.new(Vector(center) + R @ Vector(p)) for p in local]
    idx = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
           (2, 3, 7, 6), (3, 0, 4, 7), (1, 2, 6, 5)]
    faces = []
    for ids in idx:
        f = bm.faces.new([vs[i] for i in ids])
        faces.append(f)
        f.normal_update()
        for loop in f.loops:
            _uv_for_face(loop, g.uv, loop.vert.co, f.normal, tile, grain, off)
    if bevel > 0.0:
        edges = list({e for v in vs for e in v.link_edges})
        ret = bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=seg,
                              affect="EDGES", profile=0.5, clamp_overlap=True)
        new_faces = list(ret.get("faces", []))
        new_faces += [f for f in faces if f.is_valid]
        for f in new_faces:
            f.normal_update()
            for loop in f.loops:
                _uv_for_face(loop, g.uv, loop.vert.co, f.normal, tile, grain, off)
            f.smooth = smooth
        if jitter > 0.0:
            seen = set()
            for f in new_faces:
                for v in f.verts:
                    if v.index not in seen:
                        seen.add(v.index)
                        n = (v.co - Vector(center))
                        if n.length > 1e-6:
                            v.co += n.normalized() * rr(-jitter, jitter)
    else:
        for f in faces:
            f.smooth = smooth
    return vs


def cylinder(g, center, radius, depth, rot=(0, 0, 0), segments=24, tile=1.0,
             cap=True, smooth=True, taper=1.0, off=None, radius2=None):
    if off is None:
        off = _rand_off()
    bm = g.bm
    R = Euler(rot, "XYZ").to_matrix()
    r0 = radius
    r1 = radius * taper if radius2 is None else radius2
    ring0 = []
    ring1 = []
    for i in range(segments):
        a = tau * i / segments
        z0 = -depth * 0.5
        z1 = depth * 0.5
        ring0.append(bm.verts.new(Vector(center) + R @ Vector((r0 * cos(a), r0 * sin(a), z0))))
        ring1.append(bm.verts.new(Vector(center) + R @ Vector((r1 * cos(a), r1 * sin(a), z1))))
    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new([ring0[i], ring0[j], ring1[j], ring1[i]])
        f.normal_update()
        for loop in f.loops:
            v = loop.vert.co
            a = math.atan2((R.inverted() @ (v - Vector(center))).y,
                           (R.inverted() @ (v - Vector(center))).x)
            local = R.inverted() @ (v - Vector(center))
            loop[g.uv].uv = ((a % tau) * max(r0, 0.001) / tile + off[0],
                             (local.z + depth * 0.5) / tile + off[1])
        f.smooth = smooth
    if cap:
        for rr_, zz, flip in ((r0, -depth * 0.5, True), (r1, depth * 0.5, False)):
            if rr_ <= 0.0:
                continue
            cv = bm.verts.new(Vector(center) + R @ Vector((0, 0, zz)))
            ring = []
            for i in range(segments):
                a = tau * i / segments
                ring.append(bm.verts.new(Vector(center) + R @ Vector((rr_ * cos(a), rr_ * sin(a), zz))))
            for i in range(segments):
                j = (i + 1) % segments
                f = bm.faces.new([cv, ring[j], ring[i]] if flip else [cv, ring[i], ring[j]])
                f.normal_update()
                for loop in f.loops:
                    v = R.inverted() @ (loop.vert.co - Vector(center))
                    u = 0.5 + 0.5 * v.x / max(rr_, 1e-5)
                    w = 0.5 + 0.5 * v.y / max(rr_, 1e-5)
                    loop[g.uv].uv = (u + off[0], w + off[1])
                f.smooth = False
    return ring0


def disk(g, center, radius, rot=(0, 0, 0), segments=24, tile=1.0, off=None, smooth=False):
    if off is None:
        off = (0.5, 0.5)
    bm = g.bm
    R = Euler(rot, "XYZ").to_matrix()
    cv = bm.verts.new(Vector(center))
    ring = []
    for i in range(segments):
        a = tau * i / segments
        ring.append(bm.verts.new(Vector(center) + R @ Vector((radius * cos(a), radius * sin(a), 0))))
    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new([cv, ring[i], ring[j]])
        f.normal_update()
        for loop in f.loops:
            v = loop.vert.co - Vector(center)
            loop[g.uv].uv = (0.5 + v.x / (2 * radius) + off[0],
                             0.5 + v.y / (2 * radius) + off[1])
        f.smooth = smooth


def torus(g, center, major, minor, rot=(0, 0, 0), major_seg=24, minor_seg=10,
          tile=1.0, off=None, smooth=True):
    if off is None:
        off = _rand_off()
    bm = g.bm
    R = Euler(rot, "XYZ").to_matrix()
    rings = []
    for i in range(major_seg):
        a = tau * i / major_seg
        ring = []
        for j in range(minor_seg):
            b = tau * j / minor_seg
            p = Vector(((major + minor * cos(b)) * cos(a),
                        (major + minor * cos(b)) * sin(a),
                        minor * sin(b)))
            ring.append(bm.verts.new(Vector(center) + R @ p))
        rings.append(ring)
    for i in range(major_seg):
        i2 = (i + 1) % major_seg
        for j in range(minor_seg):
            j2 = (j + 1) % minor_seg
            f = bm.faces.new([rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]])
            f.normal_update()
            for loop in f.loops:
                v = R.inverted() @ (loop.vert.co - Vector(center))
                a = math.atan2(v.y, v.x)
                b = math.atan2(v.z, math.sqrt(v.x * v.x + v.y * v.y) - major)
                loop[g.uv].uv = (a / tau * (tau * major / tile) + off[0],
                                 b / tau * (tau * minor / tile) + off[1])
            f.smooth = smooth


def tube(g, points, radius, sides=6, tile=1.0, caps=True, smooth=True, off=None):
    if off is None:
        off = _rand_off()
    pts = [Vector(p) for p in points]
    if len(pts) < 2:
        return
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    tangents = []
    for i in range(len(pts)):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == len(pts) - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        tangents.append(t.normalized())
    # parallel transport a normal along the path
    up = Vector((0, 0, 1)) if abs(tangents[0].z) < 0.9 else Vector((0, 1, 0))
    n = tangents[0].cross(up).normalized()
    normals = []
    for i, t in enumerate(tangents):
        if i > 0:
            q = tangents[i - 1].rotation_difference(t)
            n = (q @ n)
            n = (n - t * n.dot(t)).normalized()
        normals.append(n.copy())
    bm = g.bm
    rings = []
    for i, p in enumerate(pts):
        t = tangents[i]
        n = normals[i]
        b = t.cross(n).normalized()
        ring = []
        for j in range(sides):
            a = tau * j / sides
            ring.append(bm.verts.new(p + n * (radii[i] * cos(a)) + b * (radii[i] * sin(a))))
        rings.append(ring)
    for i in range(len(pts) - 1):
        for j in range(sides):
            j2 = (j + 1) % sides
            f = bm.faces.new([rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]])
            f.normal_update()
            for loop in f.loops:
                v = loop.vert.co - pts[i]
                t = tangents[i]
                b = t.cross(normals[i]).normalized()
                a = math.atan2(v.dot(b), v.dot(normals[i]))
                loop[g.uv].uv = (a / tau * (tau * max(radii[i], 0.001) / tile) + off[0],
                                 (i / max(1, len(pts) - 1)) * 2.0 + off[1])
            f.smooth = smooth
    if caps:
        for ring, p, t in ((rings[0], pts[0], tangents[0]), (rings[-1], pts[-1], tangents[-1])):
            f = bm.faces.new(list(reversed(ring)) if t.z > 0 else ring)
            f.normal_update()
            f.smooth = False


def lathe(g, profile, center=(0, 0, 0), segments=24, rot=(0, 0, 0), tile=1.0,
          smooth=True, off=None):
    """Revolve a list of (radius, z) profile points around local Z."""
    if off is None:
        off = _rand_off()
    bm = g.bm
    R = Euler(rot, "XYZ").to_matrix()
    C = Vector(center)
    rings = []
    for (r, z) in profile:
        ring = []
        for i in range(segments):
            a = tau * i / segments
            ring.append(bm.verts.new(C + R @ Vector((r * cos(a), r * sin(a), z))))
        rings.append(ring)
    for k in range(len(rings) - 1):
        ravg = max(0.0005, 0.5 * (profile[k][0] + profile[k + 1][0]))
        for i in range(segments):
            j = (i + 1) % segments
            f = bm.faces.new([rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]])
            f.normal_update()
            for loop in f.loops:
                v = R.inverted() @ (loop.vert.co - C)
                a = math.atan2(v.y, v.x) % tau
                z = (v.z - profile[0][1]) / tile
                loop[g.uv].uv = (a * ravg / tile + off[0], z + off[1])
            f.smooth = smooth
    # caps
    for k, flip in ((0, True), (len(rings) - 1, False)):
        if profile[k][0] > 1e-4:
            f = bm.faces.new(list(reversed(rings[k])) if flip else rings[k])
            f.normal_update()
            f.smooth = False
    return rings


def sphere(g, center, radii, rot=(0, 0, 0), subdiv=2, tile=1.0, smooth=True,
           off=None, jitter=0.0):
    if off is None:
        off = _rand_off()
    bm = g.bm
    ret = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    vs = ret["verts"]
    R = Euler(rot, "XYZ").to_matrix()
    C = Vector(center)
    for v in vs:
        d = v.co.copy()
        if jitter > 0.0:
            d += d.normalized() * rr(-jitter, jitter)
        v.co = C + R @ Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2]))
    faces = set()
    for v in vs:
        faces.update(v.link_faces)
    for f in faces:
        f.normal_update()
        for loop in f.loops:
            v = loop.vert.co - C
            vr = R.inverted() @ v
            u = math.atan2(vr.y, vr.x) / tau + 0.5
            w = 0.5 + math.asin(max(-1.0, min(1.0, vr.z / max(radii[2], 1e-5)))) / pi
            loop[g.uv].uv = (u * (tau * max(radii[0], 0.001) / tile) + off[0],
                             w * (pi * max(radii[2], 0.001) / tile) + off[1])
        f.smooth = smooth
    return vs


def extrude_xz(g, points, y, depth, bevel=0.0, seg=2, tile=1.0, grain="X",
               off=None, smooth=False):
    """Extrude a 2D polygon in the XZ plane along Y."""
    if off is None:
        off = _rand_off()
    bm = g.bm
    front = [bm.verts.new((x, y + depth * 0.5, z)) for (x, z) in points]
    back = [bm.verts.new((x, y - depth * 0.5, z)) for (x, z) in points]
    faces = []
    faces.append(bm.faces.new(front))
    faces.append(bm.faces.new(list(reversed(back))))
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new([front[i], front[j], back[j], back[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    for f in faces:
        f.normal_update()
        for loop in f.loops:
            _uv_for_face(loop, g.uv, loop.vert.co, f.normal, tile, grain, off)
    if bevel > 0.0:
        edges = list({e for f in faces if f.is_valid for e in f.edges})
        ret = bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=seg,
                              affect="EDGES", profile=0.5, clamp_overlap=True)
        new_faces = list(ret.get("faces", [])) + [f for f in faces if f.is_valid]
        for f in new_faces:
            f.normal_update()
            for loop in f.loops:
                _uv_for_face(loop, g.uv, loop.vert.co, f.normal, tile, grain, off)
            f.smooth = smooth
    else:
        for f in faces:
            f.smooth = smooth


def quad(g, corners, uv_rect=(0, 0, 1, 1), smooth=False):
    bm = g.bm
    vs = [bm.verts.new(c) for c in corners]
    f = bm.faces.new(vs)
    f.normal_update()
    u0, v0, u1, v1 = uv_rect
    uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    for loop, uv in zip(f.loops, uvs):
        loop[g.uv].uv = uv
    f.smooth = smooth


def cloth(g, origin, u_vec, v_vec, normal, nu, nv, thick, height_fn,
          uv_rect=(0, 0, 1, 1), smooth=True):
    """Two-sided sheet with folds. height_fn(u,v) returns displacement along normal."""
    bm = g.bm
    O = Vector(origin)
    U = Vector(u_vec)
    V = Vector(v_vec)
    N = Vector(normal)
    u0, v0, u1, v1 = uv_rect
    top = []
    bot = []
    for j in range(nv + 1):
        vt = j / nv
        rt = []
        rb = []
        for i in range(nu + 1):
            ut = i / nu
            h = height_fn(ut, vt)
            p = O + U * ut + V * vt + N * h
            rt.append(bm.verts.new(p))
            rb.append(bm.verts.new(p - N * thick))
        top.append(rt)
        bot.append(rb)

    def uv(ut, vt):
        return (u0 + (u1 - u0) * ut, v0 + (v1 - v0) * vt)

    for j in range(nv):
        for i in range(nu):
            ut0, ut1 = i / nu, (i + 1) / nu
            vt0, vt1 = j / nv, (j + 1) / nv
            f = bm.faces.new([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
            f.normal_update()
            f.smooth = smooth
            for loop, (uu, vv) in zip(f.loops, [uv(ut0, vt0), uv(ut1, vt0), uv(ut1, vt1), uv(ut0, vt1)]):
                loop[g.uv].uv = (uu, vv)
            f2 = bm.faces.new([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
            f2.normal_update()
            f2.smooth = smooth
            for loop, (uu, vv) in zip(f2.loops, [uv(ut0, vt0), uv(ut0, vt1), uv(ut1, vt1), uv(ut1, vt0)]):
                loop[g.uv].uv = (uu, vv)
    # thin rims around the four edges
    for i in range(nu):
        ua, ub = i / nu, (i + 1) / nu
        for j in (0, nv):
            f = bm.faces.new([top[j][i], bot[j][i], bot[j][i + 1], top[j][i + 1]])
            f.normal_update()
            f.smooth = False
            for loop, (uu, vv) in zip(f.loops, [uv(ua, j / nv), uv(ua, j / nv), uv(ub, j / nv), uv(ub, j / nv)]):
                loop[g.uv].uv = (uu, vv)
    for j in range(nv):
        va, vb = j / nv, (j + 1) / nv
        for i in (0, nu):
            f = bm.faces.new([top[j][i], bot[j][i], bot[j + 1][i], top[j + 1][i]])
            f.normal_update()
            f.smooth = False
            for loop, (uu, vv) in zip(f.loops, [uv(i / nu, va), uv(i / nu, va), uv(i / nu, vb), uv(i / nu, vb)]):
                loop[g.uv].uv = (uu, vv)


# === END PRIMITIVES ===
