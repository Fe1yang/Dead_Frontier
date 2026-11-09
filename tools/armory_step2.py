import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# ---------------- main: the 3D preview world ----------------
p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "var armory_viewport" not in t:
    anchor = "var armory_return := \"shop\""
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + '''
var armory_viewport: SubViewport
var armory_stage: Node3D
var armory_model: Node3D
var armory_spin := 0.0
var armory_drag := false''', 1)

if "func _build_armory_view()" not in t:
    anchor2 = "func armory_weapon_id() -> String:"
    assert t.count(anchor2) == 1
    build = '''## A tiny 3D stage that renders the selected weapon for the armory panel.
func _build_armory_view() -> void:
	armory_viewport = SubViewport.new()
	armory_viewport.size = Vector2i(460, 380)
	armory_viewport.own_world_3d = true
	armory_viewport.transparent_bg = true
	armory_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	armory_viewport.msaa_3d = Viewport.MSAA_2X
	add_child(armory_viewport)

	armory_stage = Node3D.new()
	armory_viewport.add_child(armory_stage)

	var cam := Camera3D.new()
	cam.position = Vector3(0.0, 0.16, 1.05)
	cam.fov = 34.0
	armory_stage.add_child(cam)
	cam.look_at(Vector3(0, 0.02, 0))

	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-34, -38, 0)
	key.light_energy = 1.7
	armory_stage.add_child(key)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-14, 132, 0)
	fill.light_energy = 0.7
	armory_stage.add_child(fill)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.32, 0.34, 0.38)
	e.ambient_light_energy = 0.9
	env.environment = e
	armory_stage.add_child(env)


func _armory_show_weapon() -> void:
	if not is_instance_valid(armory_viewport):
		_build_armory_view()
	if is_instance_valid(armory_model):
		armory_model.queue_free()
		armory_model = null
	var id: String = armory_weapon_id()
	var path := "res://assets/models/weapons/%s.glb" % id.to_lower()
	if id == "RIFLE":
		path = "res://assets/models/rifle.glb"
	if not ResourceLoader.exists(path):
		return
	var model := (load(path) as PackedScene).instantiate() as Node3D
	armory_stage.add_child(model)
	armory_model = model
	# normalise: centre it and scale the longest side to a fixed length on screen
	var box := AABB()
	var first := true
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m == null or m.mesh == null:
			continue
		var a: AABB = m.transform * m.get_aabb()
		box = a if first else box.merge(a)
		first = false
	if first:
		return
	var span := maxf(box.size.x, maxf(box.size.y, box.size.z))
	var k := 0.62 / maxf(0.001, span)
	model.scale = Vector3.ONE * k
	var centre := box.get_center()
	model.position = -centre * k + Vector3(0, 0.02, 0)
	model.rotation.y = deg_to_rad(28.0)


'''
    t = t.replace(anchor2, build + anchor2, 1)

# refresh the model when the armory opens or the selection changes
t = t.replace(
    '''func open_armory() -> void:
	armory_return = state
	armory_index = 0
	state = "armory"''',
    '''func open_armory() -> void:
	armory_return = state
	armory_index = 0
	state = "armory"
	_armory_show_weapon()''',
    1,
)
t = t.replace(
    '''func armory_step(side: int) -> void:
	armory_index = posmod(armory_index + side, ARMORY_WEAPONS.size())''',
    '''func armory_step(side: int) -> void:
	armory_index = posmod(armory_index + side, ARMORY_WEAPONS.size())
	_armory_show_weapon()''',
    1,
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main: armory 3D stage")

# ---------------- hud: draw the viewport texture ----------------
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()

old = '''	var id: String = game.armory_weapon_id()
	var stats: Dictionary = game.ARMORY_STATS.get(id, {})'''
new = '''	var id: String = game.armory_weapon_id()
	var stats: Dictionary = game.ARMORY_STATS.get(id, {})
	# the 3D weapon, rendered by main into a SubViewport
	if is_instance_valid(game.armory_viewport):
		var tex: Texture2D = game.armory_viewport.get_texture()
		if tex != null:
			clean_ops.append(["texture", tex, Rect2(40, 158, 460, 380)])'''
assert h.count(old) == 1
h = h.replace(old, new, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("hud: viewport texture drawn")
