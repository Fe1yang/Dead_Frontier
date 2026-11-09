import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the truck must stay on screen behind the armory overlay, otherwise the shop turns into the
# bare test world
old_vis = 'shop_truck.visible=state=="shop"'
n = t.count(old_vis)
t = t.replace(old_vis, 'shop_truck.visible=state in ["shop", "armory"]')
print("truck visibility lines patched:", n)

# and the shop music keeps playing while browsing the armory
old_music = 'sound.music_state(payfail_return_state if state=="payfail" else (map_return_state if state=="map" else state))'
assert t.count(old_music) == 1
new_music = ('sound.music_state(payfail_return_state if state=="payfail" else '
             '(map_return_state if state=="map" else ("shop" if state=="armory" else state)))')
t = t.replace(old_music, new_music, 1)

# opening / closing the armory must not hide the truck either
t = t.replace(
    '''func open_armory() -> void:
	armory_return = state
	armory_index = 0
	state = "armory"
	_armory_show_weapon()''',
    '''func open_armory() -> void:
	armory_return = state
	armory_index = 0
	state = "armory"
	shop_truck.visible = true
	player.visible = false
	_armory_show_weapon()''',
    1,
)

t = t.replace(
    '''func close_armory() -> void:
	state = armory_return if armory_return != "" else "shop"''',
    '''func close_armory() -> void:
	state = armory_return if armory_return != "" else "shop"
	shop_truck.visible = state in ["shop", "armory"]''',
    1,
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armory keeps the truck and the shop music")
