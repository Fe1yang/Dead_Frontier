import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	# world coordinates, because the district node carries a scale and props must not inherit it
	node.global_position = world_pos'''
new = '''	# world coordinates, because the district node carries a scale and props must not inherit it.
	# Anything standing on the roadway sits on the asphalt (y=0), not on the 0.14 m pavement, or it
	# hovers and its shadow lands a step away from it.
	var pos := world_pos
	if absf(pos.x) < 4.45:
		pos.y = 0.01
	node.global_position = pos'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props on the roadway now sit on the asphalt")
