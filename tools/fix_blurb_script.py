import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\tools\unlock_all_future_text.py"
t = io.open(p, encoding="utf-8").read()

old = '''    if m:
        lang = m.group(1)
        continue
'''
new = '''    if m:
        lang = m.group(1)
'''
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("block detection fixed")
