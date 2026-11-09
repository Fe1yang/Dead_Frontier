import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The dog clip is authored for a quadruped skeleton; on the human rig it stretches the neck and
# pushes the hands through the road. A hunched human sprint reads as crawling without deforming.
old = '\tif kind=="jockey": clip_name="Dog_Run"  # the asset ships the quadruped dog clips'
new = '\tif kind=="jockey": clip_name="Zombie_Walk_Fwd"  # dog clips deform the human rig'
assert t.count(old) == 1
t = t.replace(old, new, 1)

old_lean = "const JOCKEY_LEAN_DEG:=27.0"
new_lean = "const JOCKEY_LEAN_DEG:=58.0   # pitching the body forward turns the sprint into a crawl"
assert t.count(old_lean) == 1
t = t.replace(old_lean, new_lean, 1)

old_drop = "const JOCKEY_DROP:=-0.12"
new_drop = "const JOCKEY_DROP:=-0.30"
assert t.count(old_drop) == 1
t = t.replace(old_drop, new_drop, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey: humanoid clip, 58 deg lean, lowered")
