import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

start = t.find("func _build_flame_jet() -> void:")
end = t.find("func pulse_flame() -> void:")
assert start > 0 and end > start
body = t[start:end]

# back to the original sprite
assert body.count('load("res://assets/vfx/flame_soft.png")') == 1
body = body.replace('load("res://assets/vfx/flame_soft.png")', 'load("res://assets/vfx/flame_particle.png")', 1)

# drop the smoke layer that came with the Wallcoeur experiment
smoke_start = body.find("\t# a slower smoke layer over the fire reads as a real plume")
smoke_end = body.find("\tflame_smoke = smoke")
assert smoke_start > 0 and smoke_end > smoke_start
body = body[:smoke_start] + body[smoke_end + len("\tflame_smoke = smoke\n"):]

t = t[:start] + body + t[end:]

# the smoke node is gone, so its per-shot positioning must go too
smoke_use = t.find("\tif is_instance_valid(flame_smoke):")
if smoke_use > 0:
    end_line = t.find("\n", t.find("look_at", smoke_use))
    t = t[:smoke_use] + t[end_line + 1:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame effect reverted to the original sprite, smoke layer removed")
