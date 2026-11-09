import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"
t = io.open(p, encoding="utf-8").read()

# The dictionary already had unlock_all / unlock_all_desc; remove the duplicates I injected.
count = 0
while '"unlock_all_desc_TMP":' in t:
    i = t.find('"unlock_all_desc_TMP":')
    j = t.find('",', i) + 2
    t = t[:i] + t[j:]
    count += 1

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("removed injected duplicates:", count, "remaining desc keys:", t.count('"unlock_all_desc"'))
