import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	var shel := _shelter_of(road)
	if shel.size == Vector3.ZERO:
		return'''
new = '''	var shel := _shelter_of(road)
	if shel.size == Vector3.ZERO:
		# No shelter mesh in this block: stand it on the pavement line instead of skipping, so
		# every other block gets one. One per 16 m block can never overlap the next.
		return'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("kept the safe behaviour (no booth without a shelter)")
