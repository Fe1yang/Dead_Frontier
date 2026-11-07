extends Node3D
const ModelFix=preload("res://scripts/model_fix.gd")

const AnimLibrary=preload("res://scripts/anim_library.gd")
## Jockey runs on all fours: its gallop clip is tipped forward about the hips and lowered so
## hands and feet strike the ground like an animal (the raw clip hovers in a crouch).
const JOCKEY_LEAN_DEG:=27.0
const JOCKEY_DROP:=-0.12
## The juggernaut is a hulking brute: scaled up and walking upright instead of the zombie shamble.
const BRUTE_SCALE:=1.42
const BRUTE_ARM_BONES:=["clavicle_l","upperarm_l","lowerarm_l","hand_l","clavicle_r","upperarm_r","lowerarm_r","hand_r"]

var kind := "walker"
var health := 40.0
var max_health := 40.0
var speed := 3.7
var damage := 18.0
var reward := 1
var radius := 0.42
var age := 0.0
var hit_flash := 0.0
var stun_timer := 0.0
var burn_timer := 0.0
var burn_dps := 0.0
var burn_damage_accumulated := 0.0
var burn_number_timer := 0.0
var frenzy_timer := 0.0
var banshee_pulse_timer := 0.0
var banshee_pulse_ready := false
var banshee_time := 0.0
var banshee_ground_speed := 2.0 # how fast she is walking backwards over the road (for the anim)
var dead := false
var model: Node3D
var animation_player: AnimationPlayer
var meshes: Array[MeshInstance3D] = []
var bar: MeshInstance3D
var bar_fill: MeshInstance3D
var flash_material: StandardMaterial3D
var flames: CPUParticles3D
var embers: CPUParticles3D

func configure(type: String, difficulty: float) -> void:
	kind = type
	match kind:
		"runner": health=26*difficulty; speed=5.2+difficulty*0.15; damage=14; reward=2; radius=0.36
		"brute": health=150*difficulty; speed=5.6+difficulty*0.10; damage=32; reward=5; radius=0.80
		# The bomber waddles in slow and fat; it never swings, it detonates.
		"bomber","bomber_female": health=120*difficulty; speed=4.4+difficulty*0.08; damage=30; reward=6; radius=0.66
		"jockey": health=68*difficulty; speed=7.4+difficulty*0.16; damage=22; reward=3; radius=0.48
		"banshee": health=210*difficulty; speed=1.65+difficulty*0.05; damage=28; reward=8; radius=0.46
		_: health=44*difficulty; speed=3.65+difficulty*0.1; damage=18; reward=1
	max_health = health
	age = randf()*4
	banshee_pulse_timer = 2.8 if kind=="banshee" else 0.0
	var assets := {
		"walker": "zombie_walker_universal.glb",
		"runner": "zombie_female_universal.glb",
		"brute": "zombie_juggernaut_universal.glb",
		"jockey": "zombie_jockey_universal.glb",
		"banshee": "zombie_banshee_universal.glb",
		"bomber": "zombie_bomber_universal.glb",
		"bomber_female": "zombie_bomber_female_universal.glb"
	}
	var asset: String="res://assets/models/actors/"+assets.get(kind,"zombie_walker_universal.glb")
	if not ResourceLoader.exists(asset): asset="res://assets/models/actors/zombie_walker_universal.glb" # bomber models land later
	model = load(asset).instantiate()
	# The jockey rig is authored facing -Z; turn it so its head leads toward the player.
	# Bomber is already authored facing +Z (toward the player): no rotation.
	if kind=="jockey": model.rotation.y=PI
	if kind=="brute": model.scale*=BRUTE_SCALE
	add_child(model)
	ModelFix.double_sided(model)
	_collect(model)
	animation_player=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	var clip_name := "Zombie_Walk_Fwd"
	if kind=="brute" or kind.begins_with("bomber"):
		# The juggernaut/bomber are hulking heavies: they borrow the upright UAL1 "Walk" instead
		# of the zombie shamble, with the arm tracks stripped and the arm bones pinned to the
		# bind pose. The juggernaut's arm geometry is skinned mostly to the torso, and the
		# bomber's belly is so huge that arms-down walk poses would bury the arms inside it —
		# pinning holds the arms out to the sides, Boomer-style, so they stay visible.
		var borrowed:=AnimLibrary.borrow(animation_player,"Walk","ual1",{},BRUTE_ARM_BONES)
		AnimLibrary.pin_to_bind_pose(model,BRUTE_ARM_BONES)
		if borrowed!="": clip_name=borrowed
	if kind=="jockey": clip_name="Jockey_Quad_Run"
	elif kind=="banshee": clip_name="Banshee_Walk"
	if animation_player and animation_player.has_animation(clip_name):
		var clip:=animation_player.get_animation(clip_name)
		clip.loop_mode=Animation.LOOP_LINEAR
		var rate:=randf_range(0.86,1.12)
		match kind:
			"runner": rate=randf_range(1.42,1.62)
			"brute": rate=_brute_stride_rate()
			"bomber": rate=_brute_stride_rate()
			"bomber_female": rate=_brute_stride_rate()
			"jockey": rate=randf_range(1.18,1.30)
			"banshee": rate=0.72
		animation_player.speed_scale=rate
		animation_player.play(clip_name)
		animation_player.seek(randf()*clip.length,true)
	else:
		push_error("Zombie animation missing: "+clip_name+" in "+asset)
	if kind=="jockey":
		var hip:=Vector3(0,0.53,0)
		var lean:=Basis(Vector3.RIGHT,deg_to_rad(JOCKEY_LEAN_DEG))
		model.transform=Transform3D(lean*model.basis,hip-lean*hip+Vector3(0,JOCKEY_DROP,0))
	flash_material = StandardMaterial3D.new()
	flash_material.albedo_color = Color(1,0.95,0.75,0.7)
	flash_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	flash_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_make_health_bar()
	_make_fire()

func _collect(node: Node) -> void:
	if node is MeshInstance3D: meshes.append(node)
	for child in node.get_children(): _collect(child)

func _make_health_bar() -> void:
	bar = _quad(0.84,0.075,Color(0.02,0.035,0.025,0.9))
	bar_fill = _quad(0.78,0.045,Color("c9f54a"))
	var height:=2.35*BRUTE_SCALE+0.1 if kind=="brute" else 2.15
	if kind=="banshee": height=2.72
	elif kind=="jockey": height=1.20
	bar.position = Vector3(0,height,0)
	bar_fill.position = bar.position+Vector3(0,0,0.012)
	add_child(bar); add_child(bar_fill)
	bar.visible = kind in ["brute","banshee"] or kind.begins_with("bomber"); bar_fill.visible = bar.visible
	# No bile sacs: user rejected the yellow-white pustules as ugly. Bomber reads via
	# silhouette + health bar only.

## Glowing bile sacs across the gut: the visual warning that this one explodes.
var pustule_mat: StandardMaterial3D
func _make_pustules() -> void:
	pustule_mat=StandardMaterial3D.new()
	pustule_mat.albedo_color=Color("d8e34a"); pustule_mat.emission_enabled=true
	pustule_mat.emission=Color("c6e04a"); pustule_mat.emission_energy_multiplier=1.6
	var spots:=[[-0.16,1.02,0.30,0.085],[0.10,1.12,0.32,0.11],[0.22,0.92,0.24,0.07],[-0.02,0.86,0.33,0.095],[0.05,1.26,0.24,0.06],[-0.24,1.18,0.18,0.06]]
	for s in spots:
		var pust:=MeshInstance3D.new()
		var sm:=SphereMesh.new(); sm.radius=0.5; sm.height=1.0; sm.radial_segments=10; sm.rings=6
		pust.mesh=sm; pust.position=Vector3(s[0],s[1],s[2]); pust.scale=Vector3.ONE*s[3]*2.0
		pust.material_override=pustule_mat; pust.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(pust)

func _quad(w: float,h: float,color: Color) -> MeshInstance3D:
	var n := MeshInstance3D.new()
	var mesh := QuadMesh.new(); mesh.size=Vector2(w,h); n.mesh=mesh
	var m := StandardMaterial3D.new(); m.albedo_color=color; m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode=BaseMaterial3D.BILLBOARD_ENABLED; m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	n.material_override=m
	return n

func _particle_material() -> StandardMaterial3D:
	var m:=StandardMaterial3D.new()
	m.vertex_color_use_as_albedo=true
	m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode=BaseMaterial3D.BILLBOARD_ENABLED
	return m

func _fire_gradient() -> Gradient:
	var gradient:=Gradient.new()
	gradient.set_color(0,Color(1.0,0.86,0.28,0.72))
	gradient.set_color(1,Color(1.0,0.12,0.015,0.0))
	gradient.add_point(0.38,Color(1.0,0.38,0.025,0.62))
	return gradient

func _make_fire() -> void:
	flames=CPUParticles3D.new()
	flames.amount=18 if kind=="banshee" else 16
	flames.lifetime=0.48
	flames.preprocess=0.30
	flames.emission_shape=CPUParticles3D.EMISSION_SHAPE_SPHERE
	flames.emission_sphere_radius=0.24
	flames.direction=Vector3.UP
	flames.spread=28.0
	flames.gravity=Vector3(0,0.85,0)
	flames.initial_velocity_min=0.25
	flames.initial_velocity_max=0.62
	flames.scale_amount_min=0.65
	flames.scale_amount_max=1.25
	flames.color_ramp=_fire_gradient()
	var quad:=QuadMesh.new(); quad.size=Vector2(0.28,0.48)
	var flame_material:=_particle_material()
	flame_material.albedo_texture=load("res://assets/vfx/flame_particle.png")
	quad.material=flame_material; flames.mesh=quad
	flames.position=Vector3(0,0.94 if kind!="jockey" else 0.48,0)
	flames.emitting=kind=="banshee"
	add_child(flames)
	embers=CPUParticles3D.new()
	embers.amount=8; embers.lifetime=0.75; embers.preprocess=0.35
	embers.emission_shape=CPUParticles3D.EMISSION_SHAPE_SPHERE; embers.emission_sphere_radius=0.30
	embers.direction=Vector3.UP; embers.spread=48; embers.gravity=Vector3(0,0.55,0)
	embers.initial_velocity_min=0.45; embers.initial_velocity_max=0.95
	embers.scale_amount_min=0.65; embers.scale_amount_max=1.25
	embers.color=Color("ff9b35")
	var spark:=SphereMesh.new(); spark.radius=0.025; spark.height=0.05; spark.radial_segments=6; spark.rings=3
	spark.material=_particle_material(); embers.mesh=spark
	embers.position=flames.position; embers.emitting=flames.emitting
	add_child(embers)

func ignite(duration: float,dps: float,frenzy_duration: float=0.0) -> void:
	if dead: return
	burn_timer=maxf(burn_timer,duration)
	burn_dps=maxf(burn_dps,dps)
	frenzy_timer=maxf(frenzy_timer,frenzy_duration)
	if is_instance_valid(flames): flames.emitting=true
	if is_instance_valid(embers): embers.emitting=true

## The road scrolls toward the player at 3.5 m/s, so a zombie's walk over the ground is
## speed-3.5. The juggernaut's walk clip (scaled up with the model) covers ~2 m/s at rate 1.0,
## so the feet keep pace with the ground instead of sliding.
func _brute_stride_rate() -> float:
	return clampf((speed-3.5)/2.0,0.8,1.4)

func collision_height() -> float:
	match kind:
		"brute": return 2.35*BRUTE_SCALE
		"banshee": return 2.60
		"jockey": return 1.30
		_: return 2.02

func tick(delta: float) -> void:
	if dead: return
	age += delta
	stun_timer = maxf(0.0, stun_timer-delta)
	burn_timer = maxf(0.0, burn_timer-delta)
	frenzy_timer = maxf(0.0, frenzy_timer-delta)
	burn_number_timer = maxf(0.0, burn_number_timer-delta)
	banshee_pulse_ready=false
	if kind=="banshee":
		banshee_pulse_timer-=delta
		if banshee_pulse_timer<=0.0:
			banshee_pulse_ready=true
			banshee_pulse_timer=4.6
	if burn_timer>0.0:
		var burn_damage: float=minf(health,burn_dps*delta)
		burn_damage_accumulated+=burn_damage
		take_hit(burn_dps*delta)
		hit_flash=0.0
	var frenzy:=frenzy_timer>0.0
	var move_scale := 0.12 if stun_timer>0.0 else (1.68 if frenzy else 1.0)
	if kind=="banshee":
		_banshee_move(delta,move_scale)
	else:
		position.z += speed*move_scale*delta
	hit_flash=maxf(0,hit_flash-delta)
	for mesh in meshes: mesh.material_overlay=flash_material if hit_flash>0 else null
	if is_instance_valid(animation_player):
		var base_rate:=speed/3.7
		if kind=="jockey": base_rate=1.22
		elif kind=="brute" or kind.begins_with("bomber"): base_rate=_brute_stride_rate()
		elif kind=="banshee": base_rate=clampf(banshee_ground_speed/2.3,0.6,1.7)
		animation_player.speed_scale = 0.0 if stun_timer>0.0 else maxf(0.55,base_rate*(1.30 if frenzy else 1.0))

	if is_instance_valid(flames): flames.emitting=burn_timer>0.0 or kind=="banshee"
	if is_instance_valid(embers): embers.emitting=flames.emitting
	bar.visible=kind in ["brute","banshee"] or kind.begins_with("bomber") or health<max_health
	bar_fill.visible=bar.visible
	bar_fill.scale.x=clampf(health/max_health,0,1)
	# (bile sacs removed — no pustule throb)

## The Banshee keeps her distance: she walks backwards ahead of the survivor as fast as the
## survivor runs, drifting closer and further (roughly 9-19 m ahead), so she can't be outrun
## and has to be shot down.
const BANSHEE_HOLD_Z := -14.0
const BANSHEE_SWAY := 5.0
func _banshee_move(delta: float,move_scale: float) -> void:
	banshee_time+=delta
	# The longer she lives the closer she stalks (from ~14 m down to ~7 m ahead), so she can't
	# hide behind the horde for ever.
	var close_in:=clampf(banshee_time/22.0,0.0,1.0)
	var target:=lerpf(BANSHEE_HOLD_Z,-7.0,close_in)+sin(banshee_time*0.75)*BANSHEE_SWAY*lerpf(1.0,0.45,close_in)
	var old_z:=position.z
	if position.z<target-0.3:
		position.z=minf(target,position.z+3.2*move_scale*delta) # still coming in from the distance
	else:
		position.z=move_toward(position.z,target,2.4*delta)
	# The road scrolls towards the survivor at 3.5 m/s; whatever she doesn't move in z she walks backwards.
	banshee_ground_speed=maxf(0.0,3.5-(position.z-old_z)/maxf(delta,0.0001))

func consume_banshee_pulse() -> bool:
	if not banshee_pulse_ready or dead: return false
	banshee_pulse_ready=false
	return true

func consume_burn_damage_number() -> float:
	if burn_damage_accumulated<=0.0: return 0.0
	if burn_number_timer>0.0 and burn_timer>0.0 and not dead: return 0.0
	var amount: float=burn_damage_accumulated
	burn_damage_accumulated=0.0
	burn_number_timer=0.35
	return amount

func take_hit(amount: float) -> bool:
	if dead: return true
	health-=amount; hit_flash=0.07
	if health<=0: dead=true
	return dead
