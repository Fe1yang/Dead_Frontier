import subprocess

clone = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
out = clone + r"\tools\old_cover.png"
rev = "2a7cff2~1:assets/ui/title_screen_old.png"
res = subprocess.run(["git", "-C", clone, "show", rev], capture_output=True)
data = res.stdout
open(out, "wb").write(data)
print("bytes", len(data), "head", data[:8], "err", res.stderr[:80])
