import io
import shutil

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
src_png = r"C:\Users\user\AppData\Local\Temp\vfxbundle\brackeys_vfx_bundle\particles\alpha\flame_01_a.png"
dst_png = ROOT + r"\assets\vfx\flame_jet.png"
shutil.copyfile(src_png, dst_png)
print("copied flame_01_a.png -> flame_jet.png")

p = ROOT + r"\scripts\player_3d.gd"
h = io.open(p, encoding="utf-8").read()

start = h.find("func _build_flame_jet() -> void:")
assert start > 0
end = h.find("func pulse_flame", start)
assert end > start
block = h[start:end]

block = block.replace(
    'mat.albedo_texture = load("res://assets/vfx/flame_particle.png")',
    'mat.albedo_texture = load("res://assets/vfx/flame_jet.png")',
)
block = block.replace(
    "mat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX",
    "mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD",
)
if "mat.albedo_color" not in block:
    anchor = "mat.vertex_color_use_as_albedo = true"
    assert block.count(anchor) == 1
    block = block.replace(
        anchor,
        anchor + "\n\t# additive at a third brightness: bright enough to read as fire, not a white sheet\n\tmat.albedo_color = Color(1.0, 1.0, 1.0, 0.35)",
        1,
    )
else:
    block = block.replace("mat.albedo_color = Color(1.0, 0.55, 0.15, 1.0)", "mat.albedo_color = Color(1.0, 1.0, 1.0, 0.35)")

h = h[:start] + block + h[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("jet uses flame_jet.png, ADD blend at 0.35")
