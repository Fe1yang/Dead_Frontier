import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) drag state starts when a press lands on the 3D area
old = '\tif state=="shop":'
idx = t.find(old)
assert idx > 0
line_end = t.find("\n", idx)
insert = ('\tif state=="armory":\n'
          '\t\tif ARMORY_VIEW.has_point(pos):\n'
          '\t\t\tarmory_drag = true\n'
          '\t\t\treturn true\n')
t = t[:line_end + 1] + insert + t[line_end + 1:]

# 2) the rect constant next to the other armory data
t = t.replace(
    'const ARMORY_WEAPONS := ["PISTOL", "MAKAROV", "SUOMI", "SMG", "SHOTGUN", "SNIPER", "LAUNCHER", "FLAME"]',
    'const ARMORY_WEAPONS := ["PISTOL", "MAKAROV", "SUOMI", "SMG", "SHOTGUN", "SNIPER", "LAUNCHER", "FLAME"]\n'
    'const ARMORY_VIEW := Rect2(40, 158, 460, 380)   # where the 3D weapon is drawn; drag it to spin',
    1,
)

# 3) spin the model while dragging; any release clears the flag
if "armory_spin -= event.relative.x" not in t:
    anchor = "\tif state=="
    pos = t.find("\tif state==")
    spin = '''	if armory_drag and armory_viewport != null and is_instance_valid(armory_model):
		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
		elif (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed):
			armory_drag = false
'''
    t = t[:pos] + spin + t[pos:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armory drag wired")
