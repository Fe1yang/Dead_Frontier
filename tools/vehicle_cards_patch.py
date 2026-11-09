import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

t = t.replace(
    "const LOBBY_VEHICLE_CARDS:=3   # bikes only: the tank and the saloon are never shown in the lobby",
    "const LOBBY_VEHICLE_CARDS:=5   # every vehicle keeps its card; only the preview is limited",
    1,
)

old = "\t\t\t\tvehicle_choice=i; lobby.set_vehicle_visual(i)"
new = (
    "\t\t\t\tvehicle_choice=i\n"
    "\t\t\t\t# The tank (3) and the saloon (4) keep their card, art and name, but are never\n"
    "\t\t\t\t# mounted on the 3D stage: mounting those two huge models here stalls the lobby.\n"
    "\t\t\t\tif i <= 3:\n"
    "\t\t\t\t\tlobby.set_vehicle_visual(i)\n"
    "\t\t\t\telse:\n"
    "\t\t\t\t\tlobby.set_vehicle_visual(vehicle_choice if vehicle_choice <= 3 else 0)\n"
    "\t\t\t\t\tlobby.focus_vehicle = false"
)
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("five vehicle cards, preview limited to the bikes")
