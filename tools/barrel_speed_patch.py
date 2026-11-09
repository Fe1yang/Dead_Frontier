import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# barrels scrolled at a hardcoded 3.5 m/s while the road uses world_speed, which climbs with the
# survivor's move multiplier, so a barrel drifted forward together with the player.
p = ROOT + r"\scripts\barrel_3d.gd"
t = io.open(p, encoding="utf-8").read()
old = "\tposition.z += 3.5*delta"
new = "\t# main advances barrels with world_speed instead; scrolling here fought it\n\tpass"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("barrel stops self-scrolling")

p2 = ROOT + r"\scripts\main_3d.gd"
h = io.open(p2, encoding="utf-8").read()
old_tick = '''func _tick_barrels(delta: float) -> void:
	for i in range(barrels.size()-1,-1,-1):
		var b=barrels[i]
		if b.dead: barrels.remove_at(i); b.queue_free(); continue
		b.tick(delta)'''
new_tick = '''func _tick_barrels(delta: float) -> void:
	for i in range(barrels.size()-1,-1,-1):
		var b=barrels[i]
		if b.dead: barrels.remove_at(i); b.queue_free(); continue
		b.position.z += world_speed * delta
		b.tick(delta)'''
assert h.count(old_tick) == 1, h.count(old_tick)
h = h.replace(old_tick, new_tick, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("barrels ride world_speed")
