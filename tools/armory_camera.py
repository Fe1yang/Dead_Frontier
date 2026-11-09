import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '\tif scene_state=="offer": scene_state=offer_return_state'
new = ('\tif scene_state=="offer": scene_state=offer_return_state\n'
       '\t# the armory is an overlay on the supply truck, so it uses the truck camera\n'
       '\tif scene_state=="armory": scene_state="shop"')
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armory now renders with the supply truck camera")
