import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"
p = base + r"\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# play the equip cue wherever the lobby actually equips something
edits = (
    # survivor equipped from the dropdown
    ("\t\t\tselect_character(equip_menu_index); equip_menu_index=-1; return",
     "\t\t\tselect_character(equip_menu_index); equip_menu_index=-1; sound.play(\"equip\"); return"),
    # vehicle equipped by tapping its card
    ("\t\t\t\t\towned_vehicle=vkey; _save()",
     "\t\t\t\t\towned_vehicle=vkey; _save(); sound.play(\"equip\")"),
)

for old, new in edits:
    if t.count(old) == 1 and "sound.play(\"equip\")" not in t.split(old)[0][-80:]:
        t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("equip cue wired for survivor and vehicle")
