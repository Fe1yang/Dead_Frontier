import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the flag is `weapon_equipped` (the flamethrower is the only lobby weapon)
t = t.replace("\t\t\t\telif flame_equipped:", "\t\t\t\telif weapon_equipped:", 1)
t = t.replace("\t\t4:\n\t\t\tflame_equipped = true\n\t\t\t_save()",
              "\t\t4:\n\t\t\tweapon_equipped = true\n\t\t\t_save()", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("uses the real weapon_equipped flag")
