import io

paths = (
    r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\export_presets.cfg",
    r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\export_presets.cfg",
)

for p in paths:
    t = io.open(p, encoding="utf-8").read()
    old = 'application/version="20"'
    new = 'application/version="21"'
    assert t.count(old) == 1, (p, t.count(old))
    io.open(p, "w", encoding="utf-8", newline="\n").write(t.replace(old, new, 1))
    print("build 21 ->", p)
