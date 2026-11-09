import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\export_presets.cfg"
t = io.open(P, encoding="utf-8").read()

old = 'application/version="17"'
new = 'application/version="18"'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("CFBundleVersion 17 -> 18")
