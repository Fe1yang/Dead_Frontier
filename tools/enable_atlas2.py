import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		# Original authored districts. The baked-atlas build cut the draw calls sharply but
		# flattened the road surface, and the ground quality matters more than the frame time.
		var path: String="res://assets/models/environment/"+asset+".glb"'''
new = '''		# Atlas build: the buildings are baked into one texture, while the asphalt/pavement keep
		# their own tiling materials so the road still has its surface detail.
		var path: String="res://assets/models/environment/atlas/"+asset+".glb"
		if not ResourceLoader.exists(path): path="res://assets/models/environment/"+asset+".glb"'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("atlas districts re-enabled (ground preserved build)")
