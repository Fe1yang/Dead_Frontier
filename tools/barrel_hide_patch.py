import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func _explode(barrel: Node3D) -> void:
	barrel.dead=true; sound.play("explosion"); shake=1.0'''
new = '''func _explode(barrel: Node3D) -> void:
	barrel.dead=true
	# hide the body at once: the node is only freed on the next barrel tick, and its charred shell
	# was left standing on the road for that frame (and longer if the tick missed it)
	barrel.visible = false
	sound.play("explosion"); shake=1.0'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("exploded barrels vanish immediately")
