import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		weapon_model.scale *= Vector3.ONE*(float(WEAPON_SCALES.get(weapon_id,0.6))*ITEM_BOOST)
		# a small prop (a vest, a can) otherwise reads as an empty barrel from a few metres away
		var shown := _model_span(weapon_model) * weapon_model.scale.x
		if shown > 0.01 and shown < 0.85:
			weapon_model.scale *= 0.85 / shown'''
new = '''		# every drop is half again bigger than before, except the helmet which already reads well
		var boost: float = 1.0 if weapon_id=="HELMET" else CRATE_ITEM_SCALE
		weapon_model.scale *= Vector3.ONE*(float(WEAPON_SCALES.get(weapon_id,0.6))*boost)
		if weapon_id!="HELMET":
			# a small prop (a vest, a can) otherwise reads as an empty barrel from a few metres away
			var shown := _model_span(weapon_model) * weapon_model.scale.x
			if shown > 0.01 and shown < 0.85:
				weapon_model.scale *= 0.85 / shown'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

if "CRATE_ITEM_SCALE" not in t.split("func _ready")[0]:
    t = t.replace("const ITEM_BOOST := 1.75", "const ITEM_BOOST := 1.75\nconst CRATE_ITEM_SCALE := 1.5   # helmets keep their size", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate items 1.5x, helmet unchanged")
