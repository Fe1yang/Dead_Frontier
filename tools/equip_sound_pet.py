import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

p = base + r"\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# pets: play the cue when an owned pet is actually equipped
start = t.find("func select_pet(index: int) -> void:")
assert start > 0
end = t.find("\nfunc ", start + 10)
body = t[start:end]
if 'sound.play("equip")' not in body:
    # the owning path sets pet_choice / pet_equipped
    for old, new in (
        ("\tpet_choice=index", "\tpet_choice=index; sound.play(\"equip\")"),
        ("\tpet_equipped=true", "\tpet_equipped=true"),
    ):
        if old in body:
            body = body.replace(old, new, 1)
            break
    t = t[:start] + body + t[end:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pet equip cue added" if 'sound.play("equip")' in body else "pet path unchanged")
