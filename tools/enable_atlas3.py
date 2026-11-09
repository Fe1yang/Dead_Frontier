import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		var path: String="res://assets/models/environment/"+asset+".glb"'''
new = '''		var path: String="res://assets/models/environment/atlas/"+asset+".glb"
		if not ResourceLoader.exists(path): path="res://assets/models/environment/"+asset+".glb"'''

assert t.count(old) >= 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("atlas path enabled for the 4K test")
