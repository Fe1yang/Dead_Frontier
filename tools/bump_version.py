import io

paths = (
    r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\project.godot",
    r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\project.godot",
)

for p in paths:
    t = io.open(p, encoding="utf-8").read()
    old = 'application/version="19"'
    new = 'application/version="20"'
    assert t.count(old) == 1, p
    io.open(p, "w", encoding="utf-8", newline="\n").write(t.replace(old, new, 1))
    print("bumped", p)
