import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

fixed = 0
for i, line in enumerate(lines):
    if line == '\t\t\tstate="paused"; _release_touches(); _freeze_world(true)' and i + 1 < len(lines) \
       and lines[i + 1].strip().startswith('elif state=="paused"'):
        lines[i] = '\t\t\t\tstate="paused"; _release_touches(); _freeze_world(true)'
        fixed += 1

text = "\n".join(lines)

# unfreeze whenever the run leaves the paused state
old = '\t\t\telif state=="paused": state="playing"'
new = '\t\t\telif state=="paused":\n\t\t\t\tstate="playing"; _freeze_world(false)'
if text.count(old) == 1:
    text = text.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(text)
print("indent fixed:", fixed)
