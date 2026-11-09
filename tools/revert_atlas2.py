import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		# Atlas build: the buildings are baked into one texture, while the asphalt/pavement keep
		# their own tiling materials so the road still has its surface detail.
		var path: String="res://assets/models/environment/atlas/"+asset+".glb"
		if not ResourceLoader.exists(path): path="res://assets/models/environment/"+asset+".glb"'''
new = '''		# Original authored districts: the atlas build flattened the road into a grey slab,
		# and the ground is the surface the player stares at for the whole run.
		var path: String="res://assets/models/environment/"+asset+".glb"'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("reverted to the authored districts")
