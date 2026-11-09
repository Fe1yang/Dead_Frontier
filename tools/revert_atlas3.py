import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# undo whichever atlas switch is currently in place
pattern = re.compile(
    r'\t\tvar path: String="res://assets/models/environment/atlas/"\+asset\+"\.glb"\n'
    r'\t\tif not ResourceLoader\.exists\(path\): path="res://assets/models/environment/"\+asset\+"\.glb"'
)
replacement = (
    '\t\t# Authored districts. Every atlas build flattened the road into a grey slab, and the\n'
    '\t\t# ground is what the player looks at for the whole run, so the speed is not worth it.\n'
    '\t\tvar path: String="res://assets/models/environment/"+asset+".glb"'
)
t2, n = pattern.subn(replacement, t)
assert n == 1, n
io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
print("reverted to the authored districts")
