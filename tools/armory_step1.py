import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# ---------- main: state, roster, stats ----------
p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "func open_armory" not in t:
    anchor = "func close_shop() -> void:"
    assert t.count(anchor) == 1
    block = '''## Armory: a browsable 3D catalogue of every weapon, opened from the supply truck.
const ARMORY_BTN := Rect2(404, 80, 112, 40)
const ARMORY_WEAPONS := ["PISTOL", "MAKAROV", "SUOMI", "SMG", "SHOTGUN", "SNIPER", "LAUNCHER", "FLAME"]
var armory_index := 0
var armory_return := "shop"

## Damage / rate / magazine for every weapon, taken from the same table set_weapon uses.
const ARMORY_STATS := {
	"PISTOL":   {"damage": 24.0, "rate": 0.42, "mag": 12},
	"MAKAROV":  {"damage": 20.0, "rate": 0.36, "mag": 8},
	"SUOMI":    {"damage": 11.0, "rate": 0.085, "mag": 70},
	"SMG":      {"damage": 12.0, "rate": 0.095, "mag": 36},
	"SHOTGUN":  {"damage": 30.0, "rate": 0.72, "mag": 8},
	"SNIPER":   {"damage": 95.0, "rate": 0.85, "mag": 5},
	"LAUNCHER": {"damage": 180.0, "rate": 1.0, "mag": 4},
	"FLAME":    {"damage": 22.0, "rate": 0.12, "mag": 100},
}

func armory_weapon_id() -> String:
	return String(ARMORY_WEAPONS[clampi(armory_index, 0, ARMORY_WEAPONS.size() - 1)])

func armory_step(side: int) -> void:
	armory_index = posmod(armory_index + side, ARMORY_WEAPONS.size())

func open_armory() -> void:
	armory_return = state
	armory_index = 0
	state = "armory"

func close_armory() -> void:
	state = armory_return if armory_return != "" else "shop"

'''
    t = t.replace(anchor, block + anchor, 1)

# tap: the armory button inside the supply truck screen
old_tap = '\tif state=="shop":'
idx = t.find(old_tap)
assert idx > 0
line_end = t.find("\n", idx)
t = t[:line_end + 1] + '\t\tif ARMORY_BTN.has_point(pos): open_armory(); return true\n' + t[line_end + 1:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main: armory state, roster and stats")

# ---------- hud: overlay, panel, bars ----------
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()

if "func _draw_armory" not in h:
    anchor2 = "func _draw_shop() -> void:"
    assert h.count(anchor2) == 1
    draw = '''## Armory overlay: the supply truck dims behind a dark sheet and the weapon card takes the
## centre of the screen. Step 1: panel, name and the three stat bars.
func _draw_armory() -> void:
	_box(Rect2(0, 0, 540, game.ui_h), Color(0, 0, 0, 0.72))
	_panel(Rect2(30, 90, 480, 700), Color(0.03, 0.034, 0.038, 0.97), Color(LINE, 1.0), 0)
	_bold_text("军械库" if String(game.language_code).begins_with("zh") else "ARMORY", Vector2(60, 132), 26, WHITE)
	_text("%d / %d" % [game.armory_index + 1, game.ARMORY_WEAPONS.size()], Vector2(430, 132), 15, MUTED)
	var id: String = game.armory_weapon_id()
	var stats: Dictionary = game.ARMORY_STATS.get(id, {})
	# name
	_bold_text(id, Vector2(60, 610), 24, WHITE)
	# bars: damage / rate / magazine, normalised against the strongest weapon
	var dmg: float = float(stats.get("damage", 0.0))
	var rate: float = 1.0 / maxf(0.05, float(stats.get("rate", 0.3)))
	var mag: float = float(stats.get("mag", 1))
	var rows := [["伤害", dmg / 180.0, str(int(dmg))],
		["攻速", rate / (1.0 / 0.085), "%.1f/s" % rate],
		["容量", mag / 100.0, str(int(mag))]]
	var y: float = 640.0
	for row in rows:
		_text(String(row[0]), Vector2(60, y + 4), 15, MUTED)
		var bar := Rect2(110, y - 12, 280, 16)
		_box(bar, Color(0.10, 0.11, 0.12, 0.95), Color(0.25, 0.26, 0.27, 1.0), 1.0)
		var fill: float = clampf(float(row[1]), 0.0, 1.0)
		if fill > 0.0:
			_box(Rect2(bar.position.x + 1, bar.position.y + 1, (bar.size.x - 2) * fill, bar.size.y - 2), Color("ffd75e"), Color("ffd75e"), 0.0)
		_text(String(row[2]), Vector2(404, y + 4), 15, GOLD)
		y += 34.0
	# nav
	_box(Rect2(60, 736, 60, 44), Color(0.10, 0.11, 0.12, 1.0), Color(LINE, 1.0), 0)
	_text_center("‹", Vector2(90, 764), 22, WHITE)
	_box(Rect2(420, 736, 60, 44), Color(0.10, 0.11, 0.12, 1.0), Color(LINE, 1.0), 0)
	_text_center("›", Vector2(450, 764), 22, WHITE)
	_button(Rect2(24, 24, 100, 48), "‹  " + game.localize("back"), false)

'''
    h = h.replace(anchor2, draw + anchor2, 1)

# route the draw call
if '"_draw_armory"' not in h:
    old_route = '\tif game.state=="shop": _draw_shop()'
    if h.count(old_route) == 1:
        h = h.replace(old_route, old_route + '\n\tif game.state=="armory": _draw_armory()', 1)

io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("hud: armory overlay drawn")
