extends Node3D
const ModelFix=preload("res://scripts/model_fix.gd")

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
# Gate buffs (see buff_catalog.gd). Kept as separate multipliers / bonuses so they survive
# picking up a new gun (set_weapon re-reads the base stats of each gun).
var shield := 0.0             # absorbs damage before health
var regen := 0.0              # HP per second
var kill_heal := 0.0          # HP per kill
var dmg_reduce := 0.0         # 0..0.6 of incoming damage removed
var move_mult := 1.0          # forward run and side-step speed, up to 1.4
var bullet_speed_scale := 1.0
var crit_chance := 0.0        # 0..0.6
var crit_mult := 1.5          # damage x on a crit
var mag_scale := 1.0
var reload_scale := 1.0       # reload time multiplier, down to 0.3
var pierce_bonus := 0
var bullet_split := 0         # fragments when a bullet hits a zombie
var explode_chance := 0.0
var burn_dps := 0.0
var poison_dps := 0.0
var shock_chance := 0.0
var coin_mult := 1.0
var drop_chance := 0.0
var ammo_return := 0.0
var pickup_bonus := 0.0       # extra pickup reach in metres
var stowed: Dictionary = {}
var hand_anchor: BoneAttachment3D   # the main gun while the pistol is out: id, ammo, reserve
var weapon_levels: Dictionary = {} # shop upgrade level per weapon id
var meta_reserve_bonus := 0     # permanent ammo-case reserve, re-applied on every gun change
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
# Motorcycle from a vehicle crate: the survivor rides it, ramming zombies; every hit it soaks
# (or zombie it runs down) wears it out, it smokes under 30 durability and breaks apart at 0.
var vehicle := ""
var vehicle_durability := 0.0
var vehicle_model: Node3D
var cannon_kick:=0.0
var hide_rider:=false  # tank hull recoil, 1.0 right after a shot
var rider: SkeletonModifier3D
const BIKE_DURABILITY := 100.0
## Per-vehicle feel: forward speed, side-step pace, and ram power (how hard it plows through
## zombies — higher ram = less durability spent per zombie run down). The three bikes are
## genuinely different models: scrambler, sport bike and cruiser.
const VEHICLE_STATS := {
	"BIKE": {"speed": 2.9, "side": 1.8, "ram": 1.1},
	"SPORT": {"speed": 3.2, "side": 1.75, "ram": 1.5},
	"CRUISER": {"speed": 3.6, "side": 1.7, "ram": 1.9},
	"GOLD": {"speed": 3.4, "side": 1.72, "ram": 2.2},
	"TANK": {"speed": 2.0, "side": 0.55, "ram": 3.0},
}
## One GLB per vehicle. All are authored at real-world scale, Y-up, facing -Z (the
## survivor's run direction), so they mount without any per-vehicle scaling hacks.
const VEHICLE_MODELS := {
	"BIKE": "res://assets/models/vehicles/bike_paid.glb",
	"SPORT": "res://assets/models/vehicles/bike_paid2.glb",
	"CRUISER": "res://assets/models/vehicles/bike_paid3.glb",
	"GOLD": "res://assets/models/vehicles/bike_gold.glb",
	"TANK": "res://assets/models/vehicles/tank_military.glb",
}
## Seat fit per vehicle (lift_y, back_z), measured from each GLB:
## scrambler seat top ~0.83, sport ~0.90, cruiser ~0.73. Rider pelvis rest height is
## 0.917 for ALL 5 survivors (same rig), so one row per vehicle covers every character.
const SEAT_FIT := {
	"BIKE": Vector2(0.14, 0.17),
	"SPORT": Vector2(0.22, 0.09),
	"CRUISER": Vector2(0.04, 0.15),
	"GOLD": Vector2(0.10, 0.14),
	"TANK": Vector2(1.05, 0.30),
}

func vehicle_speed() -> float:
	return float(VEHICLE_STATS.get(vehicle, {}).get("speed", 1.0)) if vehicle != "" else 1.0

func vehicle_side() -> float:
	return float(VEHICLE_STATS.get(vehicle, {}).get("side", 1.0)) if vehicle != "" else 1.0

func vehicle_ram() -> float:
	return float(VEHICLE_STATS.get(vehicle, {}).get("ram", 1.0)) if vehicle != "" else 1.0
var legs: Array[Node3D] = []
var walk_time := 0.0
var flash_time := 0.0
var hurt_flash := 0.0
var aim_direction := Vector3.FORWARD
var light: OmniLight3D
var torch: SpotLight3D
var torch_spill: OmniLight3D
var flash: Node3D

const GRIP_OFFSETS := {
	"PISTOL": Vector3(0.0,0.20,0.18),  # pushed forward: the grip was clipping into the palm
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
	torch=SpotLight3D.new(); torch.light_color=Color("e3edff"); torch.spot_range=18.0; torch.spot_angle=44.0
	# The emitter sits just beyond the muzzle; disabling self-shadowing stops the gun
	# itself from blacking out its own beam in the Compatibility renderer.
	torch.spot_angle_attenuation=1.15; torch.spot_attenuation=1.0; torch.shadow_enabled=false; torch.light_energy=0.0
	add_child(torch); torch.visible=false
	torch_spill=OmniLight3D.new(); torch_spill.light_color=Color("c9dcff"); torch_spill.omni_range=2.8; torch_spill.light_energy=0.0
	add_child(torch_spill)
	set_aim(aim_direction)

func set_night(night: float) -> void:
	if is_instance_valid(torch):
		torch.visible=night>0.025; torch.light_energy=9.0*night
	if is_instance_valid(torch_spill): torch_spill.light_energy=0.65*night

func set_character(index: int, asset_override:="") -> void:
	character = clampi(index,0,CHARACTER_ASSETS.size()-1)
	character_asset_override = asset_override
	_load_character()
	set_aim(aim_direction)

## Darius the paramedic doubles every healing effect (medkits, heal gates, kill-heal,
## regen). Kept as a derived value so it can never desync from the chosen character.
func heal_scale() -> float:
	return 2.0 if character==2 else 1.0

## Jian the scavenger: years of stripping the dead city taught him what is worth
## carrying — every ammo box yields half again as much, and coins stretch 25% further.
func scavenger_ammo_scale() -> float:
	return 1.5 if character==4 else 1.0

func scavenger_coin_scale() -> float:
	return 1.25 if character==4 else 1.0

## Maya's field instinct: she slowly patches herself up when she's hurting (never past
## 60% — it is a survival net, not sustain), and every hit she takes floods her with
## adrenaline: a short burst of extra speed to get clear.
const INSTINCT_REGEN:=1.5        # HP per second while below the cap
const INSTINCT_REGEN_CAP:=0.6    # …up to this share of max health
const INSTINCT_HASTE_TIME:=2.5   # seconds of speed after a hit
const INSTINCT_HASTE:=1.25       # speed multiplier while the adrenaline lasts
var instinct_boost:=0.0          # seconds of adrenaline left

func is_maya() -> bool:
	return character==3

func instinct_regen_rate() -> float:
	if not is_maya() or health>=max_health*INSTINCT_REGEN_CAP: return 0.0
	return INSTINCT_REGEN

## The survivor's real pace: gate buffs, Maya's adrenaline, and the bike's engine.
func effective_move_mult() -> float:
	return move_mult*(INSTINCT_HASTE if instinct_boost>0.0 else 1.0)*vehicle_speed()

func on_vehicle() -> bool:
	return vehicle!=""

## Climb on: the bike appears under the survivor, the run cycle freezes and the seated
## pose modifier folds the legs onto the pegs (arms stay on the gun via the grip IK).
func mount_vehicle(id: String) -> void:
	var path: String=String(VEHICLE_MODELS.get(id,""))
	if vehicle!="" or path=="" or not ResourceLoader.exists(path): return
	vehicle=id; vehicle_durability=BIKE_DURABILITY
	vehicle_model=(load(path) as PackedScene).instantiate() as Node3D
	vehicle_model.position=Vector3(0,0,0.05)
	add_child(vehicle_model); ModelFix.double_sided(vehicle_model)
	# the tank GLB faces +Z; the survivor runs -Z, so turn the hull around
	hide_rider=(id=="TANK")
	# GOLD: reflective paint - high metallic + low roughness lets the sky light
	# run along the bodywork instead of faking it with particles.
	if id=="GOLD":
		for mi in vehicle_model.find_children("*","MeshInstance3D",true,false):
			var m2:=mi as MeshInstance3D
			if m2==null or m2.mesh==null: continue
			for s2 in range(m2.mesh.get_surface_count()):
				var bm:=m2.mesh.surface_get_material(s2) as BaseMaterial3D
				if bm!=null:
					# NOT metallic: with no reflection probe a metal surface renders black.
					# Glossy dielectric + rim = sun highlights that slide over the paint.
					bm.metallic=0.0; bm.roughness=0.18; bm.metallic_specular=1.0
					bm.rim_enabled=true; bm.rim=0.55; bm.rim_tint=1.0
					bm.emission_enabled=true
					bm.emission=Color(1.0,0.72,0.22)
					bm.emission_energy_multiplier=1.15
	if id=="TANK":
		vehicle_model.rotation.y=PI
		# a crew sits INSIDE a tank: drop the survivor model and its attachments
		if is_instance_valid(model): model.visible=false
	# Seat the rider on THIS vehicle's seat (per-vehicle lift/back, see SEAT_FIT).
	if is_instance_valid(model):
		model.position.z=float(SEAT_FIT.get(id,Vector2.ZERO).y)
	if is_instance_valid(skeleton):
		rider=(load("res://scripts/rider_pose.gd") as GDScript).new() as SkeletonModifier3D
		rider.set("body",model); skeleton.add_child(rider)

## Back on foot (bike broken or the run reset): drop the pose; the run cycle never stopped.
func dismount_vehicle() -> void:
	vehicle=""
	if is_instance_valid(model):
		model.position=Vector3.ZERO
		model.visible=true
	hide_rider=false
	if is_instance_valid(vehicle_model): vehicle_model.queue_free(); vehicle_model=null
	if is_instance_valid(rider): rider.queue_free(); rider=null

func _tick_vehicle_visual(delta: float) -> void:
	if not is_instance_valid(vehicle_model): return
	for w in ["WheelFrontPivot","WheelRearPivot"]:
		var pivot:=vehicle_model.find_child(w,true,false) as Node3D
		if pivot: pivot.rotation.x+=delta*10.0
	# Lean into sideways moves like a real bike instead of pure translation.
	if vehicle=="TANK":
		# tracked hull: never lean, just kick back from the cannon and settle
		vehicle_model.rotation.z=lerpf(vehicle_model.rotation.z,0.0,1.0-exp(-delta*9.0))
		cannon_kick=maxf(0.0,cannon_kick-delta*3.6)
		vehicle_model.position.z=0.05+cannon_kick*0.22
		return
	var lateral: float=0.0
	if is_instance_valid(self):
		lateral=clampf((position.x-target_x)*1.4,-1.0,1.0)
	vehicle_model.rotation.z=lerpf(vehicle_model.rotation.z,-lateral*0.42,1.0-exp(-delta*9.0))

const CHARACTER_ASSETS := ["survivor_male_universal","survivor_riley_universal","survivor_medic_universal","survivor_maya_universal","survivor_jian_scout_universal"]
## Female characters run on the female-captured clips (narrower stance, no male hip sway).
const FEMALE_CHARACTERS := [1, 3]  # riley, maya

var run_clip:="Run_Gun"     # resolved in _play_run (female variant when available)

## Animation name for this character: the "_F" female variant when the model has one.
func _anim_name(base: String) -> String:
	if character in FEMALE_CHARACTERS and is_instance_valid(animation_player) and animation_player.has_animation(base+"_F"):
		return base+"_F"
	return base

var character_asset_override:="" # outfit skin: full res:// path that replaces the default body

func _load_character() -> void:
	if is_instance_valid(model):
		remove_child(model)
		model.queue_free()
	armor_model = null
	helmet_model = null
	helmet_attachment = null
	weapon_model = null
	var asset_path: String = character_asset_override
	if asset_path=="": asset_path="res://assets/models/actors/"+CHARACTER_ASSETS[clampi(character,0,CHARACTER_ASSETS.size()-1)]+".glb"
	if not ResourceLoader.exists(asset_path): asset_path="res://assets/models/actors/"+CHARACTER_ASSETS[0]+".glb"
	BootTrace.mark("player: loading " + asset_path.get_file())
	model = ModelFix.spawn(asset_path)
	if model == null:
		push_error("survivor model unavailable, keeping the previous one")
		return
	model.rotation.y = PI
	add_child(model)
	ModelFix.double_sided(model)
	legs.clear()
	skeleton=model.find_child("Skeleton3D",true,false) as Skeleton3D
	right_hand=skeleton.find_bone("hand_r") if is_instance_valid(skeleton) else -1
	grip=null
	if is_instance_valid(skeleton):
		grip=GunGripIK.new()
		grip.character=character
		# Yuhang's mesh has no vertex weighted >0.6 to the hand group, so mesh_offset() comes
		# back empty and the IK would aim the wrist bone instead of the visible hand (hands
		# crossed, arms buried). All five rigs share the same bone lengths and shoulder width
		# (upper 0.274 / fore 0.273 / shoulder 0.384), so his palm sits where the male's does.
		var off_r: Vector3=GunGripIK.mesh_offset(model,"hand_r")
		var off_l: Vector3=GunGripIK.mesh_offset(model,"hand_l")
		if off_r.length()<0.001: off_r=Vector3(0.078,-0.096,-0.010)
		if off_l.length()<0.001: off_l=Vector3(0.020,-0.096,0.113)
		grip.hand_offset={"r":off_r,"l":off_l}
		skeleton.add_child(grip)
		# Follows the hand bone after the IK has run, so the gun sits exactly in the visible palm.
		hand_anchor=BoneAttachment3D.new(); hand_anchor.bone_name="hand_r"; skeleton.add_child(hand_anchor)
	animation_player=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	_play_run()
	_load_weapon_model()
	set_armor(has_armor)
	set_helmet(has_helmet)

## The run clip moves a planted foot ~0.97 m/s at normal speed, but the road scrolls at
## 3.5 m/s, so at the old 0.88 the feet skated. 1.9 is a fast sprint cadence (0.7 s a
## stride pair) that cuts the slide by more than half without looking cartoonish.
const RUN_ANIM_SPEED := 1.9

func _play_run() -> void:
	run_clip=_anim_name("Run_Gun")
	if is_instance_valid(animation_player) and animation_player.has_animation(run_clip):
		var clip := animation_player.get_animation(run_clip)
		clip.loop_mode = Animation.LOOP_LINEAR
		animation_player.speed_scale = RUN_ANIM_SPEED*move_mult
		animation_player.play(run_clip)

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
	dismount_vehicle()
	max_health = 100.0
	health = max_health
	projectile_count = 1
	gun_level = 1
	split_bonus = 0
	shield = 0.0; regen = 0.0; kill_heal = 0.0; dmg_reduce = 0.0; move_mult = 1.0
	bullet_speed_scale = 1.0; crit_chance = 0.0; crit_mult = 1.5; mag_scale = 1.0; reload_scale = 1.0
	pierce_bonus = 0; bullet_split = 0; explode_chance = 0.0; burn_dps = 0.0; poison_dps = 0.0
	shock_chance = 0.0; coin_mult = 1.0; drop_chance = 0.0; ammo_return = 0.0; pickup_bonus = 0.0
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
	instinct_boost = 0.0
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
	# The ammo case is permanent: the extra reserve is re-applied by set_weapon every
	# time a gun is (re)loaded, so picking up a crate gun never wipes the purchase.
	meta_reserve_bonus=int(upgrades.get("ammo",0))*30
	reserve_ammo+=meta_reserve_bonus
	var boost:=1.0+int(upgrades.get("damage",0))*0.08
	damage_scale*=boost; damage*=boost
	weapon_levels.clear()
	for w in ["PISTOL","SMG","SHOTGUN","RIFLE","SNIPER","LAUNCHER"]:
		weapon_levels[w]=int(upgrades.get("w_"+w.to_lower(),0))
	# Weapon upgrade damage is applied inside set_weapon (which reset() just ran), so the
	# bonus lands exactly once per gun — never squared by applying it again here.
	damage=base_damage(weapon)*weapon_bonus(weapon)

func weapon_bonus(id: String) -> float:
	return 1.0+int(weapon_levels.get(id,0))*0.12

## The gun's damage before gate buffs and shop upgrades — one source of truth shared by
## set_weapon and apply_meta so a bought level always lands exactly once.
func base_damage(id: String) -> float:
	match id:
		"SMG": return 12.0*damage_scale
		"SNIPER": return 95.0*damage_scale
		"SHOTGUN": return 30.0*damage_scale
		"PISTOL": return 24.0*damage_scale
		"LAUNCHER": return 180.0*damage_scale
		_: return 20.0*damage_scale

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
	damage = base_damage(weapon)*weapon_bonus(weapon)
	# The ammo case bought in the supply truck is never lost to a weapon swap.
	reserve_ammo += meta_reserve_bonus
	magazine_size = maxi(1,int(round(magazine_size*mag_scale)))
	reload_duration *= reload_scale
	bullet_speed *= bullet_speed_scale
	pierce += pierce_bonus
	projectile_count = mini(9 if weapon=="SHOTGUN" else 5, projectile_count+split_bonus)
	ammo = magazine_size
	gun_level += 1
	_load_weapon_model()
	_play_run()

func set_aim(direction: Vector3) -> void:
	if direction.length()<0.01: return
	# Full 360 deg aim: the survivor turns on the spot to shoot whatever is picked,
	# including the horde (or the beast) coming up from behind. (The forward-only clamp
	# that briefly lived here also made the stance read as crossed arms at the edges.)
	direction.y=0.0
	aim_direction = direction.normalized()
	var yaw: float=PI+atan2(-aim_direction.x,-aim_direction.z)
	if is_instance_valid(model): model.rotation.y=yaw
	_update_weapon_transform()

func _update_weapon_transform() -> void:
	if not is_instance_valid(weapon_model) or not is_instance_valid(model): return
	# Flush movement/yaw before reading muzzle and hand globals; otherwise the torch
	# lags one frame behind a sideways-moving player in the Compatibility renderer.
	force_update_transform(); model.force_update_transform()
	var hand_position:=Vector3(0,1.42,0.38)
	if is_instance_valid(grip) and grip.grip_point!=Vector3.ZERO and grip.support_point!=Vector3.ZERO:
		# Both IK points refer to the visible palms, not the possibly misaligned hand bones.
		# Center every survivor's weapon between those palms instead of hanging it off hand_r.
		var between_hands: Vector3=(grip.grip_point+grip.support_point)*0.5
		hand_position=model.global_transform.affine_inverse()*skeleton.global_transform*between_hands
	elif is_instance_valid(hand_anchor) and is_instance_valid(grip) and hand_anchor.is_inside_tree():
		hand_position=model.global_transform.affine_inverse()*(hand_anchor.global_transform*(grip.hand_offset["r"] as Vector3))
	elif is_instance_valid(grip) and grip.grip_point!=Vector3.ZERO:
		hand_position=model.global_transform.affine_inverse()*skeleton.global_transform*grip.grip_point
	elif is_instance_valid(skeleton) and right_hand>=0:
		var hand_global:=skeleton.to_global(skeleton.get_bone_global_pose(right_hand).origin)
		hand_position=model.global_transform.affine_inverse()*hand_global
	var weapon_scale:=float(WEAPON_SCALES.get(weapon,0.5))
	weapon_model.position=hand_position+GRIP_OFFSETS.get(weapon,GRIP_OFFSETS["PISTOL"])*weapon_scale
	weapon_model.force_update_transform()
	var muzzle:=to_local(muzzle_position())
	if is_instance_valid(light): light.position=muzzle
	if is_instance_valid(torch):
		torch.position=muzzle+aim_direction*0.08+Vector3(0,-0.04,0)
		torch.look_at(to_global(torch.position+aim_direction*8.0+Vector3(0,-0.85,0)),Vector3.UP)
	if is_instance_valid(torch_spill): torch_spill.position=muzzle-aim_direction*0.30
	if is_instance_valid(flash):
		flash.position=muzzle
		flash.quaternion=Quaternion(Vector3.LEFT,aim_direction)

func tick(delta: float) -> void:
	_tick_vehicle_visual(delta)
	instinct_boost=maxf(0.0,instinct_boost-delta)
	position.x = move_toward(position.x,target_x,delta*6.8*effective_move_mult()*vehicle_side())
	position.x = clampf(position.x,-3.15,3.15)
	walk_time += delta*6.6
	if is_instance_valid(animation_player) and animation_player.current_animation==run_clip:
		# On a vehicle the run cycle freezes (rider pose holds the legs); animating it
		# under the pose makes the legs vibrate. Arms stay on the gun via grip IK.
		animation_player.speed_scale = 0.0 if vehicle!="" else RUN_ANIM_SPEED*effective_move_mult()
	# Seated lift per vehicle (SEAT_FIT) so pelvis sits ON the seat, not through it.
	model.position.y = float(SEAT_FIT.get(vehicle,Vector2.ZERO).x) if vehicle!="" else 0.0
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
	var reload_clip:=_anim_name("Reload_Gun")
	if is_instance_valid(animation_player) and animation_player.has_animation(reload_clip):
		var clip := animation_player.get_animation(reload_clip)
		clip.loop_mode = Animation.LOOP_NONE
		animation_player.speed_scale = clip.length/reload_duration
		animation_player.play(reload_clip)
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
	var applied_damage := amount * (0.8 if has_helmet else 1.0) * (1.0-dmg_reduce)
	if shield>0.0:
		var soak := minf(shield,applied_damage)
		shield -= soak; applied_damage -= soak
	health = maxf(0,health-applied_damage)
	hurt_flash = 0.2
	if applied_damage>0.0 and is_maya(): instinct_boost=INSTINCT_HASTE_TIME # adrenaline: run!

## `value` comes from the gate's rarity roll (percent for damage / rate, HP for heal, bullets for
## split); -1 keeps the original common-gate amounts.
func apply_upgrade(id: String,value:=-1.0) -> void:
	match id:
		# Small steps per gate (many gates per run), so a run builds up gradually.
		"damage":
			var f:=1.0+(8.0 if value<0 else value)/100.0
			damage_scale *= f; damage *= f; gun_level += 1
		"rate":
			var f:=1.0-(6.0 if value<0 else value)/100.0
			rate_scale *= f; fire_interval = maxf(0.075,fire_interval*f); gun_level += 1
		"multishot":
			var n:=1 if value<0 else int(value)
			split_bonus += n; projectile_count = mini(9 if weapon=="SHOTGUN" else 5,projectile_count+n); gun_level += 1
		"heal": health = minf(max_health,health+(15.0 if value<0 else value)*heal_scale())
		"max_hp": max_health += value; health = minf(max_health,health+value)
		"regen": regen += value
		"kill_heal": kill_heal += value
		"dmg_reduce": dmg_reduce = minf(0.6,dmg_reduce+value/100.0)
		"shield": shield = minf(200.0,shield+value)
		"move": move_mult = minf(1.4,move_mult*(1.0+value/100.0))
		"bullet_speed":
			var f:=1.0+value/100.0
			bullet_speed_scale *= f; bullet_speed *= f
		"crit_chance": crit_chance = minf(0.6,crit_chance+value/100.0)
		"crit_damage": crit_mult += value/100.0
		"magazine":
			var f:=1.0+value/100.0
			mag_scale *= f
			var grown:=maxi(magazine_size+1,int(round(magazine_size*f)))
			ammo += grown-magazine_size; magazine_size = grown
		"reserve":
			# spare magazines for the gun that uses them (the pistol never runs out)
			if weapon!="PISTOL": reserve_ammo += magazine_size*int(value)
			elif not stowed.is_empty(): stowed.reserve = int(stowed.reserve)+30*int(value)
		"reload":
			var f:=1.0-value/100.0
			var before:=reload_scale; reload_scale = maxf(0.3,reload_scale*f)
			reload_duration *= reload_scale/before
		"pierce": pierce_bonus += int(value); pierce += int(value)
		"split": bullet_split += int(value)
		"explode": explode_chance = minf(0.6,explode_chance+value/100.0)
		"burn": burn_dps += value
		"poison": poison_dps += value
		"shock": shock_chance = minf(0.6,shock_chance+value/100.0)
		"coins": coin_mult += value/100.0
		"drop": drop_chance = minf(0.4,drop_chance+value/100.0)
		"ammo_return": ammo_return = minf(0.6,ammo_return+value/100.0)
		"pickup_range": pickup_bonus += value*0.5
		"smg", "sniper", "shotgun", "pistol": set_weapon(id.to_upper())

## A gate buff that would do nothing right now is never offered (see main_3d _buff_useful).
func can_use_reserve() -> bool:
	return weapon!="PISTOL" or not stowed.is_empty()

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
