import io

MP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
HP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"

t = io.open(MP, encoding="utf-8").read()

# tab 4 ("weapons") gets the fourth slot; tab 3 (vehicles) keeps the third
old_slot = "\tvar slot := 2 if t == 3 else t"
new_slot = "\tvar slot := 3 if t == 4 else (2 if t == 3 else t)"
assert t.count(old_slot) == 1
t = t.replace(old_slot, new_slot, 1)

# one card in the weapons tab
old_count = '\tif lobby_tab==3: return LOBBY_VEHICLE_CARDS # BIKE / SPORT / CRUISER / GOLD / TANK / SEDAN'
new_count = old_count + '\n\tif lobby_tab==4: return 1  # the flamethrower'
assert t.count(old_count) == 1
t = t.replace(old_count, new_count, 1)

# ownership rides on the store record the purchase already writes
old_owned = "func vehicle_is_owned(id: String) -> bool:"
assert t.count(old_owned) == 1
t = t.replace(
    old_owned,
    '## The flamethrower is a one-off store purchase; the purchase record is the ownership flag.\n'
    "func flame_owned() -> bool:\n"
    '\treturn bool(store_owned.get("weapon_flame", false))\n\n' + old_owned,
    1,
)

# tapping the weapon card opens the store where it is sold
old_tap = "\t\t\tif lobby_tab==3:"
assert t.count(old_tap) == 1
t = t.replace(
    old_tap,
    "\t\t\tif lobby_tab==4:\n"
    "\t\t\t\topen_store()\n"
    "\t\t\t\treturn\n" + old_tap,
    1,
)

# owned flamethrower is carried into every run
old_start = "\tplayer.reset(); player.apply_meta(meta_upgrades); player.set_aim(aim_direction)"
assert t.count(old_start) == 1
t = t.replace(
    old_start,
    old_start + '\n\tif flame_owned():\n\t\tplayer.set_weapon("FLAME")',
    1,
)

io.open(MP, "w", encoding="utf-8", newline="\n").write(t)

h = io.open(HP, encoding="utf-8").read()

old_tabs = "\tfor t in [0, 1, 3]:"
assert h.count(old_tabs) == 1
h = h.replace(old_tabs, "\tfor t in [0, 1, 3, 4]:", 1)

old_label = '\t\t_text_center("载具" if t==3 else ShopText.text(lang,"chars" if t==0 else "pets"),Vector2(tab.get_center().x,tab.end.y-12),14,WHITE if tab_on else MUTED)'
new_label = (
    '\t\tvar tlabel: String = "载具" if t==3 else ("武器" if t==4 else ShopText.text(lang,"chars" if t==0 else "pets"))\n'
    '\t\t_text_center(tlabel,Vector2(tab.get_center().x,tab.end.y-12),14,WHITE if tab_on else MUTED)'
)
assert h.count(old_label) == 1
h = h.replace(old_label, new_label, 1)

# gold card for the flamethrower
old_branch = "\tif game.lobby_tab==3:\n\t\t# Vehicle card: same anatomy as the pet/skin cards - art, lock overlay, name."
assert h.count(old_branch) == 1
weapon_branch = '''	if game.lobby_tab==4:
		# Flamethrower: a gold-framed card, because it is the one high-value weapon in the game.
		var owned: bool=game.flame_owned()
		var gold:=Color("e8b84b")
		_panel(vis,Color(0.16,0.12,0.05,0.95) if owned else Color(0.10,0.08,0.03,0.85),gold if whole else Color(gold,0.55),2)
		var wtex: Texture2D=_store_art("weapon_flame")
		var wr2:=Rect2(card.position+Vector2(5,5),card.size-Vector2(10,30))
		var wvis:=wr2.intersection(view)
		if wtex and wvis.size.y>1.0:
			var wts:=wtex.get_size()
			clean_ops.append(["region",wtex,wvis,Rect2((wvis.position-wr2.position)/wr2.size*wts,wvis.size/wr2.size*wts)])
		if not owned and wvis.size.y>1.0:
			_box(wvis,Color(0,0,0,0.55))
		if whole:
			_text_center("火焰喷射器" if String(lang).begins_with("zh") else "FLAMETHROWER",Vector2(card.get_center().x,card.end.y-9),13,gold)
			if owned:
				draw_rect(Rect2(card.position.x+6,card.end.y-5,card.size.x-12,2),gold)
		return

''' + old_branch
h = h.replace(old_branch, weapon_branch, 1)

io.open(HP, "w", encoding="utf-8", newline="\n").write(h)
print("weapons tab wired: slot, count, tap, card, auto-equip")
