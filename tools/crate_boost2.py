import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) everything on a drop goes up by half again
t = t.replace("const ITEM_BOOST := 1.15", "const ITEM_BOOST := 1.75", 1)

# 2) never let a drop shrink below something you can actually see
old = "\t\tweapon_model.scale *= Vector3.ONE*(float(WEAPON_SCALES.get(weapon_id,0.6))*ITEM_BOOST)"
new = '''		weapon_model.scale *= Vector3.ONE*(float(WEAPON_SCALES.get(weapon_id,0.6))*ITEM_BOOST)
		# a small prop (a vest, a can) otherwise reads as an empty barrel from a few metres away
		var shown := _model_span(weapon_model) * weapon_model.scale.x
		if shown > 0.01 and shown < 0.85:
			weapon_model.scale *= 0.85 / shown'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate items 1.75x with a 0.85 m floor")
