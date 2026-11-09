import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the jockey asset ships dog-family clips, so the old clip name never matched and it slid
old = '\tif kind=="jockey": clip_name="Jockey_Quad_Run"'
new = '\tif kind=="jockey": clip_name="Dog_Run"  # the asset ships the quadruped dog clips'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# a crawling beast should be lower and smaller than the walkers, not twice their bulk
old_scale = '\tvar clip_name := "Zombie_Walk_Fwd"'
new_scale = '\tif kind=="jockey":\n\t\tmodel.scale *= JOCKEY_SCALE\n\tvar clip_name := "Zombie_Walk_Fwd"'
assert t.count(old_scale) == 1
t = t.replace(old_scale, new_scale, 1)

if "JOCKEY_SCALE" not in t.split("func configure")[0]:
    t = t.replace("const JOCKEY_DROP:=-0.12", "const JOCKEY_DROP:=-0.12\nconst JOCKEY_SCALE:=0.62   # it came in twice the bulk of the walkers", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey: dog run clip + 0.62 scale")
