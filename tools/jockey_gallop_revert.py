import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

# my duplicate builder (the file already builds the same gallop into `gait`)
dup_build = ('\t\tvar sk: Skeleton3D = model.find_child("Skeleton3D", true, false) as Skeleton3D\n'
             '\t\tif sk != null:\n'
             '\t\t\tjockey_gallop = DogGallop.new(sk, {})\n')
t = t.replace(dup_build, "")

dup_tick = ('\tif kind=="jockey" and jockey_gallop != null:\n'
            '\t\tjockey_gallop.step(delta, 1.25)\n')
t = t.replace(dup_tick, "")

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("duplicate gallop removed; the existing gait stays")
