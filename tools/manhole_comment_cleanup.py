import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

out = [ln for ln in lines if ln.strip() != "# manholes sit along the pavement line, roughly aligned with the street"]
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("stale manhole comment removed; lines dropped:", len(lines) - len(out))
