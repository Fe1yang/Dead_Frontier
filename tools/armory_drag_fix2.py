import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# remove the misplaced block (lines that reference 'event' inside _process)
start = None
for i, l in enumerate(lines):
    if "armory_drag and armory_viewport != null" in l:
        start = i
        break
if start is not None:
    end = start
    while end < len(lines) and "armory_drag = false" not in lines[end]:
        end += 1
    del lines[start:end + 1]

text = "\n".join(lines)

# find any existing input handler name
import re
m = re.search(r"func (_unhandled_input|_input)\(event: InputEvent\) -> void:", text)
if m:
    name = m.group(1)
else:
    # no handler: add one before _pointer_down
    anchor = "func _pointer_down(pos: Vector2) -> bool:"
    assert text.count(anchor) == 1
    text = text.replace(anchor, '''func _input(event: InputEvent) -> void:
	if armory_drag and is_instance_valid(armory_model):
		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
			return
		if (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed):
			armory_drag = false


''' + anchor, 1)
    name = "_input"
    io.open(p, "w", encoding="utf-8", newline="\n").write(text)
    print("inserted a fresh _input handler")
    raise SystemExit(0)

sig = "func %s(event: InputEvent) -> void:" % name
block = sig + '''
	if armory_drag and is_instance_valid(armory_model):
		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
			return
		if (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed):
			armory_drag = false'''
text = text.replace(sig, block, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(text)
print("drag hooked into", name)
