import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# drop the block that was mistakenly placed in _process
start = None
for i, l in enumerate(lines):
    if "armory_drag and armory_viewport != null" in l:
        start = i
        break
assert start is not None
end = start
while end < len(lines) and not lines[end].strip() == "armory_drag = false":
    end += 1
del lines[start:end + 1]

text = "\n".join(lines)

# put it where `event` exists
anchor = "func _input(event: InputEvent) -> void:"
assert text.count(anchor) == 1, text.count(anchor)
block = '''func _input(event: InputEvent) -> void:
	if armory_drag and is_instance_valid(armory_model):
		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
			return
		if (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed):
			armory_drag = false'''

text = text.replace(anchor, block, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(text)
print("drag moved into _input")
