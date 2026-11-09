import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func _build_set() -> void:
	if _build_psx_room(): return
	# Fallbacks, kept for the case where the PSX pack is not in the project.
	if _build_safehouse(): return
	_build_set_legacy()'''
new = '''func _build_set() -> void:
	# The safehouse is a modelled concrete bunker interior with its own floor, walls,
	# blast door, boarded window and props. If the GLB is missing (or fails to load)
	# the old box room below still stands in.
	if _build_safehouse(): return
	_build_set_legacy()'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("lobby set restored; the PSX room builder stays in the file, unused")
