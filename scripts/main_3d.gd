extends Node3D

const PlayerScript=preload("res://scripts/player_3d.gd")
const ZombieScript=preload("res://scripts/zombie_3d.gd")
const BulletScript=preload("res://scripts/bullet_3d.gd")
const OrdnanceScript=preload("res://scripts/ordnance_projectile_3d.gd")
const GateScript=preload("res://scripts/gate_3d.gd")
const BarrelScript=preload("res://scripts/barrel_3d.gd")
const WeaponCrateScript=preload("res://scripts/weapon_crate_3d.gd")
const CRATE_WEAPONS:=["SMG","SHOTGUN","SNIPER","PISTOL","LAUNCHER","RIFLE"]
const CRATE_TIER:={"PISTOL":0.7,"RIFLE":0.9,"SMG":1.0,"SHOTGUN":1.1,"SNIPER":1.25,"LAUNCHER":1.5}
const RoadObstacleScript=preload("res://scripts/road_obstacle_3d.gd")
const PickupScript=preload("res://scripts/pickup_3d.gd")
const EffectScript=preload("res://scripts/effect_3d.gd")
const ExplosionScript=preload("res://scripts/explosion_3d.gd")
const SoundScript=preload("res://scripts/sound.gd")
const HudScript=preload("res://scripts/hud.gd")
const RevivalAdsScript=preload("res://scripts/revival_ads.gd")
const Localization=preload("res://scripts/localization.gd")
const ShopCatalog=preload("res://scripts/shop_catalog.gd")
const ShopText=preload("res://scripts/shop_text.gd")
const ShopSceneScript=preload("res://scripts/shop_scene_3d.gd")
const LobbySceneScript=preload("res://scripts/lobby_scene_3d.gd")
const DisasterDressing=preload("res://scripts/disaster_dressing_3d.gd") # Kimi: blood, drag marks, rubble, idle watchers on every block
const BloodPoolScript=preload("res://scripts/blood_pool_3d.gd")
const MAX_BLOOD_POOLS:=60
const BossChaserScript=preload("res://scripts/boss_chaser_3d.gd")
# Sky domes (Poly Haven, CC0, 2K HDR): a broken-cloud sky for clear runs, a heavy overcast for rain and fog.
# Procedural cloud sky from the user's sky pack (shaders/sky_clouds.gdshader); one material,
# recoloured per weather.
const SKY_SHADER=preload("res://shaders/sky_clouds.gdshader")
# Binbun-style stylised skies: saturated gradient, bright puffy cloud layers with parallax.
# "mix" is the pack's day/sunset blend (1 = full day, ~0.1 = golden hour).
const SKY_PRESETS:={
	"clear":{"sky":Color("0838c4"),"horizon":Color("5aa8e6"),"cloud":Color("ffffff"),"density":1.0,"depth":3.0,"wind":Vector2(0.35,0.18),"mix":1.0,"energy":1.0,"tiling":0.75},
	"sunset":{"sky":Color("2a3f8f"),"horizon":Color("ff8a3d"),"sunset_sky":Color("2c2f7a"),"sunset_horizon":Color("ff6a2a"),"cloud":Color("ffb57a"),"density":1.0,"depth":3.0,"wind":Vector2(0.3,0.15),"mix":0.12,"energy":1.0,"tiling":0.75},
	"rain":{"sky":Color("3d4a58"),"horizon":Color("7f8d99"),"cloud":Color("6e7984"),"density":1.6,"depth":3.5,"wind":Vector2(0.7,0.35),"mix":1.0,"energy":1.05,"tiling":0.9},
	"storm":{"sky":Color("141b26"),"horizon":Color("394556"),"cloud":Color("2c3440"),"density":2.3,"depth":4.0,"wind":Vector2(1.3,0.6),"mix":1.0,"energy":0.95,"tiling":1.0},
	"fog":{"sky":Color("8f9ea8"),"horizon":Color("d3dade"),"cloud":Color("e1e6e9"),"density":1.3,"depth":2.0,"wind":Vector2(0.2,0.1),"mix":1.0,"energy":1.1,"tiling":0.8}}
const ToonStyle=preload("res://scripts/toon_style.gd")
const EnvironmentMaterials=preload("res://scripts/environment_materials.gd")
const ROAD_SEGMENT:=16.0
const ROAD_COUNT:=24
const ROAD_LOOP:=ROAD_SEGMENT*ROAD_COUNT
const ROAD_BEHIND:=56.0 # city blocks kept behind the player for intro/chase shots

var state:="menu"
var intro_time:=0.0
var intro_horde_offsets: Array[Vector3]=[]
var chaser: Node3D # the giant Chaser that leads the opening pursuit
const CHASER_OFFSET:=Vector3(0,0,8.2)
var character_choice:=0
var language_code:="zh_CN"
var player: Node3D
var sound: Node
var hud: Control
var revival_ads: Node
var camera: Camera3D
var shop_truck: Node3D
var lobby: Node3D
var settings_return_state:="menu"
var text_size:=1 # 0 small, 1 medium (default), 2 large: for players who need bigger text
var lobby_toast:=0.0
# Weather: each run randomly rolls clear, rain or fog (no snow on this city map).
const RainShader=preload("res://shaders/rain_and_snow.gdshader")
var weather:="clear"
var run_weather:="clear"
var runs_this_launch:=0 # the first run after launching is always clear weather # remembered while the shop overrides the lighting
var world_env: Environment
var sky_material: ShaderMaterial
var sun_light: DirectionalLight3D
var rain_overlay: ColorRect
var rain_material: ShaderMaterial
var lightning_flash: ColorRect
var lightning_timer:=6.0
var lightning_t:=-1.0      # time since the current strike started (<0: none)
var thunder_delay:=-1.0
var weather_base:={}
var force_sunset:=false # preview/testing only       # exposure / sun / ambient of the current weather, restored after a flash
var shop_return_state:="menu"
var shop_items: Array=[]
var bank_coins:=0
var run_coins:=0
var last_reward:=0
var survival_bonus:=0
var revive_used:=false
var revive_pending:=false
var revive_invulnerable:=0.0
var jockey_introduced:=false
var banshee_introduced:=false
var banshee_warning:=0.0
var meta_upgrades:=ShopCatalog.default_levels()
var shop_index:=0
var zombies: Array=[]
var bullets: Array=[]
var ordnance: Array=[]
var gates: Array=[]
var barrels: Array=[]
var crates: Array=[]
var blood_pools: Array=[]
var watchers: Array=[]   # roadside zombies (scenery that can be shot), owned by the road blocks
var kill_counts:={}      # kind -> kills this run
var kill_coins:={}       # kind -> coins earned from those kills
var crate_timer:=3.0
var obstacles: Array=[]
var pickups: Array=[]
var effects: Array=[]
var roads: Array=[]
var scenery: Array=[]
var rng:=RandomNumberGenerator.new()
var run_time:=0.0
var distance:=0.0
var kills:=0
var wave:=1
var best_distance:=0
var spawn_timer:=0.0
var gate_timer:=7.0
var barrel_timer:=5.0
var obstacle_timer:=5.5
var pickup_timer:=3.0
var shot_timer:=0.0
var growl_timer:=4.0
var damage_flash:=0.0
var shake:=0.0
var wave_banner:=0.0
var hint_time:=7.0
var new_gate_index:=0
var elapsed:=0.0
var auto_reload:=true
var touch_controls:=false
var mouse_position:=Vector2(270,390)
var aim_direction:=Vector3.FORWARD
var aim_target: Node3D
var aim_point:=Vector3.ZERO
var left_touch_id:=-1
var right_touch_id:=-1
var left_stick:=Vector2.ZERO
var right_stick:=Vector2.ZERO
# Touch layout (mobile only; hidden on desktop): sticks bottom corners, action buttons stacked on the right.
const STICK_LEFT:=Vector2(110,842)
const STICK_RIGHT:=Vector2(430,842)
const BTN_RELOAD:=Vector2(490,640)
const BTN_FRAG:=Vector2(490,724)
const BTN_FLASH:=Vector2(414,724)
const BTN_FIRE_MODE:=Vector2(414,640)
const BTN_SWAP:=Vector2(490,556)
const BTN_RADIUS:=36.0
const PAUSE_BUTTON:=Rect2(476,8,58,58)
var left_origin:=STICK_LEFT
var right_origin:=STICK_RIGHT
var left_knob:=Vector2(92,820)
var right_knob:=Vector2(448,820)

func _ready() -> void:
	rng.randomize(); _load_save(); _setup_world(); _build_road()
	touch_controls=OS.has_feature("mobile")
	sound=SoundScript.new(); sound.muted=_read_muted(); add_child(sound)
	if "--smoke-test" in OS.get_cmdline_user_args() or "--soak-test" in OS.get_cmdline_user_args(): sound.muted=true
	revival_ads=RevivalAdsScript.new(); add_child(revival_ads)
	revival_ads.revive_rewarded.connect(_revive_after_reward)
	revival_ads.revive_cancelled.connect(_revive_ad_cancelled)
	player=PlayerScript.new(); player.character=character_choice; add_child(player); player.reset()
	shop_truck=ShopSceneScript.new()
	add_child(shop_truck); shop_truck.visible=false; shop_items=ShopCatalog.items()
	lobby=LobbySceneScript.new(); add_child(lobby); lobby.visible=false
	_setup_weather_overlay()
	var layer:=CanvasLayer.new(); add_child(layer)
	hud=HudScript.new(); hud.game=self; hud.mouse_filter=Control.MOUSE_FILTER_IGNORE; layer.add_child(hud)
	hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_menu_zombies(); _set_menu_scene(); _update_mouse_aim()
	if "--capture" in OS.get_cmdline_user_args(): call_deferred("_capture")
	elif "--smoke-test" in OS.get_cmdline_user_args(): call_deferred("_smoke_test")
	elif "--soak-test" in OS.get_cmdline_user_args(): call_deferred("_soak_test")

func localize(key: String) -> String:
	return Localization.text(language_code,key)

func _setup_world() -> void:
	var we:=WorldEnvironment.new(); var env:=Environment.new()
	var sky:=Sky.new(); var sky_mat:=ShaderMaterial.new(); sky_mat.shader=SKY_SHADER
	sky_mat.set_shader_parameter("cloud_tex_01",load("res://assets/sky/clouds/clouds_01.png"))
	sky_mat.set_shader_parameter("cloud_tex_02",load("res://assets/sky/clouds/clouds_04.png"))
	sky_mat.set_shader_parameter("night_noise_01",load("res://assets/sky/clouds/clouds_07.png"))
	sky_mat.set_shader_parameter("night_noise_02",load("res://assets/sky/clouds/clouds_03.png"))
	sky_mat.set_shader_parameter("cloud_tiling",Vector2(1.4,1.4))
	sky_mat.set_shader_parameter("sun_scale",0.035)
	# Fixed daytime palette (the weather presets set the colours); the sky doesn't follow the sun angle.
	sky_mat.set_shader_parameter("use_directional_light",false); sky_mat.set_shader_parameter("day_night_mix",1.0)
	sky_mat.set_shader_parameter("cloud_shape_exponent",1.35)
	sky_mat.set_shader_parameter("horizon_exponent",5.0) # thinner pale horizon band, deeper blue above
	sky_material=sky_mat; sky.sky_material=sky_mat; env.background_mode=Environment.BG_SKY; env.sky=sky; env.sky_rotation=Vector3(0,deg_to_rad(25),0)
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR; env.ambient_light_color=Color("b8c7d1"); env.ambient_light_energy=0.48
	env.reflected_light_source=1
	env.tonemap_mode=Environment.TONE_MAPPER_ACES; env.tonemap_exposure=0.88
	env.fog_enabled=true; env.fog_light_color=Color("b7c9d0"); env.fog_density=0.0032; env.fog_sky_affect=0.08
	we.environment=env; add_child(we); world_env=env
	var sun:=DirectionalLight3D.new(); sun.rotation_degrees=Vector3(-52,-32,0)
	sun.light_color=Color("fff0d9"); sun.light_energy=0.64; sun.shadow_enabled=true; sun.directional_shadow_max_distance=135
	sun.directional_shadow_mode=DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	add_child(sun); sun_light=sun
	var rim:=DirectionalLight3D.new(); rim.rotation_degrees=Vector3(-28,145,0); rim.light_color=Color("c2d9e7"); rim.light_energy=0.12
	rim.sky_mode=DirectionalLight3D.SKY_MODE_LIGHT_ONLY # the sky shader's sun follows the main sun only
	add_child(rim)
	camera=Camera3D.new(); camera.position=Vector3(0,6.4,13.5); camera.fov=52; camera.near=0.1; camera.far=390; add_child(camera)
	camera.current=true; camera.look_at(Vector3(0,1.0,-8))
	var ground:=MeshInstance3D.new(); var plane:=PlaneMesh.new(); plane.size=Vector2(700,700); ground.mesh=plane
	var m:=StandardMaterial3D.new(); m.albedo_color=Color("555c5a"); m.roughness=0.98; ground.material_override=m
	ground.position.y=-0.27; add_child(ground)

func _mesh_node(mesh: Mesh,color: Color,pos: Vector3) -> MeshInstance3D:
	var n:=MeshInstance3D.new(); n.mesh=mesh; n.position=pos
	var m:=StandardMaterial3D.new(); m.albedo_color=color; m.roughness=0.9; n.material_override=m
	add_child(n); return n

func _triangle(st: SurfaceTool,a: Vector3,b: Vector3,c: Vector3) -> void:
	var normal: Vector3=(b-a).cross(c-a).normalized()
	for point in [a,b,c]: st.set_normal(normal); st.add_vertex(point)

func _grass_clump() -> Node3D:
	var root:=Node3D.new(); var st:=SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(7):
		var base:=Vector3(rng.randf_range(-0.22,0.22),0,rng.randf_range(-0.22,0.22)); var h:=rng.randf_range(0.18,0.38); var w:=rng.randf_range(0.018,0.035)
		var angle:=rng.randf_range(0,TAU); var right:=Vector3(cos(angle),0,sin(angle))*w; var tip:=base+Vector3(rng.randf_range(-0.10,0.10),h,rng.randf_range(-0.10,0.10))
		_triangle(st,base-right,base+right,tip); _triangle(st,base+Vector3(-right.z,0,right.x),base-Vector3(-right.z,0,right.x),tip)
	var blades:=MeshInstance3D.new(); blades.mesh=st.commit()
	var m:=StandardMaterial3D.new(); m.albedo_color=Color("687348"); m.roughness=1.0; m.cull_mode=BaseMaterial3D.CULL_DISABLED; blades.material_override=m; root.add_child(blades)
	return root

func _rock() -> Node3D:
	var root:=Node3D.new(); var st:=SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var top:=Vector3(0.03,rng.randf_range(0.13,0.19),-0.02); var bottom:=Vector3(0,-0.025,0)
	var ring: Array[Vector3]=[Vector3(0.20,0.035,0),Vector3(0.02,0.02,0.14),Vector3(-0.16,0.04,0.01),Vector3(-0.01,0.025,-0.12)]
	for i in range(4):
		_triangle(st,top,ring[i],ring[(i+1)%4]); _triangle(st,bottom,ring[(i+1)%4],ring[i])
	var rock:=MeshInstance3D.new(); rock.mesh=st.commit(); rock.rotation.y=rng.randf_range(0,TAU); rock.position.y=0.04
	var m:=StandardMaterial3D.new(); m.albedo_color=Color("777b72"); m.roughness=1.0; rock.material_override=m; root.add_child(rock)
	return root

func _build_road() -> void:
	# A 384 m city loop with twelve unique blocks; all surfaces retain full PBR detail.
	for i in range(ROAD_COUNT):
		var asset: String="city_hd_%02d"%(i%12)
		var path: String="res://assets/models/environment/"+asset+".glb"
		if not ResourceLoader.exists(path): path="res://assets/models/environment/city_hd_00.glb"
		var road:=load(path).instantiate() as Node3D
		road.position=Vector3(0,0,ROAD_BEHIND-i*ROAD_SEGMENT); add_child(road)
		EnvironmentMaterials.apply(road); DisasterDressing.apply(road,i,ZombieScript); roads.append(road)
		if road.has_meta("watcher"): watchers.append(road.get_meta("watcher"))

func _process(delta: float) -> void:
	elapsed+=delta
	sound.music_state(state)
	damage_flash=maxf(0,damage_flash-delta); shake=maxf(0,shake-delta*3.0)
	banshee_warning=maxf(0,banshee_warning-delta)
	var world_speed:=3.5 if state in ["playing","intro"] else (0.25 if state=="menu" else 0.0)
	for road in roads:
		road.position.z+=world_speed*delta
		if road.position.z>ROAD_BEHIND+ROAD_SEGMENT:
			road.position.z-=ROAD_LOOP
			_refresh_watcher(road)
	_tick_lightning(delta)
	if state=="intro":
		_tick_intro(delta)
		return
	if state=="shop":
		camera.fov=shop_truck.camera_fov(); camera.position=shop_truck.camera_position(); camera.look_at(shop_truck.camera_target()); return
	lobby.visible=state=="character_select"
	lobby_toast=maxf(0.0,lobby_toast-delta)
	if state=="character_select":
		lobby.show_character(character_choice)
		camera.fov=lobby.CAMERA_FOV; camera.h_offset=0; camera.v_offset=0
		camera.position=lobby.camera_position(); camera.look_at(lobby.camera_target()); return
	if state in ["menu","language","settings"]:
		camera.fov=52; _set_menu_scene(); return
	camera.position.x=lerpf(camera.position.x,player.position.x*0.12,delta*3.0)
	camera.h_offset=rng.randf_range(-0.12,0.12)*shake; camera.v_offset=rng.randf_range(-0.1,0.1)*shake
	camera.look_at(Vector3(player.position.x*0.08,1.0,-8))
	if state!="playing": return
	run_time+=delta; distance+=delta*10.5; hint_time=maxf(0,hint_time-delta); wave_banner=maxf(0,wave_banner-delta)
	revive_invulnerable=maxf(0.0,revive_invulnerable-delta)
	var next_wave:=int(run_time/22.0)+1
	if next_wave!=wave: wave=next_wave; wave_banner=2.0; sound.play("gate")
	growl_timer-=delta
	if growl_timer<=0:
		if not zombies.is_empty(): sound.play("zombie")
		growl_timer=rng.randf_range(5.5,10.0)
	var axis:=0.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT): axis-=1
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT): axis+=1
	if touch_controls: axis=clampf(axis+left_stick.x,-1,1)
	if axis!=0: player.target_x=clampf(player.target_x+axis*5.0*delta,-3.15,3.15)
	if right_stick.length()>0.16:
		aim_direction=Vector3(right_stick.x,0,right_stick.y).normalized()
	elif not touch_controls:
		_update_mouse_aim()
	if touch_controls: _update_touch_aim()
	player.set_aim(aim_direction); player.tick(delta); shot_timer-=delta
	# Firing is automatic on every platform; aiming and reloading remain player choices.
	# Out of ammo for the current gun: fall back to the pistol, which never runs dry.
	if not player.infinite_ammo() and player.ammo<=0 and player.reserve_ammo<=0 and not player.reloading:
		swap_weapon(true)
	if shot_timer<=0:
		if player.can_fire():
			_fire(); shot_timer=player.fire_interval
		elif player.ammo<=0 and auto_reload:
			request_reload()
	spawn_timer-=delta
	if spawn_timer<=0:
		_spawn_zombie(); spawn_timer=maxf(0.30,1.55-run_time*0.008)*rng.randf_range(0.82,1.16)
	# Road events ramp up over the run: an almost empty street at the start, busier later,
	# and never two things on the same stretch of road (see _road_clear).
	var ramp: float=_pace()
	gate_timer-=delta
	if gate_timer<=0:
		if _road_clear(-40.0): _spawn_gate(); gate_timer=lerpf(11.0,7.5,ramp)*rng.randf_range(0.9,1.15)
		else: gate_timer=1.2
	barrel_timer-=delta
	if barrel_timer<=0:
		if _road_clear(-45.0): _spawn_barrel(); barrel_timer=lerpf(26.0,14.0,ramp)*rng.randf_range(0.85,1.2)
		else: barrel_timer=1.5
	crate_timer-=delta
	if crate_timer<=0:
		if _road_clear(-46.0): _spawn_crates(); crate_timer=lerpf(30.0,17.0,ramp)*rng.randf_range(0.85,1.2)
		else: crate_timer=1.5
	obstacle_timer-=delta
	if obstacle_timer<=0:
		if _road_clear(-48.0): _spawn_obstacle_pattern(); obstacle_timer=lerpf(20.0,11.0,ramp)*rng.randf_range(0.85,1.2)
		else: obstacle_timer=1.5
	pickup_timer-=delta
	if pickup_timer<=0:
		var roll:=rng.randf()
		var pickup_kind := "ammo"
		if roll<0.08: pickup_kind="helmet"
		elif roll<0.16: pickup_kind="armor"
		elif roll<0.23: pickup_kind="grenade"
		elif roll<0.29: pickup_kind="flashbang"
		elif roll<0.41: pickup_kind="fire_round"
		elif roll<0.64: pickup_kind="medkit"
		_spawn_pickup(pickup_kind); pickup_timer=lerpf(15.0,9.0,_pace())*rng.randf_range(0.85,1.2)
	_tick_bullets(delta); _tick_ordnance(delta); _tick_barrels(delta); _tick_crates(delta); _tick_blood(delta); _tick_watchers(delta); _tick_zombies(delta); _resolve_barrel_collision(); _tick_obstacles(delta); _tick_gates(delta); _tick_pickups(delta); _tick_effects(delta)
	if player.health<=0: _end_run()

func _menu_zombies() -> void:
	for i in range(3):
		var z:=ZombieScript.new(); add_child(z); z.configure("walker" if i!=1 else "brute",1.0)
		z.position=Vector3(-2.2+i*2.2,0,-16-i*6); zombies.append(z)

func _set_menu_scene() -> void:
	player.position=Vector3(1.05,0,3.0); player.target_x=1.05; player.model.rotation.y=0
	camera.position=Vector3(3.0,2.65,8.4); camera.h_offset=0; camera.v_offset=0; camera.look_at(Vector3(-0.35,1.05,3.0))

func start_run() -> void:
	_clear_world(); state="playing"; run_time=0; distance=0; kills=0; wave=1; run_coins=0; last_reward=0; survival_bonus=0
	kill_counts.clear(); kill_coins.clear()
	for road in roads: _refresh_watcher(road)
	revive_used=false; revive_pending=false; revive_invulnerable=0.0; jockey_introduced=false; banshee_introduced=false; banshee_warning=0.0
	spawn_timer=1.6; gate_timer=9.0; barrel_timer=32.0; crate_timer=20.0; obstacle_timer=24.0; pickup_timer=12.0; shot_timer=0; growl_timer=3.5; hint_time=7; damage_flash=0; new_gate_index=0
	aim_direction=Vector3.FORWARD; aim_target=null; left_stick=Vector2.ZERO; right_stick=Vector2.ZERO; _release_touches()
	shop_truck.visible=false; player.visible=true; camera.fov=52; camera.position=Vector3(0,6.4,13.5)
	runs_this_launch+=1
	set_weather("clear" if runs_this_launch==1 else _roll_weather())
	player.reset(); player.apply_meta(meta_upgrades); player.set_aim(aim_direction)
	var automated:="--smoke-test" in OS.get_cmdline_user_args() or "--soak-test" in OS.get_cmdline_user_args() or "--capture" in OS.get_cmdline_user_args()
	if automated:
		_spawn_zombie(-18); _spawn_zombie(-32)
	else:
		_begin_intro()

func _begin_intro() -> void:
	_clear_world(); intro_horde_offsets.clear(); intro_time=0.0; state="intro"
	player.position=Vector3(0,0,4.5); player.target_x=0.0; player.visible=true
	player.set_aim(Vector3.FORWARD); player._play_run()
	# The Chaser leads; a pack of smaller zombies runs around and ahead of it.
	if is_instance_valid(chaser): chaser.queue_free()
	chaser=null
	# The chaser model is supplied separately; if it isn't in the project the intro still plays
	# with the horde instead of crashing.
	if ResourceLoader.exists(BossChaserScript.MODEL_PATH):
		chaser=BossChaserScript.new(); add_child(chaser); chaser.position=player.position+CHASER_OFFSET
	var horde:= [
		["jockey",Vector3(1.3,0,5.0)],
		["runner",Vector3(-2.2,0,5.6)],
		["runner",Vector3(2.4,0,6.3)],
		["walker",Vector3(-2.7,0,8.4)],
		["walker",Vector3(2.8,0,9.2)],
		["runner",Vector3(-1.9,0,10.9)],
		["walker",Vector3(1.9,0,11.6)],
		["walker",Vector3(-0.6,0,12.8)],
		["walker",Vector3(0.9,0,13.4)]
	]
	for entry in horde:
		var z:=ZombieScript.new(); add_child(z); z.configure(str(entry[0]),1.0)
		z.model.rotation.y+=PI
		var offset: Vector3=entry[1]
		z.position=player.position+offset
		intro_horde_offsets.append(offset); zombies.append(z)
	camera.fov=50; camera.h_offset=0; camera.v_offset=0
	camera.position=Vector3(2.2,1.05,6.6); camera.look_at(player.position+CHASER_OFFSET+Vector3(0,2.3,0))
	sound.play("zombie")

func _tick_intro(delta: float) -> void:
	intro_time+=delta
	player.set_aim(Vector3.FORWARD); player.tick(delta)
	for i in range(zombies.size()):
		var z=zombies[i]
		if not is_instance_valid(z): continue
		var offset: Vector3=intro_horde_offsets[i]
		z.position=Vector3(offset.x+sin(intro_time*3.0+i)*0.07,0,player.position.z+offset.z-intro_time*0.16)
	var chaser_pos:=player.position+CHASER_OFFSET-Vector3(0,0,intro_time*0.22)
	if is_instance_valid(chaser):
		chaser.position=chaser_pos
		# each heavy footfall shakes the low camera
		shake=maxf(shake,0.18*maxf(0.0,sin(intro_time*TAU*1.15)))
	# Low angle beside the survivor looking back up at the Chaser, then swing to the run camera.
	var monster_camera:=Vector3(2.2+sin(intro_time*1.8)*0.08,1.05+intro_time*0.06,6.6-intro_time*0.12)
	var chase_camera:=Vector3(0,6.4,13.5)
	var turn:=smoothstep(1.55,4.0,intro_time)
	camera.position=monster_camera.lerp(chase_camera,turn)
	camera.v_offset=randf_range(-0.04,0.04)*shake*(1.0-turn)
	camera.fov=lerpf(50.0,52.0,turn)
	var look_target:=(chaser_pos+Vector3(0,2.3,0)).lerp(Vector3(0,1.0,-8),turn)
	camera.look_at(look_target)
	if intro_time>=4.9: _finish_intro()

func _finish_intro() -> void:
	if state!="intro": return
	_clear_world(); intro_horde_offsets.clear(); state="playing"; camera.v_offset=0
	player.position=Vector3(0,0,4.5); player.target_x=0.0; player.set_aim(Vector3.FORWARD)
	camera.position=Vector3(0,6.4,13.5); camera.fov=52; camera.look_at(Vector3(0,1.0,-8))
	spawn_timer=1.6; shot_timer=0.2; hint_time=7.0
	_spawn_zombie(-18); _spawn_zombie(-32)

func _setup_weather_overlay() -> void:
	var weather_layer:=CanvasLayer.new(); add_child(weather_layer)
	rain_overlay=ColorRect.new(); rain_overlay.color=Color(0,0,0,0)
	rain_overlay.mouse_filter=Control.MOUSE_FILTER_IGNORE
	rain_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var m:=ShaderMaterial.new(); m.shader=RainShader
	m.set_shader_parameter("rain_trails",true)
	m.set_shader_parameter("rain_amount",140.0)
	m.set_shader_parameter("near_rain_length",0.11); m.set_shader_parameter("far_rain_length",0.05)
	m.set_shader_parameter("near_rain_width",0.55); m.set_shader_parameter("far_rain_width",0.30)
	m.set_shader_parameter("near_rain_transparency",0.55); m.set_shader_parameter("far_rain_transparency",0.22)
	m.set_shader_parameter("rain_color",Color(0.78,0.84,0.90,1.0))
	m.set_shader_parameter("base_rain_speed",0.9); m.set_shader_parameter("additional_rain_speed",0.6)
	m.set_shader_parameter("slant",0.12)
	rain_overlay.material=m; rain_overlay.visible=false; weather_layer.add_child(rain_overlay)
	rain_material=m
	# Lightning: a brief cold-white wash over the whole screen on top of the exposure spike.
	lightning_flash=ColorRect.new(); lightning_flash.color=Color(0.86,0.92,1.0,0.0)
	lightning_flash.mouse_filter=Control.MOUSE_FILTER_IGNORE
	lightning_flash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); weather_layer.add_child(lightning_flash)

func _roll_weather() -> String:
	var roll:=rng.randf()
	if roll<0.35: return "clear"
	if roll<0.60: return "rain"
	if roll<0.75: return "storm"
	return "fog"

func set_weather(kind: String) -> void:
	weather=kind
	if world_env==null: return
	# Clear-day baseline (matches the original look).
	var exposure:=0.88; var ambient:=Color("b8c7d1"); var ambient_energy:=0.48
	var fog_color:=Color("b7c9d0"); var fog_density:=0.0032; var fog_sky:=0.08
	var sun_energy:=0.64; var sky_energy:=1.0; var sun_color:=Color("fff0d9")
	var depth_fog:=false; var fog_begin:=0.0; var fog_end:=100.0
	match kind:
		"rain":
			# Overcast storm: everything pressed darker and colder.
			exposure=0.76; ambient=Color("95a2ac"); ambient_energy=0.54
			fog_color=Color("74808a"); fog_density=0.012; fog_sky=0.22
			sun_energy=0.34; sky_energy=0.62; sun_color=Color("d3dce3")
		"storm":
			# Thunderstorm: much darker, cold blue-grey, heavy slanted rain; lightning lights it up.
			exposure=0.62; ambient=Color("7c8a99"); ambient_energy=0.50
			fog_color=Color("4a5663"); fog_density=0.018; fog_sky=0.30
			sun_energy=0.18; sky_energy=0.42; sun_color=Color("b8c6d6")
		"fog":
			# Thick fog that thickens with distance, like real fog: the survivor and the road
			# right around them stay crisp, the street ahead fades into white.
			exposure=0.86; ambient=Color("b9c2c7"); ambient_energy=0.62
			fog_color=Color("b4bdc2"); fog_density=0.96; fog_sky=0.7
			sun_energy=0.30; sky_energy=0.70; sun_color=Color("e6ebee")
			depth_fog=true; fog_begin=12.5; fog_end=46.0
	world_env.tonemap_exposure=exposure
	world_env.ambient_light_color=ambient; world_env.ambient_light_energy=ambient_energy
	# Mode first: switching fog mode resets the density in this Godot version.
	world_env.fog_mode=Environment.FOG_MODE_DEPTH if depth_fog else Environment.FOG_MODE_EXPONENTIAL
	world_env.fog_depth_begin=fog_begin; world_env.fog_depth_end=fog_end; world_env.fog_depth_curve=1.35
	world_env.fog_light_color=fog_color; world_env.fog_density=fog_density; world_env.fog_sky_affect=fog_sky
	weather_base={"exposure":exposure,"sun":sun_energy,"sun_color":sun_color,"ambient":ambient_energy}
	lightning_t=-1.0; thunder_delay=-1.0; lightning_timer=rng.randf_range(3.0,6.0)
	if lightning_flash: lightning_flash.color.a=0.0
	if rain_material:
		var storm: bool=kind=="storm"
		rain_material.set_shader_parameter("rain_amount",260.0 if storm else 140.0)
		rain_material.set_shader_parameter("slant",0.32 if storm else 0.12)
		rain_material.set_shader_parameter("base_rain_speed",1.0 if storm else 0.9)
		rain_material.set_shader_parameter("additional_rain_speed",0.9 if storm else 0.6)
		rain_material.set_shader_parameter("near_rain_transparency",0.75 if storm else 0.55)
		rain_material.set_shader_parameter("near_rain_length",0.16 if storm else 0.11)
	if sky_material:
		# Clear weather is either a bright midday or a golden-hour sky.
		var preset_name: String=kind
		if kind=="clear" and runs_this_launch>1 and (rng.randf()<0.4 or force_sunset): preset_name="sunset"
		var preset: Dictionary=SKY_PRESETS.get(preset_name,SKY_PRESETS["clear"])
		sky_material.set_shader_parameter("sky_day",preset.sky); sky_material.set_shader_parameter("horizon_day",preset.horizon)
		sky_material.set_shader_parameter("sky_sunset",preset.get("sunset_sky",preset.sky)); sky_material.set_shader_parameter("horizon_sunset",preset.get("sunset_horizon",preset.horizon))
		sky_material.set_shader_parameter("day_night_mix",preset.mix)
		sky_material.set_shader_parameter("cloud_color",preset.cloud); sky_material.set_shader_parameter("cloud_density",preset.density)
		sky_material.set_shader_parameter("cloud_depth",preset.depth); sky_material.set_shader_parameter("wind_speed",preset.wind)
		sky_material.set_shader_parameter("cloud_tiling",Vector2(preset.tiling,preset.tiling)); sky_material.set_shader_parameter("flash",0.0)
		world_env.background_energy_multiplier=preset.energy
		if preset_name=="sunset":
			sun_color=Color("ffb06a"); sun_energy=0.75
			world_env.ambient_light_color=Color("d8b8a8"); world_env.fog_light_color=Color("e0b49a")
	if sun_light: sun_light.light_energy=sun_energy; sun_light.light_color=sun_color
	if rain_overlay: rain_overlay.visible=kind in ["rain","storm"] and state!="shop"

## Lightning for the storm weather: a double flicker (strike, dip, re-strike) that spikes the
## exposure and sunlight and washes the screen white, then thunder rolls in a moment later.
func _tick_lightning(delta: float) -> void:
	if weather!="storm" or state!="playing" or weather_base.is_empty():
		return
	if lightning_t<0.0:
		lightning_timer-=delta
		if lightning_timer<=0.0:
			lightning_t=0.0; thunder_delay=rng.randf_range(0.35,1.3); lightning_timer=rng.randf_range(5.0,11.0)
	var flash:=0.0
	if lightning_t>=0.0:
		lightning_t+=delta
		var t:=lightning_t
		flash=maxf(exp(-pow((t-0.04)/0.035,2.0)),0.75*exp(-pow((t-0.20)/0.05,2.0)))
		if t>0.6: lightning_t=-1.0; flash=0.0
	if thunder_delay>=0.0:
		thunder_delay-=delta
		if thunder_delay<0.0: sound.play("thunder"); shake=maxf(shake,0.25)
	world_env.tonemap_exposure=float(weather_base.exposure)+flash*2.4
	if sun_light:
		sun_light.light_energy=float(weather_base.sun)+flash*2.4
		sun_light.light_color=(weather_base.sun_color as Color).lerp(Color("e8f0ff"),flash)
	world_env.ambient_light_energy=float(weather_base.ambient)+flash*1.2
	if lightning_flash: lightning_flash.color.a=flash*0.42
	if sky_material: sky_material.set_shader_parameter("flash",flash)

func open_shop() -> void:
	shop_return_state=state
	if state!="paused": _clear_world()
	state="shop"; _release_touches(); player.visible=false; shop_truck.visible=true
	run_weather=weather; set_weather("clear")
	shop_truck.position=Vector3(0,0,0); camera.h_offset=0; camera.v_offset=0
	shop_index=clampi(shop_index,0,maxi(0,shop_items.size()-1))
	shop_truck.reset_view(String(shop_items[shop_index].id) if not shop_items.is_empty() else "")
	camera.fov=shop_truck.camera_fov(); camera.position=shop_truck.camera_position(); camera.look_at(shop_truck.camera_target())

func close_shop() -> void:
	shop_truck.visible=false; player.visible=true; camera.fov=52
	if shop_return_state=="paused":
		state="paused"; set_weather(run_weather); camera.position=Vector3(player.position.x*0.12,6.4,13.5); camera.look_at(Vector3(player.position.x*0.08,1.0,-8)); return
	_clear_world(); set_weather("clear")
	# Back to the character lobby (from the lobby or after a run); the title poster is only the first screen.
	enter_lobby()

func open_language() -> void:
	state="language"

## Case opening (CS:GO style). Only the entry point exists so far; the opening scene is built
## separately and should hook in here.
var lootbox_return_state:="menu"
func open_lootbox() -> void:
	lootbox_return_state=state
	state="lootbox"; _release_touches()

func close_lootbox() -> void:
	state=lootbox_return_state

const LOBBY_SLOTS:=4
const LOBBY_TOP:=150.0
const LOBBY_STEP:=124.0
const LOBBY_CARD:=Vector2(96,112)
const LOBBY_LEFT_X:=14.0
const LOBBY_RIGHT_X:=430.0

func select_character(index: int) -> void:
	character_choice=posmod(index,lobby.CHARACTERS.size()); player.set_character(character_choice); lobby.show_character(character_choice); sound.play("gate"); _save()

## Every finished run lands back in the character lobby.
func go_to_lobby() -> void:
	_clear_world(); set_weather("clear"); player.visible=true
	enter_lobby()

func enter_lobby() -> void:
	state="character_select"; lobby.visible=true; lobby.show_character(character_choice)

## Swap button / E / Tab: switch between the crate gun and the pistol (unlimited ammo).
func swap_weapon(out_of_ammo:=false) -> bool:
	if state!="playing" or not player.swap_weapon(): return false
	sound.play("reload")
	var zh:=language_code.begins_with("zh")
	var names:={"PISTOL":"手枪","SMG":"冲锋枪","SHOTGUN":"霰弹枪","SNIPER":"狙击枪","RIFLE":"突击步枪","LAUNCHER":"榴弹发射器"}
	var label: String=("弹药耗尽 → 手枪" if zh else "OUT OF AMMO → PISTOL") if out_of_ammo else (String(names.get(player.weapon,player.weapon)) if zh else player.weapon)
	_popup(player.position+Vector3(0,2.5,0),label,Color("ffd275"))
	return true

func select_shop_item(index: int) -> void:
	if shop_items.is_empty(): return
	shop_index=posmod(index,shop_items.size()); shop_truck.focus(shop_items[shop_index].id); sound.play("hit")

func item_cost(item: Dictionary) -> int:
	return int(item.cost)+int(meta_upgrades.get(item.id,0))*20

func buy_item(id: String) -> bool:
	for item in shop_items:
		if item.id!=id: continue
		var level: int=meta_upgrades.get(id,0); var cost: int=item_cost(item)
		if level>=int(item.max_level) or bank_coins<cost: return false
		bank_coins-=cost; meta_upgrades[id]=level+1; sound.play("pickup"); _save(); return true
	return false

func _clear_world() -> void:
	if is_instance_valid(chaser): chaser.queue_free(); chaser=null
	for collection in [zombies,bullets,ordnance,gates,barrels,crates,blood_pools,obstacles,pickups,effects]:
		for node in collection:
			if is_instance_valid(node): node.queue_free()
		collection.clear()

func _end_run() -> void:
	if state!="playing": return
	survival_bonus=int(distance/75.0)
	var total_reward:=run_coins+survival_bonus
	bank_coins+=maxi(0,total_reward-last_reward)
	last_reward=total_reward
	state="gameover"; revive_pending=false; _release_touches(); best_distance=maxi(best_distance,int(distance)); _save()
	sound.play("game_over")

func request_revival() -> bool:
	if state!="gameover" or revive_used or revive_pending: return false
	if not is_instance_valid(revival_ads): return false
	revive_pending=revival_ads.show_revival_ad()
	return revive_pending

func _revive_ad_cancelled() -> void:
	revive_pending=false

func _revive_after_reward() -> void:
	if state!="gameover" or revive_used or player.health>0.0: return
	revive_used=true; revive_pending=false; revive_invulnerable=3.0
	player.health=maxf(1.0,player.max_health*0.5)
	for z in zombies.duplicate():
		if is_instance_valid(z) and _flat_distance(z.position,player.position)<13.0:
			_burst(z.position+Vector3(0,1.0,0),Color("ff9b55"),8)
			zombies.erase(z); z.queue_free()
	state="playing"; damage_flash=0.0; spawn_timer=1.8; shot_timer=0.25
	_release_touches(); _popup(player.position+Vector3(0,2.5,0),"REVIVED",Color("c9f54a"))

func _count_zombie_kind(type: String) -> int:
	var count:=0
	for z in zombies:
		if is_instance_valid(z) and not z.dead and z.kind==type: count+=1
	return count

func _spawn_zombie(at_z:=-48.0,forced_kind:="") -> void:
	var z:=ZombieScript.new(); var difficulty:=1.0+pow(run_time/55.0,1.15)*0.65; var roll:=rng.randf(); var kind:=forced_kind
	if kind.is_empty():
		if run_time>22.0 and not jockey_introduced: kind="jockey"
		elif run_time>36.0 and not banshee_introduced: kind="banshee"
		else:
			kind="walker"
			if run_time>20 and roll<minf(0.34,0.12+run_time*0.0015): kind="runner"
			if run_time>45 and roll>maxf(0.80,0.94-run_time*0.0008): kind="brute"
			if run_time>30 and roll>0.36 and roll<0.43 and _count_zombie_kind("jockey")<2: kind="jockey"
			elif run_time>70 and roll>0.90 and _count_zombie_kind("banshee")<1: kind="banshee"
	if kind=="jockey": jockey_introduced=true
	elif kind=="banshee":
		banshee_introduced=true
		banshee_warning=3.8
		if at_z< -30.0: at_z=-24.0
	var lanes:=[-2.4,0.0,2.4]; var lane: float=lanes[rng.randi_range(0,2)]
	if kind=="banshee": lane=_clear_lane_for_banshee(at_z,lane)
	for other in zombies:
		if is_instance_valid(other) and absf(other.position.x-lane)<1.1 and absf(other.position.z-at_z)<2.3: at_z-=2.8
	add_child(z); z.configure(kind,difficulty); z.position=Vector3(lane,0,at_z); zombies.append(z)

# ---- Banshee keep-out: she is slow and wide, so roadblocks, cars and barrels coming from the
# distance must never be spawned into her lane (they would drive straight through her).
const BANSHEE_KEEP_OUT:=1.75

func _banshee_xs() -> Array:
	var xs:=[]
	for z in zombies:
		if is_instance_valid(z) and not z.dead and z.kind=="banshee": xs.append(z.position.x)
	return xs

func _x_blocked_by_banshee(x: float,half_width: float) -> bool:
	for bx in _banshee_xs():
		if absf(x-bx)<BANSHEE_KEEP_OUT+half_width: return true
	return false

func _clear_lane_for_banshee(at_z: float,preferred: float) -> float:
	# Pick the lane with the most room around her spawn point.
	var best:=preferred; var best_score:=-1.0
	for lane in [preferred,-2.4,0.0,2.4]:
		var score:=100.0
		for obstacle in obstacles:
			if is_instance_valid(obstacle) and absf(obstacle.position.x-lane)<obstacle.half_extents.x+1.2:
				score=minf(score,absf(obstacle.position.z-at_z))
		for barrel in barrels:
			if is_instance_valid(barrel) and not barrel.dead and absf(barrel.position.x-lane)<1.4:
				score=minf(score,absf(barrel.position.z-at_z))
		if score>best_score+0.01: best=lane; best_score=score
	return best

func _wants_to_fire() -> bool:
	return true

func _fire() -> bool:
	if not player.can_fire(): return false
	if player.weapon=="LAUNCHER": return _fire_launcher()
	var sound_id: String=player.weapon.to_lower()
	if player.weapon=="PISTOL":
		var near_target:=is_instance_valid(aim_target) and _flat_distance(player.position,aim_target.position)<14.0
		sound_id="pistol_near" if near_target or not is_instance_valid(aim_target) else "pistol_far"
	player.fire(); sound.play(sound_id)
	var origin: Vector3=player.muzzle_position(); var base: Vector3=aim_direction.normalized()
	if is_instance_valid(aim_target) and not aim_target.dead and (zombies.has(aim_target) or watchers.has(aim_target) or barrels.has(aim_target) or crates.has(aim_target)):
		base=(aim_point-origin).normalized()
	var count: int=player.projectile_count
	for i in range(count):
		var b:=BulletScript.new(); b.position=origin; b.velocity=base.rotated(Vector3.UP,(i-(count-1)/2.0)*0.075)*player.bullet_speed
		b.damage=player.damage; b.pierce=player.pierce
		# Shots aimed at the Banshee punch through two zombies in the way, so she can be reached.
		if is_instance_valid(aim_target) and zombies.has(aim_target) and aim_target.kind=="banshee": b.pierce+=2
		add_child(b); bullets.append(b)
	return true

func _fire_launcher() -> bool:
	if not player.can_fire(): return false
	if player.fire_mode and player.fire_ammo<=0: player.fire_mode=false
	var origin: Vector3=player.muzzle_position()
	var base: Vector3=aim_direction.normalized()
	if is_instance_valid(aim_target) and not aim_target.dead and (zombies.has(aim_target) or watchers.has(aim_target) or barrels.has(aim_target) or crates.has(aim_target)):
		base=(aim_point-origin).normalized()
	base.y=0.0
	if base.length()<0.1: base=aim_direction
	base=base.normalized()
	player.fire(); sound.play("shotgun")
	_spawn_ordnance("fire" if player.fire_mode else "launcher",origin,base*14.0+Vector3(0,3.0,0))
	if player.fire_mode:
		player.fire_ammo-=1
		if player.fire_ammo<=0: player.fire_mode=false
	shake=maxf(shake,0.24)
	return true

func toggle_fire_mode() -> bool:
	if player.weapon!="LAUNCHER" or player.fire_ammo<=0: return false
	player.fire_mode=not player.fire_mode
	sound.play("gate")
	_popup(player.position+Vector3(0,2.5,0),"INCENDIARY" if player.fire_mode else "FRAG GRENADE",Color("ff7547") if player.fire_mode else Color("ffd275"))
	return true

func _throw_ordnance(kind: String) -> bool:
	if state!="playing": return false
	if kind=="frag":
		if player.grenade_count<=0: return false
		player.grenade_count-=1
	elif kind=="flash":
		if player.flashbang_count<=0: return false
		player.flashbang_count-=1
	else: return false
	var origin: Vector3=player.position+Vector3(0,1.35,0)+aim_direction*0.65
	_spawn_ordnance(kind,origin,aim_direction*9.0+Vector3(0,4.2,0))
	sound.play("reload")
	return true

func _spawn_ordnance(kind: String,origin: Vector3,initial_velocity: Vector3) -> Node3D:
	var projectile:=OrdnanceScript.new()
	projectile.kind=kind; projectile.position=origin; projectile.velocity=initial_velocity
	add_child(projectile); ordnance.append(projectile)
	return projectile

func request_reload() -> bool:
	if player.request_reload():
		sound.play("reload"); return true
	return false

func _tick_bullets(delta: float) -> void:
	for i in range(bullets.size()-1,-1,-1):
		var b=bullets[i]; b.tick(delta); var consumed:=false
		for z in zombies+watchers:
			if not is_instance_valid(z): continue
			var zp: Vector3=z.global_position
			var local_y: float=b.position.y-zp.y
			var height: float=z.collision_height()
			if not z.dead and not b.hit_targets.has(z) and local_y>0.05 and local_y<height and _flat_distance(b.position,zp)<z.radius+0.24:
				b.hit_targets.append(z); _hit_zombie(z,b.damage,_body_part(z,b.position),b.position)
				if b.pierce>0: b.pierce-=1
				else: consumed=true
				break
		if not consumed:
			for crate in crates:
				if crate.bullet_hits(b.position):
					consumed=true
					if crate.take_hit(maxi(1,roundi(b.damage/22.0))): _break_crate(crate)
					break
		if not consumed:
			for barrel in barrels:
				if not barrel.dead and not b.hit_targets.has(barrel) and b.position.y<2.4 and _flat_distance(b.position,barrel.position)<barrel.radius+0.24:
					b.hit_targets.append(barrel)
					if barrel.take_hit(b.damage): _explode(barrel)
					consumed=true; break
		if consumed or b.life<=0 or b.position.z< -65 or b.position.z>16 or absf(b.position.x)>8:
			bullets.remove_at(i); b.queue_free()

func _flat_distance(a: Vector3,b: Vector3) -> float:
	return Vector2(a.x-b.x,a.z-b.z).length()

func _tick_ordnance(delta: float) -> void:
	for i in range(ordnance.size()-1,-1,-1):
		var projectile=ordnance[i]
		projectile.tick(delta)
		if projectile.kind in ["launcher","fire"] and not projectile.detonate_requested:
			for z in zombies:
				if not is_instance_valid(z) or z.dead: continue
				var height: float=z.collision_height()
				if projectile.position.y>0.0 and projectile.position.y<height and _flat_distance(projectile.position,z.position)<z.radius+0.34:
					projectile.detonate_requested=true
					break
		if projectile.detonate_requested:
			_detonate_ordnance(projectile)
			ordnance.remove_at(i); projectile.queue_free()
		elif projectile.position.z< -70 or projectile.position.z>16 or absf(projectile.position.x)>10:
			ordnance.remove_at(i); projectile.queue_free()

func _detonate_ordnance(projectile: Node3D) -> void:
	var center: Vector3=projectile.position
	var kind: String=projectile.kind
	if kind=="flash":
		sound.play("explosion"); shake=maxf(shake,0.28)
		_burst(center,Color("d8f6ff"),34); _blast_sphere(center,Color(0.78,0.94,1.0,0.72),0.95,false)
		var ring:=EffectScript.new(); ring.position=Vector3(center.x,0.10,center.z); ring.life=0.40; ring.total_life=0.40
		add_child(ring); ring.make_shockwave(Color(0.72,0.93,1.0,0.85),0.65); effects.append(ring)
		for z in zombies:
			if is_instance_valid(z) and not z.dead and _flat_distance(z.position,center)<8.0:
				z.stun_timer=maxf(z.stun_timer,4.0)
		return
	sound.play("explosion"); shake=maxf(shake,0.85)
	_custom_explosion(center)
	_burst(center,Color("ffb14f"),26); _fire_spray(center)
	var radius := 4.5 if kind=="launcher" else 5.0
	if kind=="fire":
		radius=4.0
		_fire_spray(center)
		_blast_sphere(center,Color(1.0,0.20,0.035,0.58),0.95,false)
	for z in zombies.duplicate():
		if not is_instance_valid(z) or z.dead: continue
		if _flat_distance(z.position,center)<radius:
			if kind=="fire":
				z.burn_timer=maxf(z.burn_timer,5.0); z.burn_dps=24.0
				_hit_zombie(z,45.0,"torso",z.position+Vector3(0,1.0,0),Color("ff8a4f"))
			else:
				_hit_zombie(z,220.0 if kind=="frag" else player.damage,"torso",z.position+Vector3(0,1.0,0),Color("ffb15c"))
	for barrel in barrels.duplicate():
		if is_instance_valid(barrel) and not barrel.dead and _flat_distance(barrel.position,center)<radius and kind!="flash": _explode(barrel)
	if kind!="flash":
		for crate in crates:
			if not crate.broken and _flat_distance(crate.position,center)<radius and crate.take_hit(8): _break_crate(crate)

func _tick_zombies(delta: float) -> void:
	for i in range(zombies.size()-1,-1,-1):
		var z=zombies[i]; z.tick(delta)
		var burn_damage: float=z.consume_burn_damage_number()
		if burn_damage>0.0: _damage_number(z,burn_damage,Color("ff8a4f"))
		if z.dead:
			_hit_zombie(z,0.0,"torso",z.position+Vector3(0,1.0,0))
			continue
		if z.consume_banshee_pulse():
			var ignited:=0
			for other in zombies:
				if other==z or not is_instance_valid(other) or other.dead or other.kind=="banshee": continue
				if _flat_distance(z.position,other.position)<=12.0:
					other.ignite(5.5,8.0,5.0)
					_burst(other.position+Vector3(0,1.0,0),Color("ff7138"),8)
					ignited+=1
			if ignited>0:
				_popup(z.position+Vector3(0,2.8,0),"BANSHEE: FIRE FRENZY",Color("ff8a4f"))
		for other in zombies:
			if other==z or not is_instance_valid(other): continue
			var dx: float=z.position.x-other.position.x
			var dz: float=z.position.z-other.position.z
			var spacing: float=(z.radius+other.radius)*0.88
			if absf(dz)<1.15 and absf(dx)<spacing:
				z.position.x=clampf(z.position.x+(1.0 if dx>=0 else -1.0)*(spacing-absf(dx))*delta*2.2,-3.05,3.05)
		_avoid_barrels(z,delta)
		_avoid_obstacles(z,delta)
		if z.position.z>player.position.z-0.6 and z.position.z<player.position.z+0.8 and absf(z.position.x-player.position.x)<z.radius+0.38:
			_hurt_player(z.damage); _burst(z.position+Vector3(0,1,0),Color("91a85c"),8); zombies.remove_at(i); z.queue_free()
		elif z.position.z>13: zombies.remove_at(i); z.queue_free()

func _avoid_barrels(z: Node3D,delta: float) -> void:
	for barrel in barrels:
		if not is_instance_valid(barrel) or barrel.dead: continue
		var dx: float=z.position.x-barrel.position.x
		var dz: float=z.position.z-barrel.position.z
		var clearance: float=z.radius+barrel.radius+0.08
		# Start steering early so the zombie walks around the barrel naturally.
		if absf(dz)<2.4 and absf(dx)<clearance+0.35:
			var side: float=_barrel_avoid_side(z,barrel)
			var urgency: float=1.0-clampf(absf(dz)/2.4,0.0,1.0)
			var steer_speed: float=maxf(2.0,z.speed*0.65)
			z.position.x=clampf(z.position.x+side*steer_speed*(0.45+urgency*0.55)*delta,-3.05,3.05)
			dx=z.position.x-barrel.position.x
		# Resolve any remaining contact instead of allowing visual overlap.
		var minimum: float=z.radius+barrel.radius
		if absf(dz)>=minimum: continue
		var needed_x: float=sqrt(maxf(0.0,minimum*minimum-dz*dz))+0.015
		if absf(dx)>=needed_x: continue
		var side: float=_barrel_avoid_side(z,barrel)
		var new_x: float=barrel.position.x+side*needed_x
		if new_x < -3.05 or new_x > 3.05:
			new_x=barrel.position.x-side*needed_x
		z.position.x=clampf(new_x,-3.05,3.05)

func _barrel_avoid_side(z: Node3D,barrel: Node3D) -> float:
	var dx: float=z.position.x-barrel.position.x
	var side: float=1.0 if dx>0.0 else -1.0
	if absf(dx)<=0.06:
		var left_room: float=barrel.position.x+3.05
		var right_room: float=3.05-barrel.position.x
		if absf(left_room-right_room)>0.1:
			side=-1.0 if left_room>right_room else 1.0
		else:
			side=-1.0 if int(z.get_instance_id())%2==0 else 1.0
	var clearance: float=z.radius+barrel.radius+0.12
	if side>0.0 and barrel.position.x+clearance>3.05: return -1.0
	if side<0.0 and barrel.position.x-clearance< -3.05: return 1.0
	return side

func _body_part(z: Node3D,hit_position: Vector3) -> String:
	var local:=hit_position-z.global_position
	var ratio: float=local.y/z.collision_height()
	var w: float=1.28*ZombieScript.BRUTE_SCALE if z.kind=="brute" else (0.88 if z.kind=="runner" else 1.0)
	var head_ratio:=0.64 if z.kind=="jockey" else 0.73
	if ratio>head_ratio: return "head"
	if ratio<0.37: return "leg_l" if local.x<0 else "leg_r"
	if absf(local.x)>0.30*w and ratio>0.43: return "arm_l" if local.x<0 else "arm_r"
	return "torso"

const DAMAGE_RED:=Color("ff3030")

func _hit_zombie(z: Node3D,amount: float,part:="torso",hit_position:=Vector3.ZERO,_damage_color:=Color("f4f0df")) -> void:
	if hit_position==Vector3.ZERO: hit_position=z.global_position+Vector3(0,1.2,0)
	var multiplier: float=1.55 if part=="head" else (0.88 if part.begins_with("leg") else 1.0)
	var actual_damage: float=minf(maxf(0.0,z.health),amount*multiplier)
	if actual_damage>0.0:
		_damage_number(z,actual_damage,DAMAGE_RED)
	if z.take_hit(amount*multiplier):
		# Coins scale with how dangerous the zombie was (walker 1 ... banshee 8).
		var reward: int=int(z.reward)
		kills+=1; run_coins+=reward; sound.play("kill")
		kill_counts[z.kind]=int(kill_counts.get(z.kind,0))+1; kill_coins[z.kind]=int(kill_coins.get(z.kind,0))+reward
		var zp: Vector3=z.global_position
		_blood_spray(hit_position,28 if part=="head" else 20); _burst(hit_position,Color("78935c"),5); _dismember(z,part)
		_blood_splatter(Vector3(zp.x,0.0,zp.z),rng.randf_range(2.2,3.2)*(1.4 if z.kind=="brute" else 1.0),true)
		_popup(zp+Vector3(0,2.3,0),"+%d"%reward,Color("ffd25e"))
		zombies.erase(z); watchers.erase(z); z.queue_free()
	else:
		sound.play("hit"); _blood_spray(hit_position,7)
		if rng.randf()<0.5: _blood_splatter(Vector3(z.global_position.x,0.0,z.global_position.z),rng.randf_range(0.7,1.2),false)

func _damage_number(z: Node3D,amount: float,_color: Color) -> void:
	var e:=EffectScript.new()
	e.position=z.global_position+Vector3(rng.randf_range(-0.24,0.24),2.78,rng.randf_range(-0.12,0.12))
	e.velocity=Vector3(rng.randf_range(-0.16,0.16),1.05,0); e.life=0.78; e.total_life=0.78
	add_child(e); e.make_text("-%d"%maxi(1,roundi(amount)),DAMAGE_RED)
	e.label.font_size=64; e.label.pixel_size=0.0085; e.label.outline_size=12
	effects.append(e)

## Blood thrown away from the shooter: one directional splash (random shape out of eight,
## random size, angle jittered around the shot) plus flung droplets landing further along.
func _blood_splatter(pos: Vector3,size_m: float,kill: bool) -> void:
	var dir:=Vector3(aim_direction.x,0,aim_direction.z)
	if dir.length()<0.01: dir=Vector3.FORWARD
	dir=dir.normalized().rotated(Vector3.UP,rng.randf_range(-0.45,0.45))
	_spawn_blood_pool(pos+dir*size_m*0.25,size_m*rng.randf_range(0.85,1.15),11.0 if kill else 6.0,true,dir)
	if kill:
		for i in range(rng.randi_range(3,6)):
			var d:=dir.rotated(Vector3.UP,rng.randf_range(-0.6,0.6))
			_spawn_blood_pool(pos+d*rng.randf_range(0.9,2.8),rng.randf_range(0.18,0.5),9.0)

func _spawn_blood_pool(pos: Vector3,size_m: float,life: float,splash:=false,dir:=Vector3.ZERO) -> void:
	if blood_pools.size()>=MAX_BLOOD_POOLS:
		var oldest=blood_pools.pop_front(); if is_instance_valid(oldest): oldest.queue_free()
	var pool:=BloodPoolScript.new()
	# Tiny height steps stop overlapping pools from z-fighting on the road.
	pool.position=Vector3(pos.x,0.015+0.0008*(blood_pools.size()%12),pos.z)
	# Splash textures spray toward +U; turn that onto the spray direction. Droplets spin freely.
	pool.rotation.y=atan2(-dir.z,dir.x) if splash and dir!=Vector3.ZERO else rng.randf()*TAU
	add_child(pool); pool.setup(size_m,rng.randi(),life,splash); blood_pools.append(pool)

func _tick_blood(delta: float) -> void:
	for i in range(blood_pools.size()-1,-1,-1):
		var pool=blood_pools[i]
		if pool.tick(delta): blood_pools.remove_at(i); pool.queue_free()

func _blood_spray(pos: Vector3,count: int) -> void:
	for i in range(count):
		var e:=EffectScript.new(); e.position=pos
		e.velocity=aim_direction*rng.randf_range(1.0,3.8)+Vector3(rng.randf_range(-1.9,1.9),rng.randf_range(0.1,2.8),rng.randf_range(-0.8,0.8))
		e.gravity=-6.5; e.life=rng.randf_range(0.45,0.85); e.total_life=e.life; add_child(e)
		e.make_drop(Color("a5282c") if i%3 else Color("651b22"),rng.randf_range(0.045,0.105)); effects.append(e)

func _dismember(z: Node3D,part: String) -> void:
	var head: Array=["Head","Jaw","Brow","Brow.001","Cheek","Cheek.001","CrownLock","Ear","EyeSocket","EyeWhite","Fringe","HairMass","LowerLip","MouthCavity","NoseBridge","NoseTip","Pupil","Sideburn","Tooth"]
	var torso: Array=["Torso","ChestWound","ClothFold","CollarL","CollarR","Pocket","Rib","Tear"]
	var arm_l: Array=["ArmL","ElbowL","ForearmL","HandL","FingerL"]
	var arm_r: Array=["ArmR","ElbowR","ForearmR","HandR","FingerR"]
	var origin:=z.global_position+Vector3(0,1.05,0)
	_spawn_part(z.model,torso,origin,Vector3(rng.randf_range(-0.5,0.5),2.2,0.5))
	match part:
		"head":
			_spawn_part(z.model,head,origin,Vector3(0.7,4.2,-0.4)); _spawn_part(z.model,arm_l,origin,Vector3(-2.0,2.4,0.2)); _spawn_part(z.model,arm_r,origin,Vector3(2.0,2.6,-0.2))
		"arm_l": _spawn_part(z.model,arm_l,origin,Vector3(-3.0,3.1,0.3))
		"arm_r": _spawn_part(z.model,arm_r,origin,Vector3(3.0,3.1,0.3))
		"leg_l": _spawn_part(z.model,["LegL"],origin,Vector3(-2.2,2.5,0.4))
		"leg_r": _spawn_part(z.model,["LegR"],origin,Vector3(2.2,2.5,0.4))
		_:
			_spawn_part(z.model,head,origin,Vector3(0.3,3.7,-0.6)); _spawn_part(z.model,arm_l,origin,Vector3(-2.5,2.7,0.3)); _spawn_part(z.model,arm_r,origin,Vector3(2.5,2.7,-0.3))

func _spawn_part(source: Node3D,names: Array,pos: Vector3,force: Vector3) -> void:
	var e:=EffectScript.new(); e.position=pos; e.velocity=force; e.gravity=-7.5; e.life=1.25; e.total_life=e.life
	e.spin=Vector3(rng.randf_range(-4,4),rng.randf_range(-4,4),rng.randf_range(-4,4)); add_child(e); e.make_part(source,names); effects.append(e)

func _hurt_player(amount: float) -> void:
	if revive_invulnerable>0.0: return
	player.take_damage(amount); damage_flash=0.42; shake=0.75; sound.play("hurt")

## 0 at the start of a run, 1 after three minutes: drives how busy the road gets.
## Puts a fresh roadside zombie back on a block that lost its one (shot on an earlier pass).
func _refresh_watcher(road: Node3D) -> void:
	var index: int=roads.find(road)
	if index<0 or index%2!=0: return
	var old=road.get_meta("watcher",null)
	if old!=null and is_instance_valid(old) and not old.dead: return
	var w_rng:=RandomNumberGenerator.new(); w_rng.seed=rng.randi()
	watchers.append(DisasterDressing.spawn_watcher(road,index,ZombieScript,w_rng))

## Roadside zombies aren't statues: they turn to watch the survivor go by, and every few
## seconds do something: standing ones shuffle a few steps along the pavement, scratch, or
## sway and mutter; sitting ones lift their heads and gesture. Plays through the AnimationPlayer
## clips prepared in DisasterDressing.spawn_watcher.
func _tick_watchers(delta: float) -> void:
	for w in watchers:
		if not is_instance_valid(w) or w.dead: continue
		var anim: AnimationPlayer=w.animation_player
		var sitting: bool=w.get_meta("sitting",false)
		var base_yaw: float=w.get_meta("base_yaw",0.0)
		var gp: Vector3=w.global_position
		# Head-and-shoulders tracking: turn toward the survivor when they're close.
		var to_player:=player.global_position-gp
		var target_yaw: float=base_yaw
		if absf(to_player.z)<22.0:
			var look: float=atan2(to_player.x,to_player.z)
			target_yaw=base_yaw+clampf(wrapf(look-base_yaw,-PI,PI),-0.55 if sitting else -1.3,0.55 if sitting else 1.3)
		# Shuffling: walk a few steps along the pavement (road-local z), facing the way they go.
		var walk_left: float=w.get_meta("walk_left",0.0)
		if walk_left>0.0:
			var dir: float=w.get_meta("walk_dir",1.0)
			var step:=0.55*delta
			w.position.z+=dir*step; walk_left-=step; w.set_meta("walk_left",walk_left)
			target_yaw=0.0 if dir>0.0 else PI
			if walk_left<=0.0 and anim and anim.has_animation("ual_Idle"): anim.play("ual_Idle",0.4)
		w.model.rotation.y=lerp_angle(w.model.rotation.y,target_yaw,1.0-exp(-delta*(3.0 if walk_left>0.0 else 1.6)))
		var next_act: float=w.get_meta("next_act",3.0)-delta
		if next_act<=0.0 and walk_left<=0.0 and anim:
			next_act=rng.randf_range(3.5,7.5)
			var roll:=rng.randf()
			if sitting:
				var talk:="ual_Sitting_Talking" if anim.current_animation!="ual_Sitting_Talking" else "ual_Sitting_Idle"
				if anim.has_animation(talk): anim.play(talk,0.5)
			elif roll<0.45 and anim.has_animation("ual_Walk"):
				w.set_meta("walk_left",rng.randf_range(0.8,2.0)); w.set_meta("walk_dir",-1.0 if rng.randf()<0.5 else 1.0)
				anim.play("ual_Walk",0.35); anim.speed_scale=0.55
			elif roll<0.7 and anim.has_animation("Zombie_Scratch"):
				anim.play("Zombie_Scratch",0.3); anim.speed_scale=0.9
				next_act=rng.randf_range(2.0,3.0)
			elif anim.has_animation("ual_Idle_Talking"):
				anim.play("ual_Idle_Talking",0.4); anim.speed_scale=0.8
			elif anim.has_animation("ual_Idle"):
				anim.play("ual_Idle",0.4)
		w.set_meta("next_act",next_act)

func _pace() -> float:
	return clampf(run_time/180.0,0.0,1.0)

## True when nothing else (gate, crate, car/barrier, barrel) sits within `gap` metres of z,
## so road events arrive one at a time instead of piling up together.
func _road_clear(z: float,gap:=9.0) -> bool:
	for list in [gates,crates,obstacles,barrels]:
		for item in list:
			if is_instance_valid(item) and absf(item.position.z-z)<gap: return false
	return true

func _spawn_gate() -> void:
	# Never drop a gate on top of cars, barriers or weapon crates: try again a moment later.
	for o in obstacles:
		if is_instance_valid(o) and absf(o.position.z-(-40.0))<o.half_extents.y+3.0: gate_timer=1.0; return
	for c in crates:
		if is_instance_valid(c) and absf(c.position.z-(-40.0))<3.0: gate_timer=1.0; return
	var damage:={"id":"damage","title":"HEAVY ROUNDS","detail":"+8% DMG","color":Color("ff9e51")}
	var rate:={"id":"rate","title":"FAST TRIGGER","detail":"+6% RPM","color":Color("62dfe1")}
	var split:={"id":"split","title":"SPLIT BARREL","detail":"+1 BULLET","color":Color("cf9bff")}
	var heal:={"id":"heal","title":"FIELD MEDIC","detail":"+15 HP","color":Color("c9f54a")}
	# Small buffs, many gates. The big one (an extra bullet) only turns up once every eight gates.
	var sets:=[[damage,rate],[rate,heal],[damage,heal],[rate,damage],[heal,damage],[damage,rate],[heal,rate],[split,damage]]
	var pair: Array=sets[new_gate_index%sets.size()]; new_gate_index+=1
	var gate:=GateScript.new(); gate.position=Vector3(0,0,-40); gate.setup(pair[0],pair[1],language_code); add_child(gate); gates.append(gate)

func _tick_gates(delta: float) -> void:
	for i in range(gates.size()-1,-1,-1):
		var g=gates[i]; var old_z: float=g.position.z; g.tick(delta)
		if not g.resolved and old_z<player.position.z and g.position.z>=player.position.z:
			var choice: Dictionary=g.choose(player.position.x)
			if not choice.is_empty(): player.apply_upgrade(choice.id); sound.play("gate"); _popup(player.position+Vector3(0,2.6,0),choice.detail,g.SIDE_COLORS[g.selected].lightened(0.3))
		if g.fade<=0 or g.position.z>14: gates.remove_at(i); g.queue_free()

func _spawn_barrel() -> void:
	var x:=rng.randf_range(-2.7,2.7)
	for attempt in range(8):
		if not _x_blocked_by_banshee(x,0.45): break
		x=rng.randf_range(-2.7,2.7)
	if _x_blocked_by_banshee(x,0.45): return # no room this time; skip rather than overlap her
	var barrel:=BarrelScript.new(); barrel.position=Vector3(x,0,-45); add_child(barrel); barrels.append(barrel)

func _crate_hits(id: String) -> int:
	# Tougher crates the longer you survive and the better the gun inside.
	var base: float=6.0+run_time*0.28
	return clampi(roundi(base*float(CRATE_TIER.get(id,1.0))),5,75)

func _crate_spot_clear(x: float,z: float) -> bool:
	if _x_blocked_by_banshee(x,0.75): return false
	for o in obstacles:
		if is_instance_valid(o) and absf(o.position.z-z)<o.half_extents.y+2.2 and absf(o.position.x-x)<o.half_extents.x+1.0: return false
	for b in barrels:
		if is_instance_valid(b) and absf(b.position.z-z)<2.2 and absf(b.position.x-x)<1.3: return false
	for g in gates:
		if is_instance_valid(g) and absf(g.position.z-z)<3.5: return false
	return true

func _spawn_crates() -> void:
	var choices: Array=CRATE_WEAPONS.duplicate(); choices.erase(player.weapon)
	choices.shuffle()
	var z:=-46.0
	var spots: Array=[[-1.7,1.7],[-2.2,0.9],[-0.9,2.2]][rng.randi_range(0,2)] if rng.randf()<0.15+0.35*_pace() else [rng.randf_range(-2.2,2.2)]
	var used:=0
	for x in spots:
		if not _crate_spot_clear(x,z): continue
		var crate:=WeaponCrateScript.new(); var id: String=choices[used%choices.size()]; used+=1
		crate.setup(id,_crate_hits(id)); crate.position=Vector3(x,0,z); add_child(crate); crates.append(crate)

func _break_crate(crate: Node3D) -> void:
	sound.play("pickup"); shake=maxf(shake,0.35)
	var center: Vector3=crate.position+Vector3(0,0.55,0)
	_burst(center,Color("8a6a3c"),16); _burst(center+Vector3(0,0.6,0),Color("6cc8ff"),10)
	# Swap immediately on break; the flying gun is only the visual of it landing in your hands.
	player.stowed={}; player.set_weapon(crate.weapon_id); sound.play("gate")
	_popup(player.position+Vector3(0,2.5,0),crate.display_name(),Color("7fd2ff"))

func _tick_crates(delta: float) -> void:
	var hand: Vector3=player.position+Vector3(0,1.25,0.1)
	for i in range(crates.size()-1,-1,-1):
		var c=crates[i]; c.tick(delta,hand)
		# Crates are not solid: the runner can run straight through them.
		if c.arrived or (c.broken and c.flight>1.5):
			crates.remove_at(i); c.queue_free(); continue
		if not c.broken and c.position.z>13: crates.remove_at(i); c.queue_free()

func _tick_barrels(delta: float) -> void:
	for i in range(barrels.size()-1,-1,-1):
		var b=barrels[i]
		if b.dead: barrels.remove_at(i); b.queue_free(); continue
		b.tick(delta)
		if b.position.z>13: barrels.remove_at(i); b.queue_free()

func _resolve_barrel_collision() -> void:
	for barrel in barrels:
		if not is_instance_valid(barrel) or barrel.dead: continue
		var dz: float=player.position.z-barrel.position.z
		var minimum: float=barrel.radius+0.40
		if absf(dz)>=minimum or absf(player.position.x-barrel.position.x)>=minimum: continue
		var clearance: float=sqrt(maxf(0.0,minimum*minimum-dz*dz))+0.025
		var left: float=clampf(barrel.position.x-clearance,-3.15,3.15)
		var right: float=clampf(barrel.position.x+clearance,-3.15,3.15)
		var new_x: float=left if absf(player.position.x-left)<absf(player.position.x-right) else right
		if absf(new_x-barrel.position.x)<clearance-0.02:
			new_x=right if new_x==left else left
		player.position.x=new_x; player.target_x=new_x

func _spawn_obstacle(kind: String,lane_x: float,at_z: float=-48.0) -> Node3D:
	var obstacle:=RoadObstacleScript.new()
	obstacle.kind=kind
	obstacle.position=Vector3(lane_x,0,at_z)
	add_child(obstacle)
	obstacles.append(obstacle)
	return obstacle

func _spawn_obstacle_pattern() -> void:
	var lanes: Array=[-2.4,0.0,2.4]
	var safe_lane:=rng.randi_range(0,2)
	var blocked: Array=[0,1,2]
	blocked.erase(safe_lane)
	if rng.randf()<lerpf(0.85,0.5,_pace()): # early on usually just one lane is blocked
		blocked=[blocked[rng.randi_range(0,blocked.size()-1)]]
	# Never block the lane a Banshee is walking in.
	for lane_index in blocked.duplicate():
		if _x_blocked_by_banshee(lanes[lane_index],0.55): blocked.erase(lane_index)
	if blocked.is_empty(): return
	var car_lane: int=blocked[rng.randi_range(0,blocked.size()-1)]
	for lane_index in blocked:
		_spawn_obstacle("car" if lane_index==car_lane else "fence",lanes[lane_index],-48.0-float(blocked.find(lane_index))*0.8)

func _tick_obstacles(delta: float) -> void:
	for i in range(obstacles.size()-1,-1,-1):
		var obstacle=obstacles[i]
		obstacle.tick(delta)
		if obstacle.overlaps(player.position):
			var clearance: float=obstacle.half_extents.x+0.43
			var left: float=clampf(obstacle.position.x-clearance,-3.15,3.15)
			var right: float=clampf(obstacle.position.x+clearance,-3.15,3.15)
			var new_x: float=left if absf(player.position.x-left)<absf(player.position.x-right) else right
			if absf(new_x-obstacle.position.x)<clearance-0.04:
				new_x=right if is_equal_approx(new_x,left) else left
			player.position.x=new_x
			player.target_x=new_x
			if obstacle.hit_cooldown<=0.0:
				obstacle.hit_cooldown=1.0
				_hurt_player(obstacle.damage)
				shake=maxf(shake,0.55)
				_burst(player.position+Vector3(0,0.55,0),Color("f2a04d"),8)
				_popup(player.position+Vector3(0,2.45,0),"WRECK -%d"%int(obstacle.damage) if obstacle.kind=="car" else "BARRIER -%d"%int(obstacle.damage),Color("ffad72"))
		if obstacle.position.z>13.0:
			obstacles.remove_at(i)
			obstacle.queue_free()

func _avoid_obstacles(z: Node3D,delta: float) -> void:
	for obstacle in obstacles:
		if not is_instance_valid(obstacle): continue
		var dx: float=z.position.x-obstacle.position.x
		var dz: float=z.position.z-obstacle.position.z
		var clearance: float=obstacle.half_extents.x+z.radius+0.08
		if absf(dz)<obstacle.half_extents.y+2.0 and absf(dx)<clearance+0.22:
			var side: float=_obstacle_avoid_side(z,obstacle)
			z.position.x=clampf(z.position.x+side*maxf(2.2,z.speed*0.75)*delta,-3.05,3.05)
			dx=z.position.x-obstacle.position.x
		if absf(dz)<obstacle.half_extents.y+z.radius and absf(dx)<clearance:
			var side: float=_obstacle_avoid_side(z,obstacle)
			var new_x: float=obstacle.position.x+side*(clearance+0.025)
			if new_x< -3.05 or new_x>3.05: new_x=obstacle.position.x-side*(clearance+0.025)
			z.position.x=clampf(new_x,-3.05,3.05)

func _obstacle_avoid_side(z: Node3D,obstacle: Node3D) -> float:
	var dx: float=z.position.x-obstacle.position.x
	var side:=1.0 if dx>0.0 else -1.0
	var clearance: float=obstacle.half_extents.x+z.radius+0.12
	if absf(dx)<=0.08 or (side>0 and obstacle.position.x+clearance>3.05) or (side<0 and obstacle.position.x-clearance< -3.05):
		var left_room: float=obstacle.position.x+3.05
		var right_room: float=3.05-obstacle.position.x
		side=-1.0 if left_room>right_room else 1.0
	return side

func _explode(barrel: Node3D) -> void:
	barrel.dead=true; sound.play("explosion"); shake=1.0
	if OS.get_name()=="iOS": Input.vibrate_handheld(200,0.85)
	var center:=barrel.position+Vector3(0,0.55,0)
	# Debris and the custom blast are spawned together, with no delayed stock VFX.
	_spawn_part(barrel.model,["Cap"],center,Vector3(0.8,4.0,0.2))
	_spawn_part(barrel.model,["Ring"],center,Vector3(-1.5,2.8,0.4))
	_spawn_part(barrel.model,["Barrel"],center,Vector3(1.8,2.2,-0.3))
	_custom_explosion(center)
	_burst(center,Color("ffd275"),18); _fire_spray(center)
	if _flat_distance(player.position,barrel.position)<3.25:
		if player.has_armor:
			_hurt_player(player.max_health*0.90); _popup(player.position+Vector3(0,2.6,0),"ARMOR: -90% HP",Color("72d9e5"))
		else:
			_hurt_player(player.max_health*2.0); _popup(player.position+Vector3(0,2.6,0),"NO ARMOR",Color("ff6547"))
	for z in zombies.duplicate():
		if is_instance_valid(z) and _flat_distance(z.position,barrel.position)<3.4: _hit_zombie(z,150,"torso",z.position+Vector3(0,1.1,0),Color("ffb15c"))

func _custom_explosion(pos: Vector3) -> void:
	var fx:=ExplosionScript.new()
	fx.position=pos
	add_child(fx)
	effects.append(fx)

func _blast_sphere(pos: Vector3,color: Color,size: float,smoke: bool) -> void:
	var e:=EffectScript.new(); e.position=pos; e.life=0.38 if not smoke else 0.9; e.total_life=e.life
	add_child(e); e.make_blast(color,size,smoke); effects.append(e)

func _fire_spray(pos: Vector3) -> void:
	for i in range(36):
		var angle:=rng.randf_range(0,TAU); var e:=EffectScript.new(); e.position=pos
		e.velocity=Vector3(cos(angle)*rng.randf_range(1.2,5.0),rng.randf_range(0.8,4.5),sin(angle)*rng.randf_range(1.2,5.0))
		e.gravity=-5.5; e.life=rng.randf_range(0.35,0.75); e.total_life=e.life; add_child(e)
		e.make_drop(Color("ffd56a") if i%3==0 else Color("f05a28"),rng.randf_range(0.045,0.12)); effects.append(e)

func _spawn_pickup(kind: String,at_z:=-38.0) -> void:
	var pickup:=PickupScript.new(); pickup.kind=kind
	var lanes:=[-2.4,0.0,2.4]; pickup.position=Vector3(lanes[rng.randi_range(0,2)],0,at_z)
	add_child(pickup); pickups.append(pickup)

func _tick_pickups(delta: float) -> void:
	for i in range(pickups.size()-1,-1,-1):
		var p=pickups[i]; p.tick(delta)
		if _flat_distance(p.position,player.position)<0.82:
			if p.kind=="ammo":
				player.reserve_ammo+=player.magazine_size*2; _popup(player.position+Vector3(0,2.4,0),"AMMO +%d"%(player.magazine_size*2),Color("ffd275"))
			elif p.kind=="armor":
				player.set_armor(true); _popup(player.position+Vector3(0,2.4,0),"ARMOR EQUIPPED",Color("72d9e5"))
			elif p.kind=="helmet":
				player.set_helmet(true); _popup(player.position+Vector3(0,2.4,0),"HELMET: +20% PROTECTION",Color("b6d38a"))
			elif p.kind=="grenade":
				player.grenade_count=mini(8,player.grenade_count+2); _popup(player.position+Vector3(0,2.4,0),"FRAG +2",Color("b6d38a"))
			elif p.kind=="flashbang":
				player.flashbang_count=mini(5,player.flashbang_count+1); _popup(player.position+Vector3(0,2.4,0),"FLASH +1",Color("bdefff"))
			elif p.kind=="launcher":
				player.set_weapon("LAUNCHER"); _popup(player.position+Vector3(0,2.4,0),"GRENADE LAUNCHER",Color("ff9b55"))
			elif p.kind=="fire_round":
				player.fire_ammo=mini(24,player.fire_ammo+4); _popup(player.position+Vector3(0,2.4,0),"INCENDIARY +4",Color("ff6547"))
			else:
				player.health=minf(player.max_health,player.health+35); _popup(player.position+Vector3(0,2.4,0),"HEALTH +35",Color("c9f54a"))
			sound.play("pickup"); pickups.remove_at(i); p.queue_free()
		elif p.position.z>13: pickups.remove_at(i); p.queue_free()

func _burst(pos: Vector3,color: Color,count: int) -> void:
	for i in range(count):
		var e:=EffectScript.new(); e.position=pos; e.velocity=Vector3(rng.randf_range(-2,2),rng.randf_range(0.5,3),rng.randf_range(-2,2)); e.gravity=-5
		e.life=rng.randf_range(0.35,0.65); e.total_life=e.life; add_child(e); e.make_spark(color,rng.randf_range(0.035,0.075)); effects.append(e)

func _popup(pos: Vector3,text: String,color: Color) -> void:
	var e:=EffectScript.new(); e.position=pos; e.velocity=Vector3(0,0.8,0); e.life=0.85; e.total_life=0.85; add_child(e); e.make_text(text,color); effects.append(e)

func _tick_effects(delta: float) -> void:
	for i in range(effects.size()-1,-1,-1):
		var e=effects[i]; e.tick(delta)
		if e.life<=0: effects.remove_at(i); e.queue_free()

func _update_mouse_aim() -> void:
	if not is_instance_valid(camera) or not is_instance_valid(player): return
	aim_target=null
	for z in zombies+watchers:
		if not is_instance_valid(z) or z.dead or camera.is_position_behind(z.global_position): continue
		var top:=camera.unproject_position(z.global_position+Vector3(0,z.collision_height()*0.96,0))
		var bottom:=camera.unproject_position(z.global_position+Vector3(0,0.12,0))
		var hit_rect:=Rect2(Vector2((top.x+bottom.x)*0.5-27,top.y),Vector2(54,maxf(20,bottom.y-top.y))).grow(5)
		if hit_rect.has_point(mouse_position):
			var ratio:=clampf((mouse_position.y-top.y)/maxf(1,bottom.y-top.y),0,1)
			var height:=lerpf(z.collision_height()*0.90,0.24,ratio)
			aim_target=z; aim_point=z.global_position+Vector3(0,height,0)
			var target_flat:=aim_point-player.global_position; target_flat.y=0
			if target_flat.length()>0.15: aim_direction=target_flat.normalized()
			return
	for barrel in barrels:
		if not is_instance_valid(barrel) or barrel.dead or camera.is_position_behind(barrel.global_position): continue
		var top:=camera.unproject_position(barrel.global_position+Vector3(0,barrel.height,0))
		var bottom:=camera.unproject_position(barrel.global_position+Vector3(0,0.03,0))
		var center_x: float=(top.x+bottom.x)*0.5
		var edge:=camera.unproject_position(barrel.global_position+Vector3(barrel.radius,barrel.height*0.5,0))
		var half_width: float=maxf(12.0,absf(edge.x-center_x)+6.0)
		var hit_rect:=Rect2(Vector2(center_x-half_width,top.y),Vector2(half_width*2.0,maxf(24.0,bottom.y-top.y))).grow(4)
		if hit_rect.has_point(mouse_position):
			aim_target=barrel; aim_point=barrel.global_position+Vector3(0,barrel.height*0.5,0)
			var target_flat:=aim_point-player.global_position; target_flat.y=0
			if target_flat.length()>0.15: aim_direction=target_flat.normalized()
			return
	for crate in crates:
		if not is_instance_valid(crate) or crate.broken or camera.is_position_behind(crate.global_position): continue
		var c_top:=camera.unproject_position(crate.global_position+Vector3(0,2.0,0))
		var c_bottom:=camera.unproject_position(crate.global_position+Vector3(0,0.03,0))
		var c_edge:=camera.unproject_position(crate.global_position+Vector3(crate.half_extents.x,0.4,0))
		var c_half: float=maxf(16.0,absf(c_edge.x-c_bottom.x)+8.0)
		var c_rect:=Rect2(Vector2(c_bottom.x-c_half,c_top.y),Vector2(c_half*2.0,maxf(30.0,c_bottom.y-c_top.y))).grow(4)
		if c_rect.has_point(mouse_position):
			aim_target=crate; aim_point=crate.global_position+Vector3(0,0.45,0)
			var c_flat:=aim_point-player.global_position; c_flat.y=0
			if c_flat.length()>0.15: aim_direction=c_flat.normalized()
			return
	var origin:=camera.project_ray_origin(mouse_position); var direction:=camera.project_ray_normal(mouse_position)
	if absf(direction.y)<0.001: return
	var point:=origin+direction*((1.15-origin.y)/direction.y)
	var flat:=point-player.global_position; flat.y=0
	if flat.length()>0.15: aim_direction=flat.normalized()

func _update_touch_aim() -> void:
	aim_target=null; var best_score:=0.94
	for z in zombies+watchers:
		if not is_instance_valid(z) or z.dead: continue
		if watchers.has(z) and z.global_position.z>player.global_position.z-1.5: continue # behind: ignore
		var flat: Vector3=z.global_position-player.global_position; flat.y=0
		if flat.length()<0.2 or flat.length()>42: continue
		var score: float=aim_direction.dot(flat.normalized())-flat.length()*0.0008
		if z.kind=="banshee": score+=0.04 # the Banshee is the priority target when she's roughly in line
		if score>best_score:
			best_score=score; aim_target=z; aim_point=z.global_position+Vector3(0,z.collision_height()*0.62,0)
	for barrel in barrels:
		if not is_instance_valid(barrel) or barrel.dead: continue
		var flat: Vector3=barrel.global_position-player.global_position; flat.y=0
		if flat.length()<0.2 or flat.length()>42: continue
		var score: float=aim_direction.dot(flat.normalized())-flat.length()*0.0008
		if score>best_score:
			best_score=score; aim_target=barrel; aim_point=barrel.global_position+Vector3(0,barrel.height*0.5,0)
	for crate in crates:
		if not is_instance_valid(crate) or crate.broken: continue
		var flat: Vector3=crate.global_position-player.global_position; flat.y=0
		if flat.length()<0.2 or flat.length()>42: continue
		var score: float=aim_direction.dot(flat.normalized())-flat.length()*0.0008
		if score>best_score:
			best_score=score; aim_target=crate; aim_point=crate.global_position+Vector3(0,0.45,0)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode in [KEY_ENTER,KEY_SPACE,KEY_ESCAPE] and state=="intro":
			_finish_intro()
			return
		if state=="shop" and event.keycode in [KEY_LEFT,KEY_A]: select_shop_item(shop_index-1); return
		if state=="shop" and event.keycode in [KEY_RIGHT,KEY_D]: select_shop_item(shop_index+1); return
		if state=="shop" and event.keycode in [KEY_ENTER,KEY_SPACE]:
			if buy_item(shop_items[shop_index].id): shop_truck.celebrate_purchase(shop_items[shop_index].id)
			return
		if event.keycode in [KEY_ENTER,KEY_SPACE] and state in ["menu","gameover"]: start_run()
		elif event.keycode in [KEY_ESCAPE,KEY_P]:
			if state=="playing": state="paused"; _release_touches()
			elif state=="paused": state="playing"
		elif event.keycode==KEY_R and state=="playing": request_reload()
		elif event.keycode in [KEY_E,KEY_TAB] and state=="playing": swap_weapon()
		elif event.keycode==KEY_G and state=="playing": _throw_ordnance("frag")
		elif event.keycode==KEY_F and state=="playing": _throw_ordnance("flash")
		elif event.keycode==KEY_Q and state=="playing": toggle_fire_mode()
	if state=="character_select":
		if event is InputEventScreenDrag and event.position.x>120 and event.position.x<420: lobby.drag(event.relative.x)
		elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) and event.position.x>120 and event.position.x<420: lobby.drag(event.relative.x)
	if event is InputEventMouseMotion:
		mouse_position=event.position
		if state=="playing" and not touch_controls: _update_mouse_aim()
	elif event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT:
		if event.pressed: _pointer_down(event.position)
	elif event is InputEventScreenTouch:
		touch_controls=true
		if event.pressed:
			if _pointer_down(event.position): return
			if state=="playing":
				if event.position.x<270 and left_touch_id==-1:
					left_touch_id=event.index; left_origin=event.position; left_knob=event.position; left_stick=Vector2.ZERO
				elif event.position.x>=270 and right_touch_id==-1:
					right_touch_id=event.index; right_origin=event.position; right_knob=event.position; right_stick=Vector2.ZERO
		else:
			if event.index==left_touch_id: left_touch_id=-1; left_stick=Vector2.ZERO; left_knob=left_origin
			if event.index==right_touch_id: right_touch_id=-1; right_stick=Vector2.ZERO; right_knob=right_origin
	elif event is InputEventScreenDrag:
		if event.index==left_touch_id:
			# Left stick only steers sideways, so its knob slides on a horizontal track.
			left_stick=Vector2(clampf((event.position.x-left_origin.x)/58.0,-1.0,1.0),0.0); left_knob=left_origin+left_stick*46.0
		elif event.index==right_touch_id:
			right_stick=((event.position-right_origin)/58.0).limit_length(1.0); right_knob=right_origin+right_stick*46.0

func _release_touches() -> void:
	left_touch_id=-1; right_touch_id=-1; left_stick=Vector2.ZERO; right_stick=Vector2.ZERO
	left_origin=STICK_LEFT; right_origin=STICK_RIGHT; left_knob=left_origin; right_knob=right_origin

func _pointer_down(pos: Vector2) -> bool:
	if state=="intro":
		_finish_intro()
		return true
	if state=="menu":
		if Rect2(466,10,70,70).has_point(pos): settings_return_state="menu"; state="settings"; return true
		# The title goes straight into a run; the character lobby is where every run ends.
		sound.play("gate"); start_run(); return true
	elif state=="lootbox":
		if Rect2(24,24,100,48).has_point(pos): close_lootbox()
		return true
	elif state=="character_select":
		# Lobby layout (see hud._draw_lobby): characters left, pets right, survivor in the middle.
		for i in range(LOBBY_SLOTS):
			if Rect2(LOBBY_LEFT_X,LOBBY_TOP+i*LOBBY_STEP,LOBBY_CARD.x,LOBBY_CARD.y).has_point(pos):
				if i<lobby.CHARACTERS.size(): select_character(i)
				else: lobby_toast=1.6
				return true
			if Rect2(LOBBY_RIGHT_X,LOBBY_TOP+i*LOBBY_STEP,LOBBY_CARD.x,LOBBY_CARD.y).has_point(pos): lobby_toast=1.6; return true
		if Rect2(118,430,56,84).has_point(pos): select_character(character_choice-1); return true
		if Rect2(366,430,56,84).has_point(pos): select_character(character_choice+1); return true
		if Rect2(66,836,408,76).has_point(pos): start_run(); return true
		if Rect2(16,22,150,52).has_point(pos): open_shop(); return true
		if Rect2(466,10,70,70).has_point(pos): settings_return_state="character_select"; state="settings"; return true
		return true
	elif state=="settings":
		if Rect2(66,220,408,70).has_point(pos): sound.muted=not sound.muted; _save(); return true
		if Rect2(66,316,408,70).has_point(pos): auto_reload=not auto_reload; _save(); return true
		if Rect2(66,412,408,70).has_point(pos): open_language(); return true
		if Rect2(66,508,408,70).has_point(pos): text_size=(text_size+1)%3; sound.play("hit"); _save(); return true
		if Rect2(66,810,408,64).has_point(pos): state=settings_return_state; return true
	if state=="gameover" and Rect2(66,586,408,70).has_point(pos) and not revive_used: request_revival(); return true
	if state=="gameover" and Rect2(66,672,408,66).has_point(pos): go_to_lobby(); return true
	if state=="gameover" and Rect2(66,758,408,54).has_point(pos): open_shop(); return true
	if state=="shop":
		if Rect2(24,24,100,44).has_point(pos): close_shop(); return true
		if Rect2(404,24,112,48).has_point(pos): open_lootbox(); return true
		if Rect2(30,786,80,60).has_point(pos): select_shop_item(shop_index-1); return true
		if Rect2(430,786,80,60).has_point(pos): select_shop_item(shop_index+1); return true
		if Rect2(124,786,292,60).has_point(pos):
			var id: String=shop_items[shop_index].id
			shop_truck.focus(id)
			if buy_item(id): shop_truck.celebrate_purchase(id)
			return true
		for i in range(shop_items.size()):
			if Rect2(30+i*60,862,56,44).has_point(pos): select_shop_item(i); return true
	elif state=="language":
		for i in range(Localization.LANGUAGES.size()):
			var rect:=Rect2(30+(i%2)*245,150+floori(i/2.0)*62,235,50)
			if rect.has_point(pos): language_code=Localization.LANGUAGES[i].code; sound.play("gate"); _save(); return true
		if Rect2(66,840,408,60).has_point(pos): state="settings"; return true
	elif state=="playing":
		if PAUSE_BUTTON.has_point(pos): state="paused"; _release_touches(); return true
		if touch_controls and pos.distance_to(BTN_SWAP)<BTN_RADIUS+4: swap_weapon(); return true
		if touch_controls and pos.distance_to(BTN_RELOAD)<BTN_RADIUS+6: request_reload(); return true
		if touch_controls and pos.distance_to(BTN_FRAG)<BTN_RADIUS: _throw_ordnance("frag"); return true
		if touch_controls and pos.distance_to(BTN_FLASH)<BTN_RADIUS: _throw_ordnance("flash"); return true
		if touch_controls and player.weapon=="LAUNCHER" and pos.distance_to(BTN_FIRE_MODE)<BTN_RADIUS: toggle_fire_mode(); return true
	elif state=="paused":
		if Rect2(66,468,408,58).has_point(pos): auto_reload=not auto_reload; _save(); return true
		if Rect2(66,548,408,68).has_point(pos): state="playing"; return true
		if Rect2(66,632,408,58).has_point(pos): open_shop(); return true
		if Rect2(66,708,408,58).has_point(pos): start_run(); return true
		if Rect2(66,784,408,58).has_point(pos):
			_release_touches(); go_to_lobby(); return true
	return false

func _load_save() -> void:
	var c:=ConfigFile.new()
	if c.load("user://dead_run.cfg")==OK:
		best_distance=int(c.get_value("run","best",0)); character_choice=int(c.get_value("run","character",0)); auto_reload=bool(c.get_value("gameplay","auto_reload_v3",true)); text_size=clampi(int(c.get_value("display","text_size",1)),0,2)
		language_code=str(c.get_value("ui","language",language_code)); bank_coins=int(c.get_value("wallet","coins",0))
		for id in meta_upgrades.keys(): meta_upgrades[id]=int(c.get_value("upgrades",id,0))
func _read_muted() -> bool:
	var c:=ConfigFile.new()
	return bool(c.get_value("audio","muted",false)) if c.load("user://dead_run.cfg")==OK else false
func _save() -> void:
	if "--smoke-test" in OS.get_cmdline_user_args() or "--soak-test" in OS.get_cmdline_user_args(): return
	var c:=ConfigFile.new(); c.set_value("run","best",best_distance); c.set_value("run","character",character_choice); c.set_value("gameplay","auto_reload_v3",auto_reload); c.set_value("display","text_size",text_size)
	c.set_value("ui","language",language_code); c.set_value("wallet","coins",bank_coins)
	for id in meta_upgrades.keys(): c.set_value("upgrades",id,meta_upgrades[id])
	c.set_value("audio","muted",sound.muted if is_instance_valid(sound) else false); c.save("user://dead_run.cfg")

func _capture() -> void:
	await get_tree().create_timer(0.4).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://menu-3d.png")
	open_shop(); await get_tree().create_timer(0.35).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://shop-3d.png")
	close_shop(); open_language(); await get_tree().create_timer(0.15).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://languages-3d.png")
	enter_lobby(); select_character(0); await get_tree().create_timer(0.4).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://lobby-mason.png")
	select_character(1); await get_tree().create_timer(0.4).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://lobby-riley.png")
	state="menu"; character_choice=1; player.set_character(1); start_run()
	for i in range(4): _spawn_zombie(-7-i*6)
	_spawn_gate(); gates[0].position.z=-12
	_spawn_pickup("ammo",-5); pickups[0].position.x=-2.0
	_spawn_pickup("medkit",-14); pickups[1].position.x=2.2
	_spawn_obstacle("car",2.05,-8.0)
	_spawn_obstacle("fence",-2.05,-4.8)
	aim_direction=Vector3(-0.15,0,-1).normalized(); mouse_position=Vector2(220,390)
	await get_tree().create_timer(0.7).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://gameplay-3d.png")
	get_viewport().get_texture().get_image().save_png("res://diagnostics/obstacles/roadblocks.png")
	player.set_character(0); character_choice=0
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://gameplay-male-hd.png")
	for weapon_id in ["PISTOL","SMG","SHOTGUN","SNIPER","RIFLE"]:
		player.set_weapon(weapon_id)
		await get_tree().create_timer(0.16).timeout; await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://diagnostics/weapons_hd/gameplay_"+weapon_id.to_lower()+".png")
	player.set_weapon("PISTOL")
	player.set_character(1); character_choice=1
	for weapon_id in ["PISTOL","SMG","SHOTGUN","SNIPER","RIFLE"]:
		player.set_weapon(weapon_id)
		await get_tree().create_timer(0.16).timeout; await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://diagnostics/weapons_hd/gameplay_female_"+weapon_id.to_lower()+".png")
	player.set_weapon("PISTOL")
	touch_controls=true; right_stick=Vector2(-0.15,-1).normalized(); right_knob=right_origin+right_stick*46
	await get_tree().create_timer(0.15).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://gameplay-touch.png")
	touch_controls=false; player.ammo=0; auto_reload=false; player.set_armor(true); player.set_helmet(true)
	_spawn_pickup("armor",-3); pickups[-1].position.x=-2.3
	_spawn_pickup("helmet",-6); pickups[-1].position.x=2.3
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://armor-3d.png")
	hud.visible=false
	state="menu"
	for p in pickups: p.visible=false
	for g in gates: g.visible=false
	for z in zombies: z.visible=false
	camera.position=Vector3(2.8,2.35,8.0); camera.look_at(player.position+Vector3(0,1.05,0))
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://equipment-closeup-3d.png")
	hud.visible=true
	state="playing"
	camera.position=Vector3(0,6.4,13.5); camera.look_at(player.position+Vector3(0,0,-7.0))
	for p in pickups: p.visible=true
	for g in gates: g.visible=true
	for z in zombies: z.visible=true
	_spawn_zombie(-4); zombies[-1].position.x=0; aim_direction=Vector3.FORWARD
	_hit_zombie(zombies[-1],1000,"head",zombies[-1].position+Vector3(0,1.75,0))
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://blood-3d.png")
	_spawn_barrel(); barrels[-1].position=Vector3(1.4,0,-4); _explode(barrels[-1])
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://explosion-3d.png")
	# Ordnance captures use the live game scene, not offline model renders.
	start_run(); _clear_world(); state="playing"; shot_timer=999; auto_reload=false; hint_time=0; touch_controls=true
	player.set_character(0); character_choice=0; aim_direction=Vector3.FORWARD; player.set_aim(aim_direction)
	var pickup_kinds: Array=["grenade","flashbang","launcher","fire_round"]
	var pickup_positions: Array=[Vector3(-2.1,0,-2.0),Vector3(2.1,0,-2.8),Vector3(-1.9,0,-7.0),Vector3(1.9,0,-7.8)]
	for i in range(pickup_kinds.size()):
		_spawn_pickup(pickup_kinds[i],pickup_positions[i].z); pickups[-1].position=pickup_positions[i]
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/pickups.png")
	for pickup in pickups:
		if is_instance_valid(pickup): pickup.queue_free()
	pickups.clear()
	player.set_weapon("LAUNCHER"); player.fire_ammo=4; player.fire_mode=true
	await get_tree().create_timer(0.12).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/launcher-held.png")
	hud.visible=false; state="menu"; camera.position=Vector3(2.8,2.35,8.0); camera.look_at(player.position+Vector3(0,1.05,0))
	await get_tree().create_timer(0.08).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/launcher-closeup.png")
	hud.visible=true; state="playing"; camera.position=Vector3(0,6.4,13.5); camera.look_at(Vector3(0,1.0,-8))
	assert(_fire_launcher())
	await get_tree().create_timer(0.10).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/launcher-projectile.png")
	start_run(); _clear_world(); state="playing"; shot_timer=999; hint_time=0; touch_controls=false
	_spawn_zombie(-6); zombies[-1].position.x=0
	_spawn_ordnance("frag",zombies[-1].position+Vector3(0,0.5,0),Vector3.ZERO).fuse=0.025
	await get_tree().create_timer(0.07).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/frag-explosion.png")
	start_run(); _clear_world(); state="playing"; shot_timer=999; hint_time=0; touch_controls=false
	_spawn_zombie(-6); zombies[-1].position.x=0
	_spawn_ordnance("flash",zombies[-1].position+Vector3(0,0.6,0),Vector3.ZERO).fuse=0.025
	await get_tree().create_timer(0.07).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/flash-detonation.png")
	start_run(); _clear_world(); state="playing"; shot_timer=999; hint_time=0; touch_controls=false
	_spawn_zombie(-6); zombies[-1].position.x=0; zombies[-1].health=200
	_spawn_ordnance("fire",zombies[-1].position+Vector3(0,0.5,0),Vector3.ZERO).fuse=0.025
	await get_tree().create_timer(0.07).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/ordnance/fire-detonation.png")
	start_run(); _clear_world(); state="playing"; shot_timer=999; spawn_timer=999; hint_time=0; touch_controls=false
	await get_tree().create_timer(3.4).timeout
	player.position.x=-2.8; player.target_x=-2.8
	_spawn_zombie(-7,"jockey"); zombies[-1].position.x=-1.9
	_spawn_zombie(-10,"banshee"); zombies[-1].position.x=1.8
	_spawn_zombie(-8,"walker"); zombies[-1].position.x=0.2
	var capture_banshee=zombies[1]; var capture_walker=zombies[2]
	capture_walker.position.x=capture_banshee.position.x-0.8; capture_banshee.banshee_pulse_timer=0.0
	_tick_zombies(0.05)
	await get_tree().create_timer(0.18).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/monsters/gameplay-specials.png")
	player.health=0; _end_run()
	await get_tree().create_timer(0.10).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/monsters/gameover-revival.png")
	start_run(); _begin_intro(); shot_timer=999; hint_time=0; touch_controls=false
	await get_tree().create_timer(0.65).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/intro/intro-horde.png")
	await get_tree().create_timer(1.55).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/intro/intro-turn.png")
	await get_tree().create_timer(1.65).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://diagnostics/intro/intro-chase.png")
	_finish_intro()
	print("CAPTURE_3D_SAVED menu shop languages gameplay armor blood explosion ordnance specials revival intro")
	get_tree().quit()

func _smoke_test() -> void:
	meta_upgrades=ShopCatalog.default_levels(); bank_coins=0
	assert(Localization.LANGUAGES.size()==20)
	assert(sound.streams.get("explosion")!=null and sound.streams.get("zombie")!=null)
	assert(sound.streams.get("smg")!=null and sound.streams["smg"].get_length()>0.2)
	_pointer_down(Vector2(270,840)); assert(state in ["intro","playing"])
	_clear_world(); enter_lobby(); assert(state=="character_select")
	_pointer_down(Vector2(60,LOBBY_TOP+LOBBY_STEP+50)); assert(character_choice==1 and player.character==1)
	_pointer_down(Vector2(60,LOBBY_TOP+50)); assert(character_choice==0 and player.character==0)
	_pointer_down(Vector2(394,470)); assert(character_choice==1)
	_pointer_down(Vector2(146,470)); assert(character_choice==0)
	await get_tree().process_frame; assert(lobby.visible and is_instance_valid(lobby.actor))
	state="menu"
	_pointer_down(Vector2(490,45)); assert(state=="settings")
	var old_muted: bool=sound.muted; _pointer_down(Vector2(270,250)); assert(sound.muted!=old_muted)
	_pointer_down(Vector2(270,840)); assert(state=="menu")
	var skeleton:=player.model.find_child("Skeleton3D",true,false) as Skeleton3D
	assert(is_instance_valid(skeleton) and skeleton.get_bone_count()>=15)
	open_shop(); assert(state=="shop" and shop_truck.visible); bank_coins=100; assert(buy_item("medical")); assert(bank_coins==60)
	select_shop_item(4); assert(shop_items[shop_index].id=="w_shotgun" and shop_truck.focus_id=="w_shotgun")
	bank_coins=200; assert(buy_item("w_shotgun")); player.apply_meta(meta_upgrades); player.set_weapon("SHOTGUN"); assert(is_equal_approx(player.damage,30.0*player.damage_scale*1.12))
	meta_upgrades["w_shotgun"]=0
	open_lootbox(); assert(state=="lootbox"); close_lootbox(); assert(state=="shop")
	for code in ["en","zh_CN","ja","ar","th"]: assert(ShopText.text(code,"n_shotgun")!="n_shotgun")
	close_shop(); start_run(); assert(state=="playing" and player.health==115)
	touch_controls=true; right_stick=Vector2.ZERO; assert(_wants_to_fire()); touch_controls=false
	var old: float=player.damage; player.apply_upgrade("damage"); assert(player.damage>old)
	player.target_x=100; await get_tree().create_timer(0.2).timeout; assert(player.position.x<=3.15)
	player.apply_upgrade("smg"); assert(player.weapon=="SMG" and player.ammo==36)
	var before: int=player.ammo; assert(_fire()); assert(player.ammo==before-1 and bullets.size()>0 and sound.last_id=="smg")
	player.apply_upgrade("shotgun"); assert(player.weapon=="SHOTGUN" and player.projectile_count==7)
	var old_bullets: int=bullets.size(); assert(_fire()); assert(bullets.size()==old_bullets+7 and sound.last_id=="shotgun")
	player.apply_upgrade("pistol"); _spawn_zombie(-20); aim_target=zombies[-1]; aim_point=aim_target.position+Vector3(0,1,0)
	assert(_fire() and sound.last_id=="pistol_far")
	aim_target.position=player.position+Vector3(0,0,-6); assert(_fire() and sound.last_id=="pistol_near")
	player.apply_upgrade("sniper"); assert(player.weapon=="SNIPER" and player.magazine_size==5 and player.pierce==2)
	auto_reload=false; player.ammo=0; assert(request_reload()); assert(player.reloading)
	assert(player.animation_player.current_animation=="Reload_Gun" and player.animation_player.is_playing())
	await get_tree().create_timer(player.reload_duration+0.15).timeout; assert(not player.reloading and player.ammo>0)
	assert(player.animation_player.current_animation=="Run_Gun" and player.animation_player.is_playing())
	for weapon_id in ["PISTOL","SMG","SHOTGUN","SNIPER","RIFLE","LAUNCHER"]:
		player.set_weapon(weapon_id); player.ammo-=1
		assert(player.request_reload() and player.animation_player.current_animation=="Reload_Gun")
		player.finish_reload(); assert(player.animation_player.current_animation=="Run_Gun")
	_spawn_gate(); assert(gates.size()==1 and gates[0].left.id=="damage" and gates[0].right.id=="rate")
	state="playing"; player.set_weapon("SMG"); player.ammo=5; player.reserve_ammo=10
	assert(swap_weapon() and player.weapon=="PISTOL" and player.swap_target()=="SMG")
	assert(swap_weapon() and player.weapon=="SMG" and player.ammo==5 and player.reserve_ammo==10)
	print("SMOKE_SWAP_OK")
	# Weapon crates: weapons now only come from shooting crates down to 0.
	player.set_weapon("RIFLE")
	var crate:=WeaponCrateScript.new(); crate.setup("SHOTGUN",3); crate.position=Vector3(1.5,0,player.position.z-6); add_child(crate); crates.append(crate)
	await get_tree().process_frame
	assert(crate.counter.text=="3" and crate.bullet_hits(crate.position+Vector3(0,0.5,0.4)))
	assert(not crate.take_hit(1) and crate.counter.text=="2")
	crate.take_hit(1); assert(crate.take_hit(1) and crate.broken); _break_crate(crate)
	for step in range(40): _tick_crates(0.02)
	assert(player.weapon=="SHOTGUN" and not crates.has(crate))
	print("SMOKE_CRATE_OK")
	_spawn_barrel(); var collision_barrel=barrels[-1]; collision_barrel.position=player.position+Vector3(0,0,-0.2)
	_resolve_barrel_collision(); assert(_flat_distance(player.position,collision_barrel.position)>=collision_barrel.radius+0.39)
	collision_barrel.position=Vector3(0,0,-4); await get_tree().process_frame
	mouse_position=camera.unproject_position(collision_barrel.global_position+Vector3(0,collision_barrel.height*0.5,0)); _update_mouse_aim()
	assert(aim_target==collision_barrel and barrels.has(aim_target))
	_spawn_zombie(-6); var avoidance_zombie=zombies[-1]
	avoidance_zombie.position=collision_barrel.position+Vector3(0,0,-1.0)
	for step in range(120):
		avoidance_zombie.tick(1.0/60.0); _avoid_barrels(avoidance_zombie,1.0/60.0)
		assert(_flat_distance(avoidance_zombie.position,collision_barrel.position)>=avoidance_zombie.radius+collision_barrel.radius-0.001)
	zombies.erase(avoidance_zombie); avoidance_zombie.queue_free()
	var health_before_obstacle: float=player.health
	var collision_car=_spawn_obstacle("car",player.position.x,player.position.z)
	_tick_obstacles(0.0)
	assert(player.health<health_before_obstacle and not collision_car.overlaps(player.position))
	obstacles.erase(collision_car); collision_car.queue_free()
	var collision_fence=_spawn_obstacle("fence",player.position.x,player.position.z)
	_tick_obstacles(0.0)
	assert(not collision_fence.overlaps(player.position))
	obstacles.erase(collision_fence); collision_fence.queue_free()
	collision_car=_spawn_obstacle("car",0.0,-6.0)
	_spawn_zombie(-8.0); var road_zombie=zombies[-1]; road_zombie.position.x=0.0
	for step in range(120):
		road_zombie.tick(1.0/60.0); _avoid_obstacles(road_zombie,1.0/60.0)
		assert(not collision_car.overlaps(road_zombie.position,road_zombie.radius))
	zombies.erase(road_zombie); road_zombie.queue_free()
	obstacles.erase(collision_car); collision_car.queue_free()
	player.reserve_ammo=0; _spawn_pickup("ammo",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01); assert(player.reserve_ammo>0)
	player.health=50; _spawn_pickup("medkit",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01); assert(player.health==85)
	_spawn_pickup("armor",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01)
	assert(player.has_armor and not player.has_helmet and is_instance_valid(player.armor_model))
	_spawn_pickup("helmet",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01)
	assert(player.has_armor and player.has_helmet and is_instance_valid(player.helmet_model))
	# Every ordnance pickup must change real inventory or equip the new weapon.
	player.grenade_count=0; _spawn_pickup("grenade",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01); assert(player.grenade_count==2)
	player.flashbang_count=0; _spawn_pickup("flashbang",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01); assert(player.flashbang_count==1)
	_spawn_pickup("launcher",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01); assert(player.weapon=="LAUNCHER" and player.magazine_size==4)
	player.fire_ammo=0; _spawn_pickup("fire_round",player.position.z); pickups[-1].position.x=player.position.x; _tick_pickups(0.01); assert(player.fire_ammo==4)
	touch_controls=true; assert(_pointer_down(BTN_FIRE_MODE) and player.fire_mode)
	var old_ordnance: int=ordnance.size(); var old_fire_ammo: int=player.fire_ammo
	assert(_fire() and ordnance.size()==old_ordnance+1 and ordnance[-1].kind=="fire" and player.fire_ammo==old_fire_ammo-1)
	player.fire_ammo=1; player.fire_mode=true; assert(_fire()); assert(player.fire_ammo==0 and not player.fire_mode)
	old_ordnance=ordnance.size(); assert(_fire() and ordnance.size()==old_ordnance+1 and ordnance[-1].kind=="launcher")
	assert(_pointer_down(BTN_FRAG) and player.grenade_count==1)
	_spawn_zombie(-10); var frag_target=zombies[-1]; frag_target.position.x=0
	var frag_expected: int=maxi(1,roundi(frag_target.health))
	var frag_projectile=ordnance[-1]; frag_projectile.position=frag_target.position+Vector3(0,0.4,0); frag_projectile.velocity=Vector3.ZERO; frag_projectile.fuse=0
	_tick_ordnance(0.0); assert(not zombies.has(frag_target))
	var frag_number_found:=false
	for effect in effects:
		if is_instance_valid(effect.label) and effect.label.text=="-%d"%frag_expected: frag_number_found=true
	assert(frag_number_found)
	assert(_pointer_down(BTN_FLASH) and player.flashbang_count==0)
	_spawn_zombie(-9); var flash_target=zombies[-1]; flash_target.position.x=2.4
	var flash_projectile=ordnance[-1]; flash_projectile.position=flash_target.position+Vector3(0,0.5,0); flash_projectile.velocity=Vector3.ZERO; flash_projectile.fuse=0
	_tick_ordnance(0.0); assert(flash_target.stun_timer>=3.9 and not flash_target.dead)
	player.fire_ammo=1; player.fire_mode=true; assert(_fire())
	_spawn_zombie(-11); var burn_target=zombies[-1]; burn_target.position.x=-2.4; burn_target.health=200.0
	var fire_projectile=ordnance[-1]; fire_projectile.position=burn_target.position+Vector3(0,0.5,0); fire_projectile.velocity=Vector3.ZERO; fire_projectile.fuse=0
	_tick_ordnance(0.0); assert(burn_target.burn_timer>=4.9 and is_equal_approx(burn_target.burn_dps,24.0))
	var burned_health: float=burn_target.health; burn_target.health=5.0; _tick_zombies(0.25); assert(burned_health>5.0 and not zombies.has(burn_target))
	var burn_number_found:=false
	for effect in effects:
		if is_instance_valid(effect.label) and effect.label.text=="-5": burn_number_found=true
	assert(burn_number_found)
	touch_controls=false; player.set_weapon("PISTOL")
	for projectile in ordnance:
		if is_instance_valid(projectile): projectile.queue_free()
	ordnance.clear()
	player.health=100; player.take_damage(25); assert(is_equal_approx(player.health,80.0))
	_spawn_zombie(-8); var test_z=zombies[-1]; test_z.position.x=0
	assert(_body_part(test_z,test_z.position+Vector3(0,1.8,0))=="head")
	assert(_body_part(test_z,test_z.position+Vector3(-0.17,0.5,0))=="leg_l")
	_hit_zombie(test_z,20,"torso",test_z.position+Vector3(0,1.0,0))
	var bullet_number_found:=false
	for effect in effects:
		if is_instance_valid(effect.label) and effect.label.text=="-20": bullet_number_found=true
	assert(bullet_number_found)
	var effect_count:=effects.size(); _hit_zombie(test_z,1000,"head",test_z.position+Vector3(0,1.8,0)); assert(effects.size()>effect_count+15)
	player.health=player.max_health; _spawn_barrel(); barrels[-1].position=player.position+Vector3(0,0,-1); _explode(barrels[-1])
	assert(is_equal_approx(player.health,player.max_health*0.28))
	player.set_armor(false); player.set_helmet(false); player.health=player.max_health; _spawn_barrel(); barrels[-1].position=player.position+Vector3(0,0,-1); _explode(barrels[-1]); assert(player.health==0)
	var custom_explosion_found:=false
	for effect in effects:
		if effect.get_script()==ExplosionScript: custom_explosion_found=true
	assert(custom_explosion_found)
	run_coins=3; distance=160; var old_bank: int=bank_coins; _end_run(); assert(last_reward==5 and bank_coins==old_bank+5)
	assert(request_revival() and state=="gameover" and revive_pending)
	await get_tree().create_timer(0.55).timeout
	assert(state=="playing" and revive_used and player.health==player.max_health*0.5)
	var protected_health: float=player.health; _hurt_player(20); assert(player.health==protected_health)
	_revive_after_reward(); assert(state=="playing" and player.health==protected_health)
	run_coins=5; distance=240; player.health=0; _end_run()
	assert(last_reward==8 and bank_coins==old_bank+8)
	_revive_after_reward(); assert(state=="gameover" and bank_coins==old_bank+8)
	start_run(); _clear_world(); state="playing"; shot_timer=999; player.health=player.max_health
	run_time=37.0; jockey_introduced=true; banshee_introduced=false; _spawn_zombie()
	var automatic_banshee=zombies[-1]
	assert(automatic_banshee.kind=="banshee" and automatic_banshee.position.z>=-30.0 and banshee_warning>0.0)
	zombies.erase(automatic_banshee); automatic_banshee.queue_free()
	_spawn_zombie(-16,"jockey"); var jockey=zombies[-1]
	assert(jockey.animation_player.current_animation=="Jockey_Quad_Run" and jockey.speed>7.0)
	_spawn_zombie(-18,"banshee"); var banshee=zombies[-1]
	assert(banshee.animation_player.current_animation=="Banshee_Walk" and banshee.flames.emitting)
	_spawn_zombie(-14,"walker"); var frenzy=zombies[-1]; frenzy.position.x=banshee.position.x
	banshee.banshee_pulse_timer=0.0
	_tick_zombies(0.1)
	var old_frenzy_z: float=frenzy.position.z
	_tick_zombies(0.1)
	assert(frenzy.burn_timer>5.0 and frenzy.frenzy_timer>4.5 and frenzy.flames.emitting)
	assert(frenzy.position.z-old_frenzy_z>frenzy.speed*0.15)
	assert(banshee.burn_timer==0.0 and banshee.flames.emitting)
	_begin_intro(); assert(state=="intro" and zombies.size()==9 and intro_horde_offsets.size()==9 and (is_instance_valid(chaser) or not ResourceLoader.exists(BossChaserScript.MODEL_PATH)))
	assert(player.animation_player.current_animation=="Run_Gun" and player.animation_player.is_playing())
	_tick_intro(0.5); assert(is_equal_approx(intro_time,0.5) and camera.fov==50.0)
	_finish_intro(); assert(state=="playing" and zombies.size()==2 and intro_horde_offsets.is_empty())
	_begin_intro(); assert(_pointer_down(Vector2(270,480)) and state=="playing" and zombies.size()==2)
	_begin_intro()
	var skip_key:=InputEventKey.new(); skip_key.keycode=KEY_SPACE; skip_key.pressed=true
	_unhandled_input(skip_key); assert(state=="playing" and zombies.size()==2)
	print("SMOKE_3D_OK languages=20 settings=true character_select=true shop=true rewards=true weapons=true reload=true armor=true helmet=true helmet_protection=true barrel_collision=true barrel_aim=true ordnance=true damage_numbers=true audio=true jockey=true banshee=true fire_frenzy=true revival=true revival_rewards=true intro=true")
	_clear_world(); await get_tree().process_frame; await get_tree().process_frame; get_tree().quit()

func _soak_test() -> void:
	start_run(); player.apply_upgrade("smg"); player.damage=180; player.fire_interval=0.07; player.projectile_count=3; player.reserve_ammo=99999; auto_reload=true
	for frame in range(2100):
		player.health=100; player.target_x=sin(frame/95.0)*2.7; aim_direction=Vector3(sin(frame/130.0)*0.2,0,-1).normalized(); await get_tree().process_frame
	assert(run_time>30 and wave>=2 and kills>10 and new_gate_index>=2)
	print("SOAK_3D_OK time=",snappedf(run_time,0.1)," kills=",kills," gates=",new_gate_index," coins=",run_coins," actors=",zombies.size()+bullets.size()+effects.size())
	_clear_world(); await get_tree().process_frame; await get_tree().process_frame; get_tree().quit()
