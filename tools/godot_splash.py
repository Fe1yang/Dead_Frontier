import io

for p in (
    r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\project.godot",
    r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\project.godot",
):
    t = io.open(p, encoding="utf-8").read()
    out = []
    for line in t.split("\n"):
        s = line.strip()
        if s.startswith("boot_splash/image=") or s.startswith("boot_splash/fullsize=") or s.startswith("boot_splash/use_filter="):
            continue
        out.append(line)
    io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("restored the engine splash in", p.split("\\")[-3])
