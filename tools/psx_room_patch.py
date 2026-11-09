import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the PSX living room replaces the bunker set
old = '''func _build_set() -> void:
	# The safehouse is a modelled concrete bunker interior with its own floor, walls,
	# blast door, boarded window and props. If the GLB is missing (or fails to load)
	# the old box room below still stands in.
	if _build_safehouse(): return
	_build_set_legacy()'''
new = '''func _build_set() -> void:
	if _build_psx_room(): return
	# Fallbacks, kept for the case where the PSX pack is not in the project.
	if _build_safehouse(): return
	_build_set_legacy()'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

builder = '''## The lobby is a PSX modular living room built from the Wallcoeur PSX house pack.
## Every tile is 4 m, so the room is laid on that grid: 8 m wide, 12 m deep, 4 m tall.
const PSX_DIR := "res://assets/models/lobby_psx/"


func _psx(path: String, pos: Vector3, yaw: float = 0.0) -> Node3D:
	var full := PSX_DIR + path + ".glb"
	if not ResourceLoader.exists(full):
		return null
	var node := (load(full) as PackedScene).instantiate() as Node3D
	node.position = pos
	node.rotation.y = yaw
	add_child(node)
	return node


func _build_psx_room() -> bool:
	if not ResourceLoader.exists(PSX_DIR + "floorWood.glb"):
		return false
	# --- shell -----------------------------------------------------------------
	# floor: 2 x 3 tiles of 4 m, sunk so the surface sits at y = 0
	for gx in range(-1, 1):
		for gz in range(-1, 2):
			_psx("floorWood", Vector3(gx * 4.0 + 2.0, -0.05, gz * 4.0 + 2.0))
	# ceiling
	for gx in range(-1, 1):
		for gz in range(-1, 2):
			_psx("ceilingPlaster", Vector3(gx * 4.0 + 2.0, 0.0, gz * 4.0 + 2.0))
	# back wall (behind the survivor) and the two side walls
	_psx("wallPlaster", Vector3(0.0, 0.0, -5.95))
	_psx("wallPlaster", Vector3(-6.0, 0.0, 0.0), PI * 0.5)
	_psx("wallPlaster", Vector3(6.0, 0.0, 0.0), -PI * 0.5)
	# --- furniture -------------------------------------------------------------
	_psx("carpet2", Vector3(0.0, 0.0, -0.4))
	_psx("couchBig", Vector3(0.0, 0.0, -3.05))
	_psx("tableSmall", Vector3(0.0, 0.0, -1.15))
	_psx("tv", Vector3(-4.2, 1.05, -2.6), PI * 0.5)
	_psx("sideboard", Vector3(-4.9, 0.0, -2.6), PI * 0.5)
	_psx("shelves", Vector3(5.0, 0.0, -2.2), -PI * 0.5)
	_psx("plant", Vector3(4.4, 0.0, 2.6))
	_psx("plant", Vector3(-4.6, 0.0, 3.4))
	_psx("chair", Vector3(2.4, 0.0, -1.4), -PI * 0.4)
	_psx("painting", Vector3(0.0, 1.75, -5.86))
	_psx("bookStack", Vector3(-0.55, 0.72, -1.2))
	_psx("tableLamp", Vector3(0.55, 0.72, -1.25))
	_psx("windowCurtains", Vector3(3.2, 0.0, -5.9))
	return true


'''
anchor = "const SAFEHOUSE_ASSET:="
assert t.count(anchor) == 1
t = t.replace(anchor, builder + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("PSX living room builder added")
