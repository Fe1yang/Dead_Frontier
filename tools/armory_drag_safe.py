import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# 1) the drag state and the 3D rect belong with the armory data
have_view = any("const ARMORY_VIEW" in l for l in lines)
have_drag = any("var armory_drag" in l for l in lines)

for i, l in enumerate(lines):
    if l.startswith("const ARMORY_WEAPONS"):
        if not have_view:
            lines.insert(i + 1, "const ARMORY_VIEW := Rect2(40, 158, 460, 380)   # the 3D weapon; drag it to spin")
        break

if not have_drag:
    for i, l in enumerate(lines):
        if l.startswith("var armory_return"):
            lines.insert(i + 1, "var armory_drag := false")
            break

# 2) a standalone handler, so nothing inside _pointer_down gets restructured
for i, l in enumerate(lines):
    if l.startswith("func _pointer_down(pos: Vector2) -> bool:"):
        lines.insert(i, '''## Armory taps are handled here and nowhere else: the shop/pause branches below share one
## long if-chain, and editing it has broken the build twice.
func _armory_pointer(pos: Vector2) -> bool:
	if state != "armory":
		return false
	if ARMORY_VIEW.has_point(pos):
		armory_drag = true
		return true
	return false


''')
        break

# 3) one call line at the top of _pointer_down
for i, l in enumerate(lines):
    if l.startswith("func _pointer_down(pos: Vector2) -> bool:"):
        lines.insert(i + 1, "\tif _armory_pointer(pos): return true")
        break

# 4) drag rotation inside the existing unhandled input
for i, l in enumerate(lines):
    if l.startswith("func _unhandled_input(event: InputEvent) -> void:"):
        lines.insert(i + 1, '''	if armory_drag and is_instance_valid(armory_model):
		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
			return
		if (event is InputEventScreenTouch and not event.pressed) or (event is InputEventMouseButton and not event.pressed):
			armory_drag = false''')
        break

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("armory drag added through a standalone handler")
