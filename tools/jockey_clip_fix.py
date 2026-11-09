import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = 'if kind=="jockey": clip_name="Jockey_Quad_Run"'
new = 'if kind=="jockey": clip_name="Dog_Run"  # the jockey asset only ships the Dog_* clips'

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey plays Dog_Run instead of a clip it does not have")
