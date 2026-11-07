"""Material palette for the post-apocalyptic safehouse.

Deliberately NOT another warm wood cabin: cool concrete and galvanised steel carry the
room, with rust, olive drab, hazard yellow, faded red, white paper and cyan light as
separate accents so the frame never collapses into one brown note.
"""

import os

import bpy

import cabin_prims as P

PH = os.path.join(P.ROOT, "assets", "textures", "polyhaven")


def _img(path, non_color=False, max_size=None):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    if max_size and max(img.size) > max_size:
        img.scale(max_size, max_size)
    return img


def _ph(asset, mapname):
    return os.path.join(PH, asset, "%s_%s_2k.jpg" % (asset, mapname))


def pbr(name, diff_path, nor_path=None, rough_path=None, metal=0.0,
        normal_strength=1.0, tint=None, roughness=None, backface_cull=True,
        max_size=1024):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _img(diff_path, max_size=max_size)
    if tint is not None:
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs["Fac"].default_value = 1.0
        mix.inputs["Color2"].default_value = (*tint, 1.0)
        nt.links.new(tex.outputs["Color"], mix.inputs["Color1"])
        nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if rough_path:
        rt = nt.nodes.new("ShaderNodeTexImage")
        rt.image = _img(rough_path, True, max_size)
        nt.links.new(rt.outputs["Color"], bsdf.inputs["Roughness"])
    elif roughness is not None:
        bsdf.inputs["Roughness"].default_value = roughness
    if nor_path:
        nt_ = nt.nodes.new("ShaderNodeTexImage")
        nt_.image = _img(nor_path, True, max_size)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = normal_strength
        nt.links.new(nt_.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Metallic"].default_value = metal
    mat.use_backface_culling = backface_cull
    P.MAT[name] = mat
    return mat


def emis(name, color, strength, alpha=1.0, backface_cull=True):
    return P.plain(name, color, rough=0.6, emission=color,
                   emission_strength=strength, alpha=alpha,
                   backface_cull=backface_cull)


def build_materials():
    P.generate_textures()
    M = P.MAT
    M.clear()

    # ---- concrete shell: flat grey, no PolyHaven texture (user rejected it) --------
    # Cool grey so the olive-jacketed survivor pops off the back wall.
    M["concrete"] = P.plain("SafeConcrete", (0.42, 0.42, 0.42), rough=0.92)
    M["concrete_dark"] = P.plain("SafeConcreteDamp", (0.30, 0.30, 0.30), rough=0.95)
    M["concrete_pale"] = P.plain("SafeConcretePale", (0.68, 0.68, 0.68), rough=0.90)
    M["floor"] = P.plain("SafeFloor", (0.48, 0.48, 0.48), rough=0.90)
    M["floor_dark"] = P.plain("SafeFloorDark", (0.32, 0.32, 0.32), rough=0.92)
    M["plaster"] = P.plain("SafePlaster", (0.55, 0.55, 0.53), rough=0.95)
    M["plaster_grey"] = P.plain("SafePlasterGrey", (0.48, 0.48, 0.47), rough=0.95)
    M["brick"] = P.plain("SafeBrick", (0.38, 0.20, 0.15), rough=0.92)

    # ---- weathered wood (only for boards, crates and bench tops) --------------------
    M["wood"] = pbr("SafeWoodGrey", os.path.join(P.TEX_DIR, "wall_diff.jpg"),
                    os.path.join(P.TEX_DIR, "wall_nor.jpg"),
                    os.path.join(P.TEX_DIR, "wall_rough.jpg"),
                    tint=(0.52, 0.52, 0.49), normal_strength=0.9)
    M["wood_dark"] = pbr("SafeWoodDark", os.path.join(P.TEX_DIR, "wall_diff.jpg"),
                         os.path.join(P.TEX_DIR, "wall_nor.jpg"),
                         os.path.join(P.TEX_DIR, "wall_rough.jpg"),
                         tint=(0.26, 0.25, 0.23), normal_strength=0.9)
    M["bench_wood"] = pbr("SafeBenchWood", os.path.join(P.TEX_DIR, "floor_diff.jpg"),
                          os.path.join(P.TEX_DIR, "floor_nor.jpg"),
                          os.path.join(P.TEX_DIR, "floor_rough.jpg"),
                          tint=(0.42, 0.40, 0.36), normal_strength=1.0)
    M["wall"] = M["wood"]          # legacy prop helpers ask for "wall"
    M["bark"] = P.plain("SafeBark", (0.115, 0.088, 0.060), rough=0.95)
    M["endgrain"] = pbr("SafeEndGrain", os.path.join(P.TEX_DIR, "endgrain.png"))

    # ---- metals --------------------------------------------------------------------
    M["rust"] = pbr("SafeRust", os.path.join(P.TEX_DIR, "rust_diff.jpg"),
                    os.path.join(P.TEX_DIR, "rust_nor.jpg"),
                    os.path.join(P.TEX_DIR, "rust_rough.jpg"),
                    metal=0.30, normal_strength=1.0)
    M["rust_dark"] = pbr("SafeRustDark", os.path.join(P.TEX_DIR, "rust_diff.jpg"),
                         os.path.join(P.TEX_DIR, "rust_nor.jpg"),
                         os.path.join(P.TEX_DIR, "rust_rough.jpg"),
                         metal=0.35, tint=(0.55, 0.50, 0.46), normal_strength=1.0)
    M["steel"] = P.plain("SafeSteel", (0.30, 0.32, 0.335), rough=0.36, metal=1.0)
    M["steel_dark"] = P.plain("SafeSteelDark", (0.135, 0.145, 0.155), rough=0.48, metal=1.0)
    M["galv"] = P.plain("SafeGalvanised", (0.46, 0.48, 0.49), rough=0.44, metal=1.0)
    M["iron"] = P.plain("SafeIron", (0.055, 0.058, 0.062), rough=0.44, metal=0.92)
    M["iron_dark"] = P.plain("SafeIronDark", (0.016, 0.017, 0.018), rough=0.72, metal=0.85)
    M["copper"] = P.plain("SafeCopper", (0.34, 0.16, 0.065), rough=0.34, metal=0.95)
    M["brass"] = P.plain("SafeBrass", (0.48, 0.33, 0.11), rough=0.32, metal=0.95)
    M["chrome"] = P.plain("SafeChrome", (0.63, 0.65, 0.67), rough=0.16, metal=1.0)

    # ---- paint ---------------------------------------------------------------------
    M["olive"] = P.plain("SafeOlive", (0.052, 0.068, 0.036), rough=0.58, metal=0.32)
    M["olive_light"] = P.plain("SafeOliveLight", (0.098, 0.118, 0.066), rough=0.62, metal=0.25)
    M["olive_dark"] = P.plain("SafeOliveDark", (0.026, 0.036, 0.020), rough=0.66, metal=0.30)
    M["yellow"] = P.plain("SafeHazardYellow", (0.55, 0.375, 0.016), rough=0.60, metal=0.15)
    M["yellow_dark"] = P.plain("SafeHazardYellowDark", (0.28, 0.185, 0.008), rough=0.66)
    M["red"] = P.plain("SafeRed", (0.30, 0.019, 0.013), rough=0.54, metal=0.20)
    M["red_dark"] = P.plain("SafeRedDark", (0.115, 0.008, 0.006), rough=0.60)
    M["orange"] = P.plain("SafeOrange", (0.56, 0.16, 0.014), rough=0.52, metal=0.20)
    M["white_paint"] = P.plain("SafeWhitePaint", (0.68, 0.685, 0.655), rough=0.62)
    M["white"] = P.plain("SafeWhite", (0.58, 0.585, 0.565), rough=0.78)
    M["black"] = P.plain("SafeBlack", (0.0095, 0.0100, 0.0105), rough=0.86)
    M["rubber"] = P.plain("SafeRubber", (0.019, 0.020, 0.021), rough=0.96)
    M["grease"] = P.plain("SafeGrease", (0.014, 0.012, 0.009), rough=0.28)

    # ---- fabrics, cardboard, paper --------------------------------------------------
    M["burlap"] = pbr("SafeBurlap", os.path.join(P.TEX_DIR, "burlap_diff.jpg"),
                      os.path.join(P.TEX_DIR, "burlap_nor.jpg"),
                      os.path.join(P.TEX_DIR, "burlap_rough.jpg"),
                      normal_strength=1.0, backface_cull=False)
    M["canvas"] = P.plain("SafeCanvasOlive", (0.098, 0.108, 0.075), rough=0.96, backface_cull=False)
    M["canvas_blue"] = P.plain("SafeCanvasBlue", (0.038, 0.058, 0.088), rough=0.96, backface_cull=False)
    M["canvas_grey"] = P.plain("SafeCanvasGrey", (0.145, 0.150, 0.148), rough=0.96, backface_cull=False)
    M["wool"] = pbr("SafeWool", os.path.join(P.TEX_DIR, "wool_diff.jpg"),
                    os.path.join(P.TEX_DIR, "wool_nor.jpg"),
                    os.path.join(P.TEX_DIR, "wool_rough.jpg"),
                    tint=(0.55, 0.62, 0.50), normal_strength=1.0, backface_cull=False)
    M["leather"] = pbr("SafeLeather", os.path.join(P.TEX_DIR, "leather_diff.jpg"),
                       os.path.join(P.TEX_DIR, "leather_nor.jpg"),
                       os.path.join(P.TEX_DIR, "leather_rough.jpg"),
                       normal_strength=0.8)
    M["cardboard"] = P.plain("SafeCardboard", (0.255, 0.185, 0.108), rough=0.95)
    M["rug"] = P.plain("SafeRug", (0.22, 0.10, 0.08), rough=1.0)
    M["cardboard_dark"] = P.plain("SafeCardboardDark", (0.145, 0.104, 0.062), rough=0.96)
    M["paper"] = P.plain("SafePaper", (0.63, 0.625, 0.575), rough=0.94, backface_cull=False)
    M["paper_old"] = P.plain("SafePaperOld", (0.40, 0.36, 0.275), rough=0.96, backface_cull=False)
    M["map"] = P.plain("SafeMap", (0.54, 0.52, 0.42), rough=0.95, backface_cull=False)
    M["ink"] = P.plain("SafeInk", (0.018, 0.018, 0.017), rough=1.0)
    M["chalk"] = P.plain("SafeChalk", (0.72, 0.73, 0.70), rough=0.98)
    M["cord"] = P.plain("SafeCord", (0.028, 0.029, 0.028), rough=0.95)
    M["rope"] = P.plain("SafeRope", (0.33, 0.29, 0.195), rough=0.98)

    # ---- glass, liquid, grime -------------------------------------------------------
    M["glass"] = P.plain("SafeGlass", (0.40, 0.50, 0.56), rough=0.06, alpha=0.18, backface_cull=False)
    M["glass_green"] = P.plain("SafeGlassGreen", (0.075, 0.185, 0.095), rough=0.10, alpha=0.62)
    M["glass_amber"] = P.plain("SafeGlassAmber", (0.29, 0.125, 0.032), rough=0.10, alpha=0.62)
    M["water"] = P.plain("SafeWater", (0.030, 0.055, 0.050), rough=0.08, alpha=0.52)
    M["blood"] = P.plain("SafeBlood", (0.085, 0.006, 0.004), rough=0.42)
    M["blood_dry"] = P.plain("SafeBloodDry", (0.055, 0.012, 0.008), rough=0.70)
    M["stain"] = P.plain("SafeDampStain", (0.072, 0.070, 0.064), rough=0.94)
    M["soot"] = P.plain("SafeSoot", (0.010, 0.010, 0.009), rough=1.0)
    M["ash"] = P.plain("SafeAsh", (0.155, 0.152, 0.144), rough=1.0)
    M["sand"] = P.plain("SafeSand", (0.30, 0.27, 0.20), rough=1.0)
    M["gravel"] = P.plain("SafeGravel", (0.125, 0.125, 0.118), rough=1.0)

    # ---- labels / small colour accents ---------------------------------------------
    M["label_red"] = P.plain("SafeLabelRed", (0.34, 0.030, 0.022), rough=0.62)
    M["label_green"] = P.plain("SafeLabelGreen", (0.055, 0.145, 0.062), rough=0.64)
    M["label_cream"] = P.plain("SafeLabelCream", (0.62, 0.55, 0.38), rough=0.72)
    M["label_blue"] = P.plain("SafeLabelBlue", (0.055, 0.115, 0.205), rough=0.62)
    M["ceramic"] = P.plain("SafeEnamel", (0.71, 0.715, 0.685), rough=0.30)
    M["ceramic_blue"] = P.plain("SafeEnamelBlue", (0.085, 0.165, 0.235), rough=0.32)
    M["bone"] = P.plain("SafeBone", (0.52, 0.50, 0.42), rough=0.78)
    M["bark"] = P.plain("SafeBark", (0.115, 0.088, 0.060), rough=0.95)
    M["pine"] = P.plain("SafePine", (0.022, 0.048, 0.040), rough=1.0)
    M["pine_snow"] = P.plain("SafePineSnow", (0.42, 0.48, 0.52), rough=0.9)
    M["snow"] = P.plain("SafeSnow", (0.55, 0.60, 0.64), rough=0.9)

    # ---- light sources -------------------------------------------------------------
    M["night"] = emis("SafeNight", (0.16, 0.30, 0.52), 2.8, backface_cull=False)
    M["window_glow"] = emis("SafeWindowGlow", (0.30, 0.52, 0.80), 2.2, backface_cull=False)
    M["moon"] = emis("SafeMoon", (0.72, 0.84, 1.0), 6.0)
    M["fluor"] = emis("SafeFluorTube", (0.66, 0.86, 1.0), 6.5)
    M["fluor_dim"] = emis("SafeFluorDim", (0.30, 0.44, 0.52), 2.2)
    M["lamp_glow"] = emis("SafeLampGlow", (1.0, 0.64, 0.30), 4.6)
    M["flame"] = emis("SafeFlame", (1.0, 0.36, 0.055), 6.5, alpha=0.8, backface_cull=False)
    M["ember"] = emis("SafeEmber", (1.0, 0.20, 0.020), 4.0)
    M["screen"] = emis("SafeScreen", (0.22, 0.95, 0.40), 3.2)
    M["led_red"] = emis("SafeLedRed", (1.0, 0.055, 0.030), 6.0)
    M["led_amber"] = emis("SafeLedAmber", (1.0, 0.42, 0.035), 5.0)
    M["led_green"] = emis("SafeLedGreen", (0.25, 1.0, 0.35), 5.0)
    return M
