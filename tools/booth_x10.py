import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	# On the station's own pavement line (x 5.1..6.9), not near the kerb. Pulling it to 4.29 put
	# it on the asphalt edge, which is what read as "in the middle of the road".
	var x: float = shel.get_center().x'''
new = '''	# Fixed outer line requested by the user: 10 m from the centre line, well past the kerb.
	var x: float = side * 10.0'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("booth x set to +/-10.0")
