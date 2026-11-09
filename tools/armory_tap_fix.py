import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# locate the broken region
shop_idx = None
for i, l in enumerate(lines):
    if l == '\tif state=="shop":':
        shop_idx = i
        break
assert shop_idx is not None

# collect the armory block that was wedged into the shop body
arm_start = shop_idx + 1
assert lines[arm_start] == '\tif state=="armory":', lines[arm_start]
arm_end = arm_start
while arm_end + 1 < len(lines) and lines[arm_end + 1].startswith("\t\t"):
    arm_end += 1
arm_block = lines[arm_start:arm_end + 1]

# remove it and put it in front of the shop branch
del lines[arm_start:arm_end + 1]
for offset, l in enumerate(arm_block):
    lines.insert(shop_idx + offset, l)

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("armory tap block moved out of the shop body:", len(arm_block), "lines")
