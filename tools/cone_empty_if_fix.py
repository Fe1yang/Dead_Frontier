import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

out = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.strip() == "if decor_rng.randf() < 0.015:":
        # body was the cone that no longer exists: skip the empty if
        i += 1
        continue
    out.append(line)
    i += 1

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("removed the empty cone if block")
