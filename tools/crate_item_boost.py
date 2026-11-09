import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "ITEM_BOOST" not in t:
    anchor = "const CRATE_SCALE := 2.9"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + "\n## The item floating over a crate/barrel reads too small on a phone: scale it up.\nconst ITEM_BOOST := 1.7", 1)

old = "\t\tweapon_model.scale *= Vector3.ONE*float(WEAPON_SCALES.get(weapon_id,0.6))"
new = "\t\tweapon_model.scale *= Vector3.ONE*(float(WEAPON_SCALES.get(weapon_id,0.6))*ITEM_BOOST)"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# pets use their own fit: scale the model after the fit instead
old_pet = '''		var lift := ModelFix.fit_pet(weapon_model,float(LobbyScene.PETS[pi].get("length",1.1))*1.3)'''
new_pet = '''		var lift := ModelFix.fit_pet(weapon_model,float(LobbyScene.PETS[pi].get("length",1.1))*1.3*ITEM_BOOST)'''
if t.count(old_pet) == 1:
    t = t.replace(old_pet, new_pet, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate item display scaled up by 1.7")
