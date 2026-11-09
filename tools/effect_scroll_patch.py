import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func _tick_effects(delta: float) -> void:
	for i in range(effects.size()-1,-1,-1):
		var e=effects[i]; e.tick(delta)'''
new = '''func _tick_effects(delta: float) -> void:
	for i in range(effects.size()-1,-1,-1):
		var e=effects[i]
		# Effects belong to the world, so they ride the scrolling road like bullets and crates.
		# Without this, a barrel explosion stayed at a fixed z and travelled with the player.
		e.position.z += ROAD_SPEED * delta
		e.tick(delta)'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("effects now scroll with the road")
