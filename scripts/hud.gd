extends Control

const ShopText=preload("res://scripts/shop_text.gd")
const Localization=preload("res://scripts/localization.gd")
const GameText=preload("res://scripts/game_text.gd")
const INK=Color("0b0e0f")
const HEART=Color("a3201f")
const GrungeShader=preload("res://shaders/ui_grunge.gdshader")
const PANEL=Color("15191a")
const WHITE=Color("f6f6f3")
const MUTED=Color("b3b8b6")
const LINE=Color("4b5050")
const RED=Color("b6383e")
const GOLD=Color("d8b56c")
const ARMOR=Color("83b4c0")

var game: Node
var font: Font
var bold: Font
var portraits: Array[Texture2D]=[]
var hud_portraits: Array[Texture2D]=[]
var menu_art: Texture2D
# Small print and photos are drawn on a child layer without the worn-paint shader so they stay legible.
const CLEAN_TEXT_BELOW:=28 # Latin text smaller than this stays clean
const CLEAN_CJK_BELOW:=44 # dense CJK glyphs need to be much larger before wear is readable
var clean: Control
var clean_ops: Array=[]
# Hand-painted brush strokes used for every panel and button (assets/ui/brush_*.png, white
# alpha masks tinted at draw time) instead of thin outlined boxes.
var brush_button: Array[Texture2D]=[]
var brush_panel: Array[Texture2D]=[]
var brush_line: Array[Texture2D]=[]
const PAINT_RED:=Color("a8201c")
const PAINT_DARK:=Color(0.055,0.06,0.062,0.94)
var cjk: SystemFont
var cjk_black: FontFile
var bold_base: FontFile
var cjk_language:=""
const CJK_FONTS:={
	"zh_CN":["Microsoft YaHei","PingFang SC","Noto Sans CJK SC","Source Han Sans SC","Noto Sans SC"],
	"zh_TW":["Microsoft JhengHei","PingFang TC","Noto Sans CJK TC","Source Han Sans TC","Noto Sans TC"],
	"ja":["Yu Gothic UI","Hiragino Sans","Noto Sans CJK JP","Meiryo","Noto Sans JP"],
	"ko":["Malgun Gothic","Apple SD Gothic Neo","Noto Sans CJK KR","Noto Sans KR"]}

func _update_cjk_font() -> void:
	var code: String=game.language_code if game!=null else "zh_CN"
	if code==cjk_language or cjk==null: return
	cjk_language=code
	cjk.font_names=PackedStringArray(CJK_FONTS.get(code,CJK_FONTS["zh_CN"]))
	# The bundled heavy face has Simplified glyph shapes, so only Simplified Chinese uses it.
	if bold_base and cjk_black: bold_base.fallbacks=[cjk_black,cjk,font.fallbacks[-1]] if code=="zh_CN" else [cjk,font.fallbacks[-1]]

func _ready() -> void:
	var system:=SystemFont.new()
	system.font_names=PackedStringArray(["Noto Sans","Segoe UI","Arial"])
	system.allow_system_fallback=true
	# Condensed poster lettering for all UI text. Han characters go to a CJK font picked for the
	# current language first, so Simplified Chinese never borrows Japanese or Traditional glyph shapes.
	cjk=SystemFont.new(); cjk.allow_system_fallback=true
	var display:=load("res://assets/fonts/hud_condensed_bold.otf") as FontFile
	display.fallbacks=[cjk,system]
	font=display
	# Headings and buttons: separate copy whose Chinese falls back to a heavy poster-weight face
	# (Noto Sans CJK SC Black, bundled) instead of the thin system font.
	bold_base=display.duplicate() as FontFile
	cjk_black=load("res://assets/fonts/hud_cjk_black.otf") as FontFile
	bold_base.fallbacks=[cjk_black,cjk,system]
	var heavy:=FontVariation.new(); heavy.base_font=bold_base; heavy.variation_embolden=0.35; bold=heavy
	# Worn paint look on every bright stroke (see shaders/ui_grunge.gdshader).
	var grunge:=ShaderMaterial.new(); grunge.shader=GrungeShader
	grunge.set_shader_parameter("grunge",load("res://assets/ui/ui_grunge.png"))
	material=grunge
	clean=Control.new(); clean.mouse_filter=Control.MOUSE_FILTER_IGNORE
	clean.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(clean); clean.draw.connect(_draw_clean)
	portraits=[load("res://assets/ui/male_hd_portrait.png"),load("res://assets/ui/female_hd_portrait.png")]
	hud_portraits=[load("res://assets/ui/male_hud_gray.png"),load("res://assets/ui/female_hud_gray.png")]
	menu_art=load("res://assets/ui/title_screen.png")
	for i in range(3):
		brush_button.append(load("res://assets/ui/brush_button_%d.png"%i))
		brush_panel.append(load("res://assets/ui/brush_panel_%d.png"%i))
		brush_line.append(load("res://assets/ui/brush_line_%d.png"%i))

func _process(_delta: float) -> void:
	_update_cjk_font()
	# The title poster already has its own distressed lettering, so leave it untouched.
	if material: (material as ShaderMaterial).set_shader_parameter("strength",0.0 if game!=null and game.state=="menu" else 1.0)
	queue_redraw()

func _draw() -> void:
	clean_ops.clear()
	if game==null or font==null: return
	if game.state in ["playing","paused"]: _draw_hud()
	elif game.state=="intro": _draw_intro()
	elif game.state=="menu": _draw_menu()
	elif game.state=="gameover": _draw_hud(); clean_ops.clear(); _draw_gameover()
	elif game.state=="shop": _draw_shop()
	elif game.state=="lootbox": _draw_lootbox()
	elif game.state=="language": _draw_languages()
	elif game.state=="settings": _draw_settings()
	elif game.state=="character_select": _draw_character_select()
	if game.state=="paused": clean_ops.clear(); _draw_pause() # HUD small print sits under the overlay
	if game.damage_flash>0: draw_rect(Rect2(0,0,540,960),Color(0.65,0.025,0.025,game.damage_flash*0.36))
	draw_rect(Rect2(0,0,540,2),Color(0.45,0.04,0.055,0.65))
	if clean: clean.queue_redraw()

func _draw_clean() -> void:
	for op in clean_ops:
		match op[0]:
			"text": clean.draw_string(op[1],op[2],op[3],HORIZONTAL_ALIGNMENT_LEFT,-1,op[4],op[5])
			"texture": clean.draw_texture_rect(op[1],op[2],false)
			"tinted": clean.draw_texture_rect(op[1],op[2],false,op[3])
			"box": clean.draw_style_box(op[1],op[2])
			"poly": clean.draw_colored_polygon(op[1],op[2])
			"line": clean.draw_polyline(op[1],op[2],op[3],true)

## Player text-size setting (small / medium / large). Small print is scaled most, since that is
## what is hard to read; big headlines barely change so layouts still fit.
func _scaled(size: int) -> int:
	var choice: int=game.text_size if game!=null else 1
	var factor: float=[0.9,1.0,1.25][choice]
	if size>=40: factor=1.0+(factor-1.0)*0.4
	return maxi(8,roundi(size*factor))

func _string(f: Font,pos: Vector2,value: String,size: int,color: Color) -> void:
	size=_scaled(size)
	var limit:=CLEAN_TEXT_BELOW
	for i in range(value.length()):
		if value.unicode_at(i)>0x2E7F: limit=CLEAN_CJK_BELOW; break
	if size<limit: clean_ops.append(["text",f,pos,value,size,color])
	else: draw_string(f,pos,value,HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)

func _draw_intro() -> void:
	draw_rect(Rect2(0,0,540,78),Color(0.01,0.012,0.013,0.94))
	draw_rect(Rect2(0,852,540,108),Color(0.01,0.012,0.013,0.94))
	if game.intro_time<1.4:
		_text_center("追杀者来了" if game.language_code.begins_with("zh") else "THE CHASER IS COMING",Vector2(270,902),30,WHITE)
	else:
		_text_center("跑！不要回头" if game.language_code.begins_with("zh") else "RUN! DON'T LOOK BACK",Vector2(270,902),30,WHITE)
	_text_center("点击跳过" if game.language_code.begins_with("zh") else "TAP TO SKIP",Vector2(270,936),12,MUTED)

func _draw_hud() -> void:
	# Minimal survival HUD: hearts top-left, distance and kills top-centre, ammo and pause top-right.
	for i in range(36):
		draw_rect(Rect2(0,i*4,540,4),Color(0,0,0,0.34*(1.0-i/36.0)))
	_draw_hearts(Vector2(26,22))
	if game.player.has_armor: _draw_armor_badge(Vector2(26,66))
	var dist:=_group_thousands(int(game.distance))
	var num_w:=bold.get_string_size(dist,HORIZONTAL_ALIGNMENT_LEFT,-1,62).x
	var unit_w:=bold.get_string_size("m",HORIZONTAL_ALIGNMENT_LEFT,-1,34).x
	var x0:=270.0-(num_w+8+unit_w)/2.0
	draw_string(bold,Vector2(x0,78),dist,HORIZONTAL_ALIGNMENT_LEFT,-1,62,WHITE)
	draw_string(bold,Vector2(x0+num_w+8,78),"m",HORIZONTAL_ALIGNMENT_LEFT,-1,34,WHITE)
	_draw_skull(Vector2(244,118),17)
	draw_string(bold,Vector2(268,133),"x %d"%game.kills,HORIZONTAL_ALIGNMENT_LEFT,-1,36,WHITE)
	_draw_pause_button(PAUSE_RECT)
	_draw_ammo(Vector2(470,52))
	if game.touch_controls and game.state=="playing":
		_draw_joystick(game.left_origin,game.left_knob,false)
		_draw_joystick(game.right_origin,game.right_knob,true)
		_round_button(game.BTN_RELOAD,"reload",-1,WHITE)
		var swap_to: String=game.player.swap_target()
		_round_button(game.BTN_SWAP,"swap",-1,WHITE if swap_to!="" else Color(1,1,1,0.35))
		if swap_to!="":
			var short:={"PISTOL":"PST","SMG":"SMG","SHOTGUN":"SG","SNIPER":"SNP","RIFLE":"AR","LAUNCHER":"GL"}
			_text_center(short.get(swap_to,swap_to),game.BTN_SWAP+Vector2(0,52),13,WHITE)
		_round_button(game.BTN_FRAG,"frag",game.player.grenade_count,WHITE)
		_round_button(game.BTN_FLASH,"flash",game.player.flashbang_count,Color("cfefff"))
		if game.player.weapon=="LAUNCHER":
			_round_button(game.BTN_FIRE_MODE,"fire",game.player.fire_ammo,Color("ff8a5c"))
	if game.hint_time>0:
		var hint: String=game.localize("aim_stick") if game.touch_controls else GameText.text(game.language_code,"auto_hint")
		_text_center(hint,Vector2(270,186),15,Color(WHITE.r,WHITE.g,WHITE.b,clampf(game.hint_time,0,1)*0.9))
	if game.wave_banner>0:
		var a: float=minf(1,game.wave_banner)
		draw_rect(Rect2(232,214,76,3),Color(0.71,0.12,0.15,a))
		_text_center(game.localize("wave")+" %02d"%game.wave,Vector2(270,256),40,Color(WHITE.r,WHITE.g,WHITE.b,a))
	# (No on-screen name for the Banshee: she just turns up, like any other zombie.)

const PAUSE_RECT:=Rect2(482,14,46,46) # drawn box; the tap area is game.PAUSE_BUTTON

func _group_thousands(value: int) -> String:
	var digits:=str(value); var out:=""
	for i in range(digits.length()):
		if i>0 and (digits.length()-i)%3==0: out+=","
		out+=digits[i]
	return out

func _heart_points(center: Vector2,size: float) -> PackedVector2Array:
	var pts:=PackedVector2Array()
	for i in range(48):
		var t:=TAU*i/48.0
		var x:=16.0*pow(sin(t),3.0)
		var y:=13.0*cos(t)-5.0*cos(2.0*t)-2.0*cos(3.0*t)-cos(4.0*t)
		pts.append(center+Vector2(x,-y)*size/34.0)
	return pts

func _draw_hearts(origin: Vector2) -> void:
	var hp: float=clampf(game.player.health/game.player.max_health,0.0,1.0)*3.0
	for i in range(3):
		var c:=origin+Vector2(18+i*38,14)
		var shape:=_heart_points(c,34)
		draw_colored_polygon(shape,Color(0.05,0.03,0.03,0.55))
		var fill:=clampf(hp-i,0.0,1.0)
		if fill>=0.999: draw_colored_polygon(shape,HEART)
		elif fill>0.0:
			var clip:=PackedVector2Array([c+Vector2(-20,-20),c+Vector2(-20+40*fill,-20),c+Vector2(-20+40*fill,20),c+Vector2(-20,20)])
			for part in Geometry2D.intersect_polygons(shape,clip): draw_colored_polygon(part,HEART)
		shape.append(shape[0]); draw_polyline(shape,Color(0.02,0.01,0.01,0.75),1.5,true)

func _draw_armor_badge(pos: Vector2) -> void:
	var shield:=PackedVector2Array([pos+Vector2(0,0),pos+Vector2(16,-4),pos+Vector2(32,0),pos+Vector2(30,18),pos+Vector2(16,30),pos+Vector2(2,18)])
	draw_colored_polygon(shield,Color(0.30,0.48,0.54,0.95)); shield.append(shield[0]); draw_polyline(shield,WHITE,1.5,true)
	_text("ARMOR",pos+Vector2(40,22),16,ARMOR)

func _draw_skull(c: Vector2,r: float) -> void:
	draw_circle(c+Vector2(0,-r*0.12),r,WHITE)
	draw_rect(Rect2(c+Vector2(-r*0.58,r*0.45),Vector2(r*1.16,r*0.62)),WHITE)
	draw_circle(c+Vector2(-r*0.40,-r*0.05),r*0.30,INK); draw_circle(c+Vector2(r*0.40,-r*0.05),r*0.30,INK)
	draw_colored_polygon(PackedVector2Array([c+Vector2(0,r*0.25),c+Vector2(-r*0.13,r*0.48),c+Vector2(r*0.13,r*0.48)]),INK)
	for k in range(3): draw_line(c+Vector2(-r*0.30+k*r*0.30,r*0.62),c+Vector2(-r*0.30+k*r*0.30,r*1.05),INK,2)

func _draw_pause_button(rect: Rect2) -> void:
	# Plain rounded frame like the round control buttons (no brush underline under it).
	var box:=StyleBoxFlat.new(); box.bg_color=Color(0,0,0,0.30); box.border_color=WHITE
	box.set_border_width_all(2); box.set_corner_radius_all(6); draw_style_box(box,rect)
	draw_rect(Rect2(rect.position+Vector2(15,12),Vector2(5,22)),WHITE)
	draw_rect(Rect2(rect.position+Vector2(26,12),Vector2(5,22)),WHITE)

func _draw_ammo(right_top: Vector2) -> void:
	# "12/48" plus a cartridge icon, right-aligned beside the pause button.
	var label:="%d/∞"%game.player.ammo if game.player.infinite_ammo() else "%d/%d"%[game.player.ammo,game.player.reserve_ammo]
	var w:=bold.get_string_size(label,HORIZONTAL_ALIGNMENT_LEFT,-1,34).x
	var bullet_x:=right_top.x-12
	draw_string(bold,Vector2(bullet_x-14-w,right_top.y),label,HORIZONTAL_ALIGNMENT_LEFT,-1,34,WHITE if game.player.ammo>0 else Color("e66b62"))
	draw_rect(Rect2(bullet_x-4,right_top.y-22,9,20),WHITE)
	draw_colored_polygon(PackedVector2Array([Vector2(bullet_x-4,right_top.y-22),Vector2(bullet_x+0.5,right_top.y-34),Vector2(bullet_x+5,right_top.y-22)]),WHITE)
	draw_rect(Rect2(bullet_x-5,right_top.y-4,11,4),WHITE)
	var weapon_label: String=game.player.weapon
	if game.player.weapon=="LAUNCHER": weapon_label+="  ·  "+("INC x%d"%game.player.fire_ammo if game.player.fire_mode else "FRAG")
	_text_right(weapon_label,Vector2(right_top.x+6,right_top.y+26),16,MUTED)
	if not game.touch_controls:
		_text_right("G x%d   F x%d"%[game.player.grenade_count,game.player.flashbang_count],Vector2(right_top.x+6,right_top.y+48),15,MUTED)
	if game.player.reloading:
		var progress: float=1.0-game.player.reload_timer/game.player.reload_duration
		draw_rect(Rect2(Vector2(right_top.x-110,right_top.y+60),Vector2(116,3)),Color(1,1,1,0.18))
		draw_rect(Rect2(Vector2(right_top.x-110,right_top.y+60),Vector2(116*progress,3)),RED)
		_text_right(game.localize("loading"),Vector2(right_top.x+6,right_top.y+84),15,WHITE)
	elif game.player.ammo==0:
		_text_right(game.localize("auto") if game.auto_reload else game.localize("press_r"),Vector2(right_top.x+6,right_top.y+84),15,Color("e66b62"))

func _round_button(center: Vector2,icon: String,count: int,accent: Color) -> void:
	var r:=34.0
	draw_circle(center,r,Color(0.02,0.02,0.02,0.45))
	draw_arc(center,r,0,TAU,48,WHITE,2.5,true)
	match icon:
		"reload":
			draw_arc(center,15,deg_to_rad(200),deg_to_rad(340),20,WHITE,4,true)
			draw_arc(center,15,deg_to_rad(20),deg_to_rad(160),20,WHITE,4,true)
			var a:=center+Vector2(15,0).rotated(deg_to_rad(340)); var b:=center+Vector2(15,0).rotated(deg_to_rad(160))
			draw_colored_polygon(PackedVector2Array([a+Vector2(-6,-6),a+Vector2(6,-4),a+Vector2(1,7)]),WHITE)
			draw_colored_polygon(PackedVector2Array([b+Vector2(6,6),b+Vector2(-6,4),b+Vector2(-1,-7)]),WHITE)
		"frag":
			draw_circle(center+Vector2(0,4),13,WHITE)
			for k in range(3): draw_line(center+Vector2(-12,-1+k*6),center+Vector2(12,-1+k*6),INK,1.5)
			draw_line(center+Vector2(0,-9),center+Vector2(0,13),INK,1.5)
			draw_rect(Rect2(center+Vector2(-5,-15),Vector2(10,7)),WHITE)
			draw_arc(center+Vector2(9,-12),5,PI*0.5,PI*1.8,10,WHITE,2,true)
		"flash":
			draw_rect(Rect2(center+Vector2(-9,-10),Vector2(18,24)),accent)
			draw_rect(Rect2(center+Vector2(-5,-16),Vector2(10,6)),accent)
			for k in range(3): draw_line(center+Vector2(-9,-4+k*7),center+Vector2(9,-4+k*7),INK,1.5)
		"swap":
			# Two opposing arrows: switch guns.
			draw_line(center+Vector2(-13,-6),center+Vector2(11,-6),accent,3.5)
			draw_colored_polygon(PackedVector2Array([center+Vector2(15,-6),center+Vector2(7,-12),center+Vector2(7,0)]),accent)
			draw_line(center+Vector2(13,7),center+Vector2(-11,7),accent,3.5)
			draw_colored_polygon(PackedVector2Array([center+Vector2(-15,7),center+Vector2(-7,1),center+Vector2(-7,13)]),accent)
		"fire":
			draw_colored_polygon(PackedVector2Array([center+Vector2(0,-17),center+Vector2(11,4),center+Vector2(0,15),center+Vector2(-11,4)]),accent)
			draw_colored_polygon(PackedVector2Array([center+Vector2(0,-4),center+Vector2(5,6),center+Vector2(0,11),center+Vector2(-5,6)]),INK)
	if count>=0:
		draw_circle(center+Vector2(24,24),11,Color(0.05,0.05,0.05,0.85)); draw_arc(center+Vector2(24,24),11,0,TAU,24,accent,1.5,true)
		_text_center(str(count),center+Vector2(24,30),16,WHITE)

func _draw_joystick(origin: Vector2,knob: Vector2,aim: bool) -> void:
	# Two matching thumbsticks: left steers left/right, right turns the survivor (aim).
	draw_circle(origin,62,Color(0.02,0.02,0.02,0.28))
	draw_arc(origin,62,0,TAU,72,WHITE,3,true)
	if aim:
		# Tick marks all the way round: this stick points the survivor in any direction.
		for i in range(12):
			var a:=i*TAU/12.0; var dir:=Vector2(cos(a),sin(a))
			draw_line(origin+dir*50,origin+dir*(57 if i%3 else 44),WHITE,2.5 if i%3 else 3.0)
	else:
		# Only left and right arrows: this stick only moves the survivor sideways.
		for d in [Vector2.LEFT,Vector2.RIGHT]:
			var dir: Vector2=d; var tip: Vector2=origin+dir*50; var side:=Vector2(-dir.y,dir.x)*8
			draw_colored_polygon(PackedVector2Array([tip,tip-dir*12+side,tip-dir*12-side]),WHITE)
	# Both sticks get the same grey thumb knob.
	draw_circle(knob,26,Color(0.62,0.62,0.60,0.92)); draw_arc(knob,26,0,TAU,40,WHITE,2,true)
	if aim:
		# Small sight on the knob so the two sticks are still easy to tell apart.
		for d: Vector2 in [Vector2.UP,Vector2.DOWN,Vector2.LEFT,Vector2.RIGHT]:
			draw_line(knob+d*6,knob+d*14,Color(0.1,0.1,0.1,0.85),2.5)

func _draw_menu() -> void:
	# Full-screen title poster; the gear in its top-right corner opens settings, any other tap starts.
	if menu_art: draw_texture_rect(menu_art,Rect2(0,0,540,960),false)
	else: draw_rect(Rect2(0,0,540,960),INK)

func _crate_icon(c: Vector2,col: Color) -> void:
	# Line-art supply crate, same weight as the settings gear on the poster.
	var w:=2.6
	var front:=PackedVector2Array([c+Vector2(-20,-6),c+Vector2(14,-6),c+Vector2(14,20),c+Vector2(-20,20),c+Vector2(-20,-6)])
	draw_polyline(front,col,w,true)
	draw_polyline(PackedVector2Array([c+Vector2(-20,-6),c+Vector2(-12,-16),c+Vector2(22,-16),c+Vector2(14,-6)]),col,w,true)
	draw_polyline(PackedVector2Array([c+Vector2(22,-16),c+Vector2(22,10),c+Vector2(14,20)]),col,w,true)
	draw_line(c+Vector2(-20,7),c+Vector2(14,7),col,w,true)
	draw_rect(Rect2(c+Vector2(-6,3),Vector2(6,8)),col)

func _chip_text(label: String,rect: Rect2,col: Color) -> void:
	var size:=13
	while font.get_string_size(label,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x>rect.size.x-6 and size>8: size-=1
	_text_center(label,rect.get_center()+Vector2(0,size*0.38),size,col)

func _draw_lootbox() -> void:
	var lang: String=game.language_code
	draw_rect(Rect2(0,0,540,960),Color(0.018,0.022,0.023,0.97))
	_button(Rect2(24,24,100,48),"‹  "+game.localize("back"),false)
	_bold_text(ShopText.text(lang,"cases_title"),Vector2(150,62),26,WHITE)
	_brush_underline(Rect2(146,74,108,14))
	_crate_icon(Vector2(270,400),Color(1,1,1,0.85))
	_text_center(ShopText.text(lang,"soon"),Vector2(270,500),22,WHITE)
	_text_center(ShopText.text(lang,"soon_sub"),Vector2(270,536),14,MUTED)

func _draw_settings() -> void:
	draw_rect(Rect2(0,0,540,960),Color(0.018,0.022,0.023,0.97))
	_bold_text("SETTINGS",Vector2(42,100),32,WHITE)
	_text("AUDIO / GAMEPLAY",Vector2(44,132),14,MUTED)
	_button(Rect2(66,220,408,70),"SFX  /  "+("OFF" if game.sound.muted else "ON"),false)
	_button(Rect2(66,316,408,70),game.localize("reload_auto") if game.auto_reload else game.localize("reload_manual"),false)
	_button(Rect2(66,412,408,70),"文   "+game.localize("language"),false)
	var lang: String=game.language_code
	var sep: String="：" if lang in ["zh_CN","zh_TW","ja"] else ": "
	_button(Rect2(66,508,408,70),"Aa   %s%s%s"%[ShopText.text(lang,"text_size"),sep,ShopText.text(lang,"ts_%d"%game.text_size)],false)
	_button(Rect2(66,810,408,64),game.localize("back"),true)

func _draw_character_select() -> void:
	# Character lobby. The 3D survivor stands in the middle (lobby_scene_3d.gd); this draws the frame.
	var lang: String=game.language_code
	draw_rect(Rect2(0,0,540,104),Color(0.015,0.018,0.019,0.82))
	draw_rect(Rect2(0,812,540,148),Color(0.015,0.018,0.019,0.86))
	_button(Rect2(16,22,150,52),game.localize("shop"),false)
	draw_circle(Vector2(196,48),7,GOLD); _text("%05d"%game.bank_coins,Vector2(212,56),20,GOLD)
	_gear_icon(Vector2(501,45))
	# Column headings.
	_text_center(ShopText.text(lang,"chars"),Vector2(62,136),14,WHITE)
	_text_center(ShopText.text(lang,"pets"),Vector2(478,136),14,WHITE)
	for i in range(game.LOBBY_SLOTS):
		var left:=Rect2(game.LOBBY_LEFT_X,game.LOBBY_TOP+i*game.LOBBY_STEP,game.LOBBY_CARD.x,game.LOBBY_CARD.y)
		if i<game.lobby.CHARACTERS.size():
			var on: bool=game.character_choice==i
			_panel(left,Color("1d2223") if on else Color(0.05,0.06,0.06,0.88),RED if on else LINE,0)
			if portraits.size()>i and portraits[i]:
				clean_ops.append(["texture",portraits[i],Rect2(left.position+Vector2(4,4),Vector2(left.size.x-8,left.size.y-30))])
			_text_center(game.lobby.CHARACTERS[i].name,Vector2(left.get_center().x,left.end.y-9),12,WHITE if on else MUTED)
			if on: _brush_underline(Rect2(left.position.x-4,left.end.y-8,left.size.x+8,14))
		else:
			_locked_slot(left)
		var right:=Rect2(game.LOBBY_RIGHT_X,game.LOBBY_TOP+i*game.LOBBY_STEP,game.LOBBY_CARD.x,game.LOBBY_CARD.y)
		_locked_slot(right,true)
	# Switch arrows beside the survivor.
	_text_center("‹",Vector2(146,492),56,Color(1,1,1,0.85))
	_text_center("›",Vector2(394,492),56,Color(1,1,1,0.85))
	var name: String=game.lobby.CHARACTERS[game.character_choice].name
	_bold_text(name,Vector2(270-bold.get_string_size(name,HORIZONTAL_ALIGNMENT_LEFT,-1,30).x*0.5,790),30,WHITE)
	_text_center(ShopText.text(lang,"drag"),Vector2(270,806),11,MUTED)
	if game.lobby_toast>0.0:
		var a: float=minf(1.0,game.lobby_toast*2.0)
		_panel(Rect2(170,600,200,46),Color(0.02,0.025,0.026,0.92*a),Color(RED,a),0)
		_text_center(ShopText.text(lang,"coming"),Vector2(270,630),16,Color(1,1,1,a))
	_button(Rect2(66,836,408,76),game.localize("start")+"   ›",true)

func _locked_slot(rect: Rect2,pet:=false) -> void:
	_panel(rect,Color(0.04,0.045,0.047,0.80),Color(LINE,0.7),0)
	var c:=rect.get_center()+Vector2(0,-8)
	if pet:
		# Paw print.
		draw_circle(c+Vector2(0,8),11,Color(1,1,1,0.22))
		for o in [Vector2(-13,-6),Vector2(-5,-14),Vector2(5,-14),Vector2(13,-6)]: draw_circle(c+o,4.5,Color(1,1,1,0.22))
	else:
		# Padlock.
		draw_rect(Rect2(c+Vector2(-12,-2),Vector2(24,20)),Color(1,1,1,0.22))
		draw_arc(c+Vector2(0,-2),8,PI,TAU,16,Color(1,1,1,0.22),3.0)
	_text_center(ShopText.text(game.language_code,"coming"),Vector2(c.x,rect.end.y-10),10,Color(MUTED,0.8))

func _gear_icon(c: Vector2) -> void:
	draw_arc(c,13,0,TAU,24,WHITE,3.0)
	for i in range(8):
		var a:=i*TAU/8.0
		draw_line(c+Vector2(cos(a),sin(a))*13,c+Vector2(cos(a),sin(a))*19,WHITE,5.0)
	draw_circle(c,5,WHITE)

func _character_card(rect: Rect2,index: int) -> void:
	_panel(rect,Color("181b1c"),WHITE if game.character_choice==index else LINE,0)
	if portraits.size()>index and portraits[index]:
		clean_ops.append(["texture",portraits[index],Rect2(rect.position+Vector2(3,3),Vector2(rect.size.x-6,rect.size.y-61))])
	draw_rect(Rect2(rect.position+Vector2(3,rect.size.y-58),Vector2(rect.size.x-6,55)),Color(0.025,0.03,0.031,0.96))
	_text_center("男" if index==0 else "女",rect.position+Vector2(rect.size.x/2,rect.size.y-20),22,WHITE)
	if game.character_choice==index:
		draw_rect(Rect2(rect.position,Vector2(5,rect.size.y)),RED)
		draw_rect(Rect2(rect.position,Vector2(rect.size.x,4)),WHITE)

func _hex_badge(center: Vector2,radius: float,value: String) -> void:
	var points:=PackedVector2Array()
	for i in range(6):
		var angle:=TAU*i/6.0; points.append(center+Vector2(cos(angle),sin(angle))*radius)
	draw_colored_polygon(points,Color(0.04,0.05,0.05,0.88)); points.append(points[0]); draw_polyline(points,LINE,1.5,true)
	_text_center(value,center+Vector2(0,6),17,WHITE)

func _draw_shop() -> void:
	# The 3D window between the panels is a close-up of the gear being upgraded.
	draw_rect(Rect2(0,0,540,118),Color(0.02,0.025,0.026,0.90)); draw_rect(Rect2(0,594,540,366),Color(0.018,0.022,0.023,0.98))
	_button(Rect2(24,24,100,48),"‹  "+game.localize("back"),false)
	_bold_text(game.localize("shop_title"),Vector2(150,62),24,WHITE)
	var lang: String=game.language_code
	_text(ShopText.text(lang,"pick"),Vector2(151,91),13,MUTED)
	_button(Rect2(404,24,112,48),ShopText.text(lang,"cases"),true)
	draw_circle(Vector2(188,617),7,GOLD); _text("%05d"%game.bank_coins,Vector2(207,625),21,GOLD)
	if game.shop_items.is_empty(): return
	var item: Dictionary=game.shop_items[game.shop_index]
	var level: int=game.meta_upgrades.get(item.id,0); var cost: int=game.item_cost(item)
	var maxed: bool=level>=int(item.max_level); var affordable: bool=game.bank_coins>=cost
	# Item card: name, effect, level pips.
	_panel(Rect2(30,642,480,128),Color("141819"),LINE,0); draw_rect(Rect2(30,642,5,128),RED)
	_bold_text(ShopText.text(lang,item.name_key),Vector2(52,684),26,WHITE)
	_text(ShopText.text(lang,item.detail_key),Vector2(53,714),15,MUTED)
	for i in range(int(item.max_level)):
		var pip:=Rect2(53+i*34,734,28,14)
		draw_rect(pip,GOLD if i<level else Color("2b3132"))
	_text("LV %d / %d"%[level,item.max_level],Vector2(232,747),13,GOLD)
	_text("%d / %d"%[game.shop_index+1,game.shop_items.size()],Vector2(452,684),13,MUTED)
	# Prev / upgrade / next.
	_button(Rect2(30,786,80,60),"‹",false)
	_button(Rect2(430,786,80,60),"›",false)
	var label: String
	if maxed: label=ShopText.text(lang,"max")
	else: label="%s  %d %s"%[ShopText.text(lang,"upgrade"),cost,ShopText.text(lang,"coins")]
	_button(Rect2(124,786,292,60),label,affordable and not maxed)
	# Quick-pick chips for every item.
	for i in range(game.shop_items.size()):
		var chip: Dictionary=game.shop_items[i]; var rect:=Rect2(30+i*60,862,56,44); var on: bool=i==game.shop_index
		_panel(rect,Color("2a2021") if on else Color("141819"),RED if on else LINE,0)
		_chip_text(ShopText.text(lang,chip.name_key),rect,WHITE if on else MUTED)
	_text_center("PREMIUM / "+game.localize("planned"),Vector2(270,936),12,Color("cf8c75"))

func _draw_languages() -> void:
	draw_rect(Rect2(0,0,540,960),Color(0.018,0.022,0.023,0.97))
	_bold_text(game.localize("language"),Vector2(30,76),30,WHITE); _text("20 LANGUAGES / NATIVE NAMES",Vector2(32,105),10,MUTED)
	_brush_underline(Rect2(26,117,108,14))
	for i in range(Localization.LANGUAGES.size()):
		var item: Dictionary=Localization.LANGUAGES[i]; var rect:=Rect2(30+(i%2)*245,150+floori(i/2.0)*62,235,50); var selected: bool=item.code==game.language_code
		_panel(rect,Color("2a2021") if selected else Color("141819"),RED if selected else LINE,0)
		if selected: draw_rect(Rect2(rect.position,Vector2(3,rect.size.y)),RED)
		_text_center(item.native,rect.get_center()+Vector2(0,6),16,WHITE)
	_button(Rect2(66,840,408,60),game.localize("back"),true)

func _draw_gameover() -> void:
	var zh: bool=game.language_code.begins_with("zh")
	draw_rect(Rect2(0,0,540,960),Color(0.018,0.021,0.022,0.90))
	_text_center(game.localize("run_over"),Vector2(270,186),50,Color("e15b57")); _brush_underline(Rect2(200,204,140,16))
	_panel(Rect2(54,238,432,330),Color(0.035,0.045,0.046,0.97),LINE,0)
	_stat(game.localize("distance"),"%d m"%int(game.distance),Vector2(80,276)); _stat(game.localize("kills"),"%d"%game.kills,Vector2(300,276))
	# Kill breakdown: tougher zombies are worth more coins.
	var lang: String=game.language_code
	var y:=340.0
	for kind in ["banshee","brute","jockey","runner","walker"]:
		var n: int=int(game.kill_counts.get(kind,0))
		if n<=0: continue
		clean_ops.append(["text",font,Vector2(80,y),ShopText.text(lang,"k_"+kind),_scaled(17),WHITE])
		clean_ops.append(["text",bold,Vector2(262,y),"× %d"%n,_scaled(17),MUTED])
		var coins:="+%d"%int(game.kill_coins.get(kind,0))
		clean_ops.append(["text",bold,Vector2(458-bold.get_string_size(coins,HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(17)).x,y),coins,_scaled(17),GOLD])
		y+=22.0
	clean_ops.append(["text",font,Vector2(80,y),GameText.text(lang,"survival"),_scaled(17),WHITE])
	var surv:="+%d"%game.survival_bonus
	clean_ops.append(["text",bold,Vector2(458-bold.get_string_size(surv,HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(17)).x,y),surv,_scaled(17),GOLD])
	draw_rect(Rect2(80,y+12,378,1),Color(1,1,1,0.12))
	_text(GameText.text(lang,"total"),Vector2(80,y+38),16,MUTED); clean_ops.append(["text",bold,Vector2(80,y+78),"+%d"%game.last_reward,_scaled(36),GOLD])
	_text(GameText.text(lang,"wallet")+"  %d"%game.bank_coins,Vector2(300,y+72),20,GOLD)
	if not game.revive_used:
		_draw_revive_button(Rect2(66,586,408,70))
	else:
		_text_center("本局复活已使用" if zh else "REVIVE ALREADY USED THIS RUN",Vector2(270,628),16,MUTED)
	_button(Rect2(66,672,408,66),ShopText.text(game.language_code,"to_lobby"),true)
	_button(Rect2(66,758,408,54),game.localize("shop"),false)

func _draw_pause() -> void:
	draw_rect(Rect2(0,0,540,960),Color(0.015,0.019,0.020,0.90))
	_bold_text(game.localize("paused"),Vector2(114,370),42,WHITE); _brush_underline(Rect2(110,387,104,14))
	_button(Rect2(66,468,408,58),game.localize("reload_auto") if game.auto_reload else game.localize("reload_manual"),false)
	_button(Rect2(66,548,408,68),game.localize("resume"),true)
	_button(Rect2(66,632,408,58),game.localize("shop"),false)
	_button(Rect2(66,708,408,58),game.localize("restart"),false)
	_button(Rect2(66,784,408,58),GameText.text(game.language_code,"main_menu"),false)

func _draw_revive_button(rect: Rect2) -> void:
	# Rewarded-ad revive: opt-in, clearly labelled as an ad, reward stated up front (AdMob policy).
	var zh: bool=game.language_code.begins_with("zh")
	var ad_status: String=game.revival_ads.status if is_instance_valid(game.revival_ads) else "desktop"
	var busy: bool=game.revive_pending or ad_status=="showing"
	var pulse:=0.5+0.5*sin(Time.get_ticks_msec()/1000.0*4.0)
	var bg:=Color(0.42,0.06,0.07,0.96) if not busy else Color(0.18,0.05,0.05,0.96)
	var box:=StyleBoxFlat.new(); box.bg_color=bg; box.border_color=Color(1,0.45,0.42,0.55+0.45*pulse) if not busy else LINE
	clean_ops.append(["tinted",_pick(brush_button,rect),rect.grow_individual(14,8,14,8),Color(bg.r*1.6,bg.g*1.4,bg.b*1.4,1.0).lerp(Color("c22a24"),0.25+0.25*pulse) if not busy else Color(0.2,0.08,0.08,0.95)])
	_draw_heart_icon(rect.position+Vector2(38,rect.size.y*0.5))
	var label:=("看广告复活" if zh else "WATCH AD TO REVIVE")
	var sub:=("恢复 50% 生命，继续本局" if zh else "Continue this run with 50% HP")
	if busy: label=("广告播放中…" if zh else "AD PLAYING…"); sub=""
	elif ad_status=="loading": sub=("广告加载中…" if zh else "Loading ad…")
	elif ad_status=="unavailable": sub=("广告暂不可用，点击重试" if zh else "Ad unavailable — tap to retry")
	clean_ops.append(["text",bold,rect.position+Vector2(70,44 if sub.is_empty() else 36),label,26,WHITE])
	if not sub.is_empty(): clean_ops.append(["text",font,rect.position+Vector2(70,58),sub,14,Color(1,0.86,0.84)])
	# "AD" tag so the player always knows a video ad will play
	var tag:=Rect2(rect.end.x-58,rect.position.y+20,42,28)
	var tb:=StyleBoxFlat.new(); tb.bg_color=Color(1,1,1,0.95); tb.set_corner_radius_all(4); clean_ops.append(["box",tb,tag])
	var aw:=bold.get_string_size("AD",HORIZONTAL_ALIGNMENT_LEFT,-1,16).x
	clean_ops.append(["text",bold,tag.get_center()+Vector2(-aw/2,6),"AD",16,Color(0.42,0.06,0.07)])

func _draw_heart_icon(c: Vector2) -> void:
	var shape:=_heart_points(c,40)
	clean_ops.append(["poly",shape,Color("e23a35")])
	var outline:=shape.duplicate(); outline.append(shape[0]); clean_ops.append(["line",outline,WHITE,2.0])
	clean_ops.append(["line",PackedVector2Array([c+Vector2(-7,0),c+Vector2(7,0)]),WHITE,3.0])
	clean_ops.append(["line",PackedVector2Array([c+Vector2(0,-7),c+Vector2(0,7)]),WHITE,3.0])

func _stat(label: String,value: String,pos: Vector2) -> void:
	# Results must be easy to read: drawn without the worn-paint erosion.
	clean_ops.append(["text",font,pos,label,_scaled(16),MUTED])
	clean_ops.append(["text",bold,pos+Vector2(0,40),value,_scaled(34),WHITE])

func _icon_button(rect: Rect2,label: String) -> void:
	_panel(rect,Color(0.02,0.025,0.026,0.80),Color(0.32,0.34,0.34,0.65),0); _text_center(label,rect.get_center()+Vector2(0,4),10,WHITE)

## Same rect always picks the same stroke, different rects get different strokes.
func _pick(list: Array[Texture2D],rect: Rect2) -> Texture2D:
	return list[absi(int(rect.position.x*7.0+rect.position.y*13.0+rect.size.x))%list.size()]

func _button(rect: Rect2,label: String,primary: bool) -> void:
	# A swipe of paint a little larger than the hit area, so the ragged edges spill past it.
	# Buttons go on the clean layer: the paint texture already carries its own dry-brush wear,
	# and the extra worn-paint shader was eating holes in the lettering.
	var paint:=rect.grow_individual(14,8,14,8)
	clean_ops.append(["tinted",_pick(brush_button,rect),paint,PAINT_RED if primary else Color(0.13,0.14,0.14,0.96)])
	var size:=_scaled(30 if rect.size.y>=56 else 24)
	while bold.get_string_size(label,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x>rect.size.x-20 and size>14: size-=1
	var width:=bold.get_string_size(label,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x
	clean_ops.append(["text",bold,rect.get_center()+Vector2(-width/2+2,size*0.36+2),label,size,Color(0,0,0,0.5)])
	clean_ops.append(["text",bold,rect.get_center()+Vector2(-width/2,size*0.36),label,size,WHITE if primary else Color("e9e6dc")])

func _brush_underline(rect: Rect2,color:=PAINT_RED) -> void:
	draw_texture_rect(_pick(brush_line,rect),rect,false,color)

func _panel(rect: Rect2,bg: Color,border: Color,radius: int) -> void:
	# Smeared paint block; highlighted panels (red/white border) get a brush underline instead
	# of an outline.
	var tint:=Color(bg.r*0.9,bg.g*0.9,bg.b*0.9,minf(1.0,bg.a*1.05))
	draw_texture_rect(_pick(brush_panel,rect),rect.grow_individual(8,6,8,6),false,tint)
	if border!=LINE and border.a>0.05 and not border.is_equal_approx(Color(LINE,0.7)):
		var accent:=PAINT_RED if border.is_equal_approx(RED) else border
		draw_texture_rect(_pick(brush_line,rect),Rect2(rect.position.x-6,rect.end.y-12,rect.size.x+12,18),false,accent)

func _text(value: String,pos: Vector2,size: int,color: Color) -> void:
	size=maxi(size,12); _string(font,pos,value,size,color)

func _bold_text(value: String,pos: Vector2,size: int,color: Color) -> void:
	size=maxi(size,12); _string(bold,pos,value,size,color)

func _text_center(value: String,pos: Vector2,size: int,color: Color) -> void:
	# Big centred text is a headline: use the heavy poster face.
	size=maxi(size,12); var f: Font=bold if size>=30 else font
	var width:=f.get_string_size(value,HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(size)).x
	_string(f,pos-Vector2(width/2,0),value,size,color)

func _text_right(value: String,pos: Vector2,size: int,color: Color) -> void:
	size=maxi(size,12); var width:=font.get_string_size(value,HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(size)).x
	_string(font,pos-Vector2(width,0),value,size,color)

func _multiline(value: String,pos: Vector2,width: float,size: int,color: Color) -> void:
	size=_scaled(maxi(size,13)); draw_multiline_string(font,pos,value,HORIZONTAL_ALIGNMENT_LEFT,width,size,3,color)
