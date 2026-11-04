extends Node3D

const GunGripIK=preload("res://scripts/gun_grip_ik.gd")

var health := 100.0
var max_health := 100.0
var damage := 24.0
var fire_interval := 0.24
var projectile_count := 1
var gun_level := 1
var scrap := 0
var target_x := 0.0
var weapon := "PISTOL"
var ammo := 12
var reserve_ammo := 72
var magazine_size := 12
var reload_duration := 1.10
var reload_timer := 0.0
var reloading := false
var bullet_speed := 30.0
var pierce := 0
var grenade_count := 2
var flashbang_count := 1
var fire_ammo := 0
var fire_mode := false
var damage_scale := 1.0
var rate_scale := 1.0
var split_bonus := 0          # extra bullets from gates, kept when changing guns
var stowed: Dictionary = {}
var hand_anchor: BoneAttachment3D   # the main gun while the pistol is out: id, ammo, reserve
var weapon_levels: Dictionary = {} # shop upgrade level per weapon id
var model: Node3D
var weapon_model: Node3D
var armor_model: Node3D
var helmet_model: Node3D
var helmet_attachment: BoneAttachment3D
var skeleton: Skeleton3D
var animation_player: AnimationPlayer
var right_hand := -1
var grip: SkeletonModifier3D # straight-arm two-hand stance (see gun_grip_ik.gd)
var has_armor := false
var has_helmet := false
var character := 0
var legs: Array[Node3D] = []
var walk_time := 0.0
var flash_time := 0.0
var hurt_flash := 0.0
var aim_direction := Vector3.FORWARD
var light: OmniLight3D
var flash: Node3D

const GRIP_OFFSETS := {
	"PISTOL": Vector3(0.0,0.20,0.10),
	"SMG": Vector3(0.0,0.23,0.20),
	"SHOTGUN": Vector3(0.0,0.12,0.12),
	"SNIPER": Vector3(0.0,0.13,0.15),
	"RIFLE": Vector3(0.0,0.20,0.15),
	"LAUNCHER": Vector3(0.0,0.16,0.16),
}
const HOLD_DROP := {"PISTOL":0.10,"SMG":0.10,"SHOTGUN":0.10,"SNIPER":0.10,"RIFLE":0.10,"LAUNCHER":0.10}
const SUPPORT_REACH := {"PISTOL":0.03,"SMG":0.16,"SHOTGUN":0.22,"SNIPER":0.24,"RIFLE":0.20,"LAUNCHER":0.14}
const MUZZLE_POINTS := {
	"PISTOL": Vector3(0.0,0.137,0.40),
	"SMG": Vector3(0.0,0.085,0.90),
	"SHOTGUN": Vector3(0.0,0.10,1.19),
	"SNIPER": Vector3(0.0,0.075,1.45),
	"RIFLE": Vector3(0.0,0.10,1.05),
	"LAUNCHER": Vector3(0.0,0.115,0.48),
}
const WEAPON_SCALES := {
	"PISTOL": 0.45,
	"SMG": 0.50,
	"SHOTGUN": 0.52,
	"SNIPER": 0.50,
	"RIFLE": 0.50,
	"LAUNCHER": 0.90,
}
const FLASH_SCENES := {
	"PISTOL": "short_flash/short_flash_01.tscn",
	"SMG": "muzzle_flash/muzzle_flash_02.tscn",
	"SHOTGUN": "wide_flash/wide_flash_03.tscn",
	"SNIPER": "big_flash/big_flash_04.tscn",
	"RIFLE": "muzzle_flash/muzzle_flash_01.tscn",
	"LAUNCHER": "wide_flash/wide_flash_03.tscn",
}
const FLASH_SCALES := {"PISTOL":0.20,"SMG":0.18,"SHOTGUN":0.25,"SNIPER":0.28,"RIFLE":0.20,"LAUNCHER":0.28}

func _ready() -> void:
	_load_character()
	light = OmniLight3D.new()
	light.light_color = Color("ff9b55")
	light.omni_range = 0.48
	light.light_energy = 0.0
	add_child(light)
	set_aim(aim_direction)

func set_character(index: int) -> void:
	character = clampi(index,0,1)
	_load_character()
	set_aim(aim_direction)

func _load_character() -> void:
	if is_instance_valid(model):
		remove_child(model)
		model.queue_free()
	armor_model = null
	helmet_model = null
	helmet_attachment = null
	weapon_model = null
	var asset := "survivor_male_universal" if character==0 else "survivor_female_universal"
	model = load("res://assets/models/actors/"+asset+".glb").instantiate()
	model.rotation.y = PI
	add_child(model)
	legs.clear()
	skeleton=model.find_child("Skeleton3D",true,false) as Skeleton3D
	right_hand=skeleton.find_bone("hand_r") if is_instance_valid(skeleton) else -1
	grip=null
	if is_instance_valid(skeleton):
		grip=GunGripIK.new()
		grip.hand_offset={"r":GunGripIK.mesh_offset(model,"hand_r"),"l":GunGripIK.mesh_offset(model,"hand_l")}
		skeleton.add_child(grip)
		# Follows the hand bone after the IK has run, so the gun sits exactly in the visible palm.
		hand_anchor=BoneAttachment3D.new(); hand_anchor.bone_name="hand_r"; skeleton.add_child(hand_anchor)
	animation_player=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	_play_run()
	_load_weapon_model()
	set_armor(has_armor)
	set_helmet(has_helmet)

func _play_run() -> void:
	if is_instance_valid(animation_player) and animation_player.has_animation("Run_Gun"):
		var clip := animation_player.get_animation("Run_Gun")
		clip.loop_mode = Animation.LOOP_LINEAR
		animation_player.speed_scale = 0.88
		animation_player.play("Run_Gun")

func _load_weapon_model() -> void:
	if is_instance_valid(weapon_model):
		weapon_model.get_parent().remove_child(weapon_model)
		weapon_model.queue_free()
	weapon_model=null
	if not is_instance_valid(model): return
	var path: String="res://assets/models/rifle.glb" if weapon=="RIFLE" else "res://assets/models/weapons/"+weapon.to_lower()+".glb"
	weapon_model=load(path).instantiate() as Node3D
	model.add_child(weapon_model)
	weapon_model.rotation=Vector3.ZERO
	weapon_model.scale=Vector3.ONE*float(WEAPON_SCALES.get(weapon,0.5))
	_load_muzzle_flash()
	_update_weapon_transform()

func _load_muzzle_flash() -> void:
	if is_instance_valid(flash):
		flash.get_parent().remove_child(flash); flash.queue_free()
	var scene_path: String="res://assets/BinbunVFX/muzzle_flash/effects/"+str(FLASH_SCENES.get(weapon,FLASH_SCENES["PISTOL"]))
	flash=load(scene_path).instantiate() as Node3D
	flash.set("autoplay",false); flash.set("one_shot",true); flash.set("light_enable",false)
	flash.scale=Vector3.ONE*float(FLASH_SCALES.get(weapon,0.20))
	flash.visible=false
	add_child(flash)

func reset() -> void:
	max_health = 100.0
	health = max_health
	projectile_count = 1
	gun_level = 1
	split_bonus = 0
	stowed = {}
	scrap = 0
	damage_scale = 1.0
	rate_scale = 1.0
	target_x = 0.0
	position = Vector3(0,0,4.5)
	hurt_flash = 0.0
	reloading = false
	grenade_count = 2
	flashbang_count = 1
	fire_ammo = 0
	fire_mode = false
	set_armor(false)
	set_helmet(false)
	set_weapon("PISTOL")
	gun_level = 1
	set_aim(Vector3.FORWARD)
	_play_run()

func set_armor(equipped: bool) -> void:
	has_armor = equipped
	if is_instance_valid(armor_model):
		armor_model.get_parent().remove_child(armor_model)
		armor_model.queue_free()
		armor_model = null
	if has_armor and is_instance_valid(model):
		armor_model = load("res://assets/models/armor.glb").instantiate() as Node3D
		# Fit around the torso, not around the character's feet: the source model is
		# modelled at its final height, so scaling needs a compensating vertical offset.
		armor_model.scale = Vector3(0.72, 0.78, 0.64)
		armor_model.position.y = 1.315 * (1.0 - armor_model.scale.y)
		model.add_child(armor_model)

func set_helmet(equipped: bool) -> void:
	has_helmet = equipped
	if is_instance_valid(helmet_attachment):
		helmet_attachment.get_parent().remove_child(helmet_attachment)
		helmet_attachment.queue_free()
	helmet_attachment = null
	helmet_model = null
	if has_helmet and is_instance_valid(skeleton) and skeleton.find_bone("Head")>=0:
		helmet_attachment = BoneAttachment3D.new()
		helmet_attachment.bone_name = "Head"
		skeleton.add_child(helmet_attachment)
		helmet_model = load("res://assets/models/helmet.glb").instantiate() as Node3D
		helmet_model.scale = Vector3.ONE * 1.12
		helmet_model.position = Vector3(0,0.065,0.015)
		helmet_attachment.add_child(helmet_model)

func apply_meta(upgrades: Dictionary) -> void:
	max_health=100.0+int(upgrades.get("medical",0))*15.0
	health=max_health
	reserve_ammo+=int(upgrades.get("ammo",0))*30
	var boost:=1.0+int(upgrades.get("damage",0))*0.08
	damage_scale*=boost; damage*=boost
	weapon_levels.clear()
	for w in ["PISTOL","SMG","SHOTGUN","RIFLE","SNIPER","LAUNCHER"]:
		weapon_levels[w]=int(upgrades.get("w_"+w.to_lower(),0))
	damage*=weapon_bonus(weapon)

func weapon_bonus(id: String) -> float:
	return 1.0+int(weapon_levels.get(id,0))*0.12

func set_weapon(id: String) -> void:
	weapon = id
	reloading = false
	reload_timer = 0.0
	projectile_count = 1
	fire_mode = false
	match weapon:
		"SMG":
			magazine_size = 36; damage = 12.0*damage_scale; fire_interval = 0.095*rate_scale
			bullet_speed = 31.0; pierce = 0; reload_duration = 1.35; reserve_ammo = 108
		"SNIPER":
			magazine_size = 5; damage = 95.0*damage_scale; fire_interval = 0.85*rate_scale
			bullet_speed = 48.0; pierce = 2; reload_duration = 1.80; reserve_ammo = 25
		"SHOTGUN":
			magazine_size = 8; damage = 30.0*damage_scale; fire_interval = 0.72*rate_scale; projectile_count = 7
			bullet_speed = 30.0; pierce = 0; reload_duration = 1.65; reserve_ammo = 48
		"PISTOL":
			magazine_size = 12; damage = 24.0*damage_scale; fire_interval = 0.42*rate_scale
			bullet_speed = 30.0; pierce = 0; reload_duration = 1.10; reserve_ammo = 72
		"LAUNCHER":
			magazine_size = 4; damage = 180.0*damage_scale; fire_interval = 1.0*rate_scale
			bullet_speed = 14.0; pierce = 0; reload_duration = 2.0; reserve_ammo = 16
		_:
			weapon = "RIFLE"; magazine_size = 30; damage = 20.0*damage_scale; fire_interval = 0.30*rate_scale
			bullet_speed = 28.0; pierce = 0; reload_duration = 1.25; reserve_ammo = 90
	damage *= weapon_bonus(weapon)
	projectile_count = mini(9 if weapon=="SHOTGUN" else 5, projectile_count+split_bonus)
	ammo = magazine_size
	gun_level += 1
	_load_weapon_model()
	_play_run()

func set_aim(direction: Vector3) -> void:
	if direction.length()<0.01: return
	# Never aim back over the shoulder while running forward: that turns the survivor round
	# and the two-handed stance reads as crossed arms. Keep aim in the forward half.
	direction.y=0.0
	if direction.z>-0.05:
		direction.z=-0.05
		if absf(direction.x)<0.05: direction.x=0.0; direction.z=-1.0
	aim_direction = direction.normalized()
	var yaw: float=PI+atan2(-aim_direction.x,-aim_direction.z)
	if is_instance_valid(model): model.rotation.y=yaw
	_update_weapon_transform()

func _update_weapon_transform() -> void:
	if not is_instance_valid(weapon_model) or not is_instance_valid(model): return
	var hand_position:=Vector3(0,1.42,0.38)
	if is_instance_valid(hand_anchor) and is_instance_valid(grip) and hand_anchor.is_inside_tree():
		hand_position=model.global_transform.affine_inverse()*(hand_anchor.global_transform*(grip.hand_offset["r"] as Vector3))
	elif is_instance_valid(grip) and grip.grip_point!=Vector3.ZERO:
		# The IK owns the firing hand, so mount the weapon where the IK put the grip.
		hand_position=model.global_transform.affine_inverse()*skeleton.global_transform*grip.grip_point
	elif is_instance_valid(skeleton) and right_hand>=0:
		var hand_global:=skeleton.to_global(skeleton.get_bone_global_pose(right_hand).origin)
		hand_position=model.global_transform.affine_inverse()*hand_global
	var weapon_scale:=float(WEAPON_SCALES.get(weapon,0.5))
	weapon_model.position=hand_position+GRIP_OFFSETS.get(weapon,GRIP_OFFSETS["PISTOL"])*weapon_scale
	var muzzle:=to_local(muzzle_position())
	if is_instance_valid(light): light.position=muzzle
	if is_instance_valid(flash):
		flash.position=muzzle
		flash.quaternion=Quaternion(Vector3.LEFT,aim_direction)

func tick(delta: float) -> void:
	position.x = move_toward(position.x,target_x,delta*6.8)
	position.x = clampf(position.x,-3.15,3.15)
	walk_time += delta*6.6
	model.position.y = 0.0
	if is_instance_valid(grip):
		# Dip the gun while reloading; per-weapon support-hand reach along the barrel.
		# Long guns are held lower (stock against the chest) so the stock and scope don't go
		# through the face; the pistol stays at shoulder height.
		var hold: float=float(HOLD_DROP.get(weapon,0.10))
		grip.grip_drop = lerpf(grip.grip_drop, hold+0.16 if reloading else hold, minf(1.0,delta*10.0))
		grip.support_forward = float(SUPPORT_REACH.get(weapon,0.03))
	_update_weapon_transform()
	if reloading:
		reload_timer -= delta
		if reload_timer<=0: finish_reload()
	flash_time = maxf(0,flash_time-delta)
	hurt_flash = maxf(0,hurt_flash-delta)
	light.light_energy = 0.75 if flash_time>0 else 0.0
	flash.visible = flash_time>0
	if flash.visible: flash.scale = Vector3.ONE*float(FLASH_SCALES.get(weapon,0.20))*(0.92+randf()*0.16)

## The pistol is the fallback sidearm: it never runs out of spare magazines.
## Swap between the gun from the crates and the pistol (which never runs out).
## Returns false when there's nothing to swap to.
func swap_weapon() -> bool:
	if weapon!="PISTOL":
		stowed={"id":weapon,"ammo":ammo,"reserve":reserve_ammo,"fire_ammo":fire_ammo}
		var level:=gun_level; set_weapon("PISTOL"); gun_level=level
		return true
	if stowed.is_empty() or (int(stowed.ammo)<=0 and int(stowed.reserve)<=0): return false
	var s:=stowed; stowed={}
	var level:=gun_level; set_weapon(String(s.id)); gun_level=level
	ammo=int(s.ammo); reserve_ammo=int(s.reserve); fire_ammo=int(s.get("fire_ammo",fire_ammo))
	return true

## Name of the gun the swap button would switch to ("" when none).
func swap_target() -> String:
	if weapon!="PISTOL": return "PISTOL"
	if stowed.is_empty() or (int(stowed.ammo)<=0 and int(stowed.reserve)<=0): return ""
	return String(stowed.id)

func infinite_ammo() -> bool:
	return weapon=="PISTOL"

func can_fire() -> bool:
	return ammo>0 and not reloading

func fire() -> void:
	if not can_fire(): return
	ammo -= 1
	flash_time = 0.070 if weapon!="SNIPER" else 0.10
	if is_instance_valid(flash): flash.call("play")

func request_reload() -> bool:
	if reloading or ammo>=magazine_size or (reserve_ammo<=0 and not infinite_ammo()): return false
	reloading = true
	reload_timer = reload_duration
	if is_instance_valid(animation_player) and animation_player.has_animation("Reload_Gun"):
		var clip := animation_player.get_animation("Reload_Gun")
		clip.loop_mode = Animation.LOOP_NONE
		animation_player.speed_scale = clip.length/reload_duration
		animation_player.play("Reload_Gun")
	return true

func finish_reload() -> void:
	var needed := magazine_size-ammo
	var loaded := needed if infinite_ammo() else mini(needed,reserve_ammo)
	ammo += loaded
	if not infinite_ammo(): reserve_ammo -= loaded
	reloading = false
	reload_timer = 0.0
	_play_run()

func take_damage(amount: float) -> void:
	var applied_damage := amount * (0.8 if has_helmet else 1.0)
	health = maxf(0,health-applied_damage)
	hurt_flash = 0.2

func apply_upgrade(id: String) -> void:
	match id:
		# Small steps per gate (many gates per run), so a run builds up gradually.
		"damage": damage_scale *= 1.08; damage *= 1.08; gun_level += 1
		"rate": rate_scale *= 0.94; fire_interval = maxf(0.075,fire_interval*0.94); gun_level += 1
		"split": split_bonus += 1; projectile_count = mini(9 if weapon=="SHOTGUN" else 5,projectile_count+1); gun_level += 1
		"heal": health = minf(max_health,health+15)
		"smg", "sniper", "shotgun", "pistol": set_weapon(id.to_upper())

func muzzle_position() -> Vector3:
	if is_instance_valid(weapon_model):
		return weapon_model.to_global(MUZZLE_POINTS.get(weapon,MUZZLE_POINTS["PISTOL"]))
	return global_position+Vector3(aim_direction.x*1.05,1.35,aim_direction.z*1.05)

func _emissive(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.emission_enabled = true
	m.emission = color
	m.emission_energy_multiplier = 2.0
	return m
