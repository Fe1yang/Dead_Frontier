extends Node3D
## Character lobby: the chosen survivor stands full-body on a lit platform in an idle loop,
## like a fitting room. Characters (and later skins) swap in with a short turn; dragging spins
## the model. Pets get their own slot beside the character once their models exist.

const AnimLibrary=preload("res://scripts/anim_library.gd")
const ArmsRelaxed=preload("res://scripts/arms_relaxed.gd")
const GunGripIK=preload("res://scripts/gun_grip_ik.gd")
const ModelFix=preload("res://scripts/model_fix.gd")
const IdleLife=preload("res://scripts/idle_life.gd")
const CHARACTERS:=[
	{"asset":"res://assets/models/actors/survivor_male_universal.glb","name":"MASON","lobby_clavicle":8.0,"lobby_out":0.18,"lobby_fwd":0.04,"lobby_palm_twist":-15.0},
	{"asset":"res://assets/models/actors/survivor_riley_universal.glb","name":"RILEY","palm_twist":90.0,"lobby_palm_twist":25.0,"lobby_out":0.06,"lobby_fwd":0.03,"lobby_clavicle":5.0,"lobby_bend":14.0},
	{"asset":"res://assets/models/actors/survivor_medic_universal.glb","name":"DARIUS","lobby_clavicle":8.0,"lobby_out":0.18,"lobby_fwd":0.04,"lobby_palm_twist":-15.0,"perk":"perk_darius"},
	{"asset":"res://assets/models/actors/survivor_maya_universal.glb","name":"MAYA","palm_twist":90.0,"lobby_palm_twist":25.0,"lobby_out":0.06,"lobby_fwd":0.03,"lobby_clavicle":5.0,"lobby_bend":14.0,"perk":"perk_maya"}]
const PETS:=[
	{"asset":"res://assets/models/pets/doberman.glb","name":"杜宾犬","length":1.10},
	{"asset":"res://assets/models/pets/german_shepherd.glb","name":"德国牧羊犬","length":1.16},
	{"asset":"res://assets/models/pets/czech_wolfdog.glb","name":"捷克狼犬","length":1.22},
	{"asset":"res://assets/models/pets/tibetan_mastiff.glb","name":"藏獒","length":1.10}]
## Outfit skins: same survivor, different body. `char` indexes CHARACTERS; the first entry
## per character is the default look. Skins never change stats — Maya keeps her perk either way.
const SKINS:=[
	{"char":3,"asset":"res://assets/models/actors/survivor_maya_universal.glb","name":"maya"},
	{"char":3,"asset":"res://assets/models/actors/survivor_maya_tactical_universal.glb","name":"maya_tactical"}]
const ORIGIN:=Vector3(-200,0,0) # far from the road so nothing from the run leaks into the shot
const STAND:=Vector3(-0.08,0.0,0)  # survivor just left of centre, the dog right beside him
const ACTOR_SCALE:=0.86
const CAMERA_POS:=Vector3(0.0,1.22,5.7)
const CAMERA_TARGET:=Vector3(0.0,0.62,0.0) # aimed lower so survivor and dog stand above the picker strip
const CAMERA_FOV:=38.0
const PET_SPOT:=Vector3(0.50,0.0,0.28) # close at the survivor's side, a step forward

var actor: Node3D
var actor_anim: AnimationPlayer
var actor_index:=-1
var spin:=0.0          # user drag rotation
var spin_velocity:=0.0
var intro_turn:=0.0    # eases a newly selected character into facing the camera
var time:=0.0
var pet: Node3D
var idle_life: Node
# Safehouse lights that breathe: the bare bulb buzzes, the burn barrel embers flicker.
var bulb_light: SpotLight3D
var bulb_mat: StandardMaterial3D
var ember_light: OmniLight3D
var ember_mat: StandardMaterial3D

func _ready() -> void:
	position=ORIGIN
	_build_set()

## Framing: on the survivors tab the camera moves in so the survivor fills the shot (whole body,
## the dog still at their side); on the pets tab it eases back out to the wider two-shot.
const SOLO_POS:=Vector3(-0.08,0.92,4.15)   # centred on the survivor (STAND.x), close in
const SOLO_TARGET:=Vector3(-0.08,0.50,0.0)
var pet_zoom:=0.0      # 0 = survivor close-up, 1 = survivor and dog
var focus_pets:=false  # set by main_3d when the pets tab is open

func camera_position() -> Vector3:
	var e:=pet_zoom*pet_zoom*(3.0-2.0*pet_zoom)
	return ORIGIN+SOLO_POS.lerp(CAMERA_POS,e)+Vector3(sin(time*0.3)*0.04,sin(time*0.45)*0.02,0)

func camera_target() -> Vector3:
	var e:=pet_zoom*pet_zoom*(3.0-2.0*pet_zoom)
	return ORIGIN+SOLO_TARGET.lerp(CAMERA_TARGET,e)

var actor_asset:=""
func show_character(index: int, asset_override:="") -> void:
	index=clampi(index,0,CHARACTERS.size()-1)
	var asset_path: String=asset_override if asset_override!="" else String(CHARACTERS[index].get("asset",""))
	if not ResourceLoader.exists(asset_path):
		# A character whose model isn't in this build falls back to the first survivor.
		index=0; asset_path=String(CHARACTERS[0].asset)
	if index==actor_index and asset_path==actor_asset and is_instance_valid(actor): return
	if is_instance_valid(actor): actor.queue_free()
	actor_index=index; actor_asset=asset_path
	actor=(load(asset_path) as PackedScene).instantiate() as Node3D
	actor.position=STAND; actor.scale=Vector3.ONE*ACTOR_SCALE
	add_child(actor); ModelFix.double_sided(actor)
	_foot_shadow()
	actor_anim=actor.find_child("AnimationPlayer",true,false) as AnimationPlayer
	if actor_anim: actor_anim.stop() # the lobby is a static, natural standing pose only
	var skeleton:=actor.find_child("Skeleton3D",true,false) as Skeleton3D
	if skeleton:
		skeleton.reset_bone_poses()
		# breathing, weight shift and look-around on spine/neck/head only; added first so the
		# relaxed-arms pass below still hangs the arms naturally from the moving shoulders
		idle_life=IdleLife.new(); idle_life.setup(skeleton); skeleton.add_child(idle_life)
		var arms:=ArmsRelaxed.new(); arms.body=actor
		arms.hand_offset={"r":GunGripIK.mesh_offset(actor,"hand_r"),"l":GunGripIK.mesh_offset(actor,"hand_l")}
		arms.setup_from_model(actor,skeleton)
		arms.palm_twist_deg=float(CHARACTERS[index].get("lobby_palm_twist",0.0)) # palms toward the thighs
		# Relaxed A-stance: a visible gap at each side, hands hanging beside—not against—the thighs.
		arms.outward=float(CHARACTERS[index].get("lobby_out",0.17)); arms.forward=float(CHARACTERS[index].get("lobby_fwd",0.04))
		arms.clavicle_drop=float(CHARACTERS[index].get("lobby_clavicle",16.0)) # level, relaxed shoulders
		arms.base_bend=float(CHARACTERS[index].get("lobby_bend",0.0)) # female stance: elbows bent, hands off the hips
		skeleton.add_child(arms) # straight wrists, relaxed arms, palms facing the thighs
		idle_life.arms=arms
	intro_turn=0.0; spin=0.0; spin_velocity=0.0

## Soft dark contact shadow under the survivor's feet (a blob, independent of the set lighting).
var foot_shadow: MeshInstance3D
func _foot_shadow() -> void:
	if is_instance_valid(foot_shadow): return
	foot_shadow=_blob_shadow(Vector2(1.05,0.75),STAND+Vector3(0,0.022,0.02))

## Soft dark contact blob (a gradient decal, independent of the set lighting).
func _blob_shadow(size: Vector2,pos: Vector3) -> MeshInstance3D:
	var g:=Gradient.new(); g.set_color(0,Color(0,0,0,0.62)); g.set_color(1,Color(0,0,0,0.0)); g.add_point(0.55,Color(0,0,0,0.38))
	var tex:=GradientTexture2D.new(); tex.gradient=g; tex.fill=GradientTexture2D.FILL_RADIAL
	tex.fill_from=Vector2(0.5,0.5); tex.fill_to=Vector2(1.0,0.5); tex.width=128; tex.height=128
	var m:=StandardMaterial3D.new(); m.albedo_texture=tex; m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED; m.depth_draw_mode=BaseMaterial3D.DEPTH_DRAW_DISABLED
	var q:=PlaneMesh.new(); q.size=size
	var shadow:=MeshInstance3D.new(); shadow.mesh=q; shadow.material_override=m
	shadow.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	shadow.position=pos; add_child(shadow); return shadow

var pet_path:=""
var pet_shadow: MeshInstance3D

func show_pet(path: String) -> void:
	if path==pet_path and is_instance_valid(pet): return
	pet_path=path
	if is_instance_valid(pet): pet.queue_free(); pet=null
	if is_instance_valid(pet_shadow): pet_shadow.queue_free(); pet_shadow=null
	if path=="" or not ResourceLoader.exists(path): return
	pet=(load(path) as PackedScene).instantiate() as Node3D
	var length:=1.1
	for p in PETS:
		if p.asset==path: length=float(p.get("length",1.1))
	add_child(pet); ModelFix.double_sided(pet)
	pet.position=PET_SPOT+Vector3(0,ModelFix.fit_pet(pet,length*ACTOR_SCALE),0) # real dog size
	ModelFix.play_animation(pet,"Dog_Idle")
	# Contact shadow under the dog, sized to its body length.
	pet_shadow=_blob_shadow(Vector2(length*0.95,length*0.6),Vector3(PET_SPOT.x,0.022,PET_SPOT.z))

func drag(dx: float) -> void:
	spin+=dx*0.012; spin_velocity=dx*0.012*60.0

func _process(delta: float) -> void:
	if not visible: return
	time+=delta
	pet_zoom=move_toward(pet_zoom,1.0 if focus_pets else 0.0,delta*1.6)
	# The hanging lamp buzzes and the table lantern breathes — the den runs on a generator.
	if bulb_light:
		# Softer buzz so the floor never looks like it is strobing.
		var f:=0.92+0.08*(0.6*sin(time*11.0)+0.4*sin(time*27.7+1.3))
		bulb_light.light_energy=3.3*f; bulb_mat.emission_energy_multiplier=2.4*f
	if ember_light:
		var g:=0.72+0.28*(0.5*sin(time*6.3)+0.5*sin(time*15.1+0.7))
		ember_light.light_energy=0.85*g; ember_mat.emission_energy_multiplier=2.0*g
	intro_turn=maxf(0.0,intro_turn-delta*1.8)
	if absf(spin_velocity)>0.01:
		spin+=spin_velocity*delta; spin_velocity=lerpf(spin_velocity,0.0,1.0-exp(-delta*3.0))
	else:
		# Ease back to facing the camera when the player lets go.
		spin=lerp_angle(spin,0.0,1.0-exp(-delta*1.2))
	# On the pets tab the drag spins the dog; on the survivors tab it spins the survivor.
	var spin_pet: bool=focus_pets and is_instance_valid(pet)
	if is_instance_valid(actor):
		var t:=intro_turn*intro_turn*(3.0-2.0*intro_turn)
		actor.rotation.y=(0.0 if spin_pet else spin)+t*1.1
		actor.position.y=STAND.y+t*0.06 # settles down onto the rug as the turn finishes
	if is_instance_valid(pet):
		if spin_pet: pet.rotation.y=spin
		else: pet.rotation.y=lerp_angle(pet.rotation.y,0.0,1.0-exp(-delta*1.2))

func _mat(color: Color,rough:=0.8,metal:=0.0) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new(); m.albedo_color=color; m.roughness=rough; m.metallic=metal; return m

func _box(name: String,pos: Vector3,size: Vector3,color: Color,rough:=0.82,metal:=0.0) -> MeshInstance3D:
	var node:=MeshInstance3D.new(); node.name=name; var mesh:=BoxMesh.new(); mesh.size=size; node.mesh=mesh
	node.position=pos; node.material_override=_mat(color,rough,metal); add_child(node); return node

func _label(text: String,pos: Vector3,size: int,color: Color) -> void:
	var label:=Label3D.new(); label.text=text; label.font_size=size; label.pixel_size=.0045
	label.position=pos; label.modulate=color; label.outline_size=4; label.outline_modulate=Color("101719"); add_child(label)

# Ink handwriting on pinned paper: black, no outline, small enough to stay on the sheet.
func _paper_label(text: String,pos: Vector3,size: int,color: Color) -> void:
	var label:=Label3D.new(); label.text=text; label.font_size=size; label.pixel_size=.0022
	label.position=pos; label.modulate=color; label.outline_size=0; add_child(label)

func _cyl(name: String,pos: Vector3,r: float,h: float,color: Color,rough:=0.8,metal:=0.0,segments:=20) -> MeshInstance3D:
	var node:=MeshInstance3D.new(); node.name=name; var mesh:=CylinderMesh.new()
	mesh.top_radius=r; mesh.bottom_radius=r; mesh.height=h; mesh.radial_segments=segments
	node.mesh=mesh; node.position=pos; node.material_override=_mat(color,rough,metal); add_child(node); return node

func _ball(name: String,pos: Vector3,squash: Vector3,color: Color,rough:=1.0) -> MeshInstance3D:
	var node:=MeshInstance3D.new(); node.name=name; var mesh:=SphereMesh.new()
	mesh.radius=0.5; mesh.height=1.0; mesh.radial_segments=16; mesh.rings=8
	node.mesh=mesh; node.position=pos; node.scale=squash; node.material_override=_mat(color,rough); add_child(node); return node

func _glow(node: MeshInstance3D,color: Color,energy: float) -> StandardMaterial3D:
	var m:=node.material_override as StandardMaterial3D
	m.emission_enabled=true; m.emission=color; m.emission_energy_multiplier=energy; return m

func _build_set() -> void:
	# "Stay Alive" safehouse: a fortified warehouse lounge. Leather couch and coffee table
	# under a STAY ALIVE banner, a wall of pinned maps and photos, a humming TV, supply
	# shelves, an EXIT door with a green sign, sandbags and barrels, a mezzanine loft and
	# one industrial lamp buzzing over the big red rug. The survivor just stands at home.
	var ground:=MeshInstance3D.new(); var plane:=PlaneMesh.new(); plane.size=Vector2(18,18); ground.mesh=plane
	ground.material_override=_mat(Color("2b2823"),0.96); add_child(ground)
	# Damp stains and patches on the concrete floor.
	for s in [[-1.4,-1.7,1.3,0.9,8.0],[1.6,-0.6,1.0,0.7,-14.0],[-0.3,1.3,1.6,0.8,22.0],[2.3,1.6,0.8,0.6,4.0],[-2.6,0.9,0.9,0.7,-30.0]]:
		var stain:=_box("Floor stain",Vector3(s[0],0.002,s[1]),Vector3(s[2],0.004,s[3]),Color("211f1b"),1.0)
		stain.rotation.y=deg_to_rad(s[4])
	# Tall warehouse shell: dark timber walls, high ceiling with exposed beams.
	_box("Back wall",Vector3(0,2.75,-3.35),Vector3(9,5.5,.22),Color("382f27"),0.93)
	_box("Left wall",Vector3(-4.4,2.75,0),Vector3(.20,5.5,7.4),Color("322b24"),0.93)
	_box("Right wall",Vector3(4.4,2.75,0),Vector3(.20,5.5,7.4),Color("322b24"),0.93)
	_box("Ceiling",Vector3(0,5.52,0),Vector3(9,.18,7.6),Color("241f1a"),0.95)
	_box("Wainscot",Vector3(0,0.65,-3.21),Vector3(8.8,1.3,.04),Color("43362a"),0.9)
	for x in [-2.2,-0.75,0.75,2.2]: _box("Wall stud",Vector3(x,2.75,-3.19),Vector3(.09,5.5,.06),Color("2e261e"),0.9)
	for z in [-2.6,-0.6,1.4]: _box("Ceiling beam",Vector3(0,5.3,z),Vector3(8.8,.22,.18),Color("2e2620"),0.9)
	_box("Baseboard",Vector3(0,0.07,-3.23),Vector3(8.8,.14,.05),Color("26221c"),0.95)
	# High industrial windows leaking cold night — the only blue in a warm room.
	for wx in [-2.1,2.1]:
		_box("Window recess",Vector3(wx,3.45,-3.28),Vector3(1.0,1.1,.08),Color("16181a"),0.9)
		var pane:=_box("Night pane",Vector3(wx,3.45,-3.26),Vector3(0.86,0.96,.02),Color("3d4f60"),0.4)
		_glow(pane,Color("6b87a3"),1.1)
		_box("Window mullion v",Vector3(wx,3.45,-3.24),Vector3(.04,0.96,.02),Color("16181a"),0.8)
		_box("Window mullion h",Vector3(wx,3.45,-3.24),Vector3(.86,.04,.02),Color("16181a"),0.8)
	var moon:=OmniLight3D.new(); moon.position=Vector3(-1.9,3.8,-2.5); moon.light_color=Color("7d9dbd")
	moon.light_energy=1.0; moon.omni_range=5.0; add_child(moon)
	# Mezzanine loft on the right with a plank railing — somebody sleeps up there.
	_box("Loft deck",Vector3(2.75,3.02,-2.35),Vector3(2.9,.14,2.0),Color("4a3b2a"),0.85)
	_box("Loft beam",Vector3(1.32,2.86,-2.35),Vector3(.16,.32,2.0),Color("3a2e22"),0.85)
	_cyl("Loft post",Vector3(1.32,1.5,-1.45),0.06,2.9,Color("3a2e22"),0.85)
	_cyl("Loft rail top",Vector3(2.75,3.85,-1.38),0.03,2.8,Color("4a3b2a"),0.8).rotation.z=deg_to_rad(90)
	_cyl("Loft rail mid",Vector3(2.75,3.5,-1.38),0.022,2.8,Color("4a3b2a"),0.8).rotation.z=deg_to_rad(90)
	for i in range(8): _cyl("Loft baluster",Vector3(1.5+i*0.36,3.44,-1.38),0.02,0.82,Color("443627"),0.8)
	# Warm lamp glow up on the loft.
	var loft_lamp:=OmniLight3D.new(); loft_lamp.position=Vector3(2.6,3.9,-2.3); loft_lamp.light_color=Color("ffab5e")
	loft_lamp.light_energy=0.8; loft_lamp.omni_range=3.0; add_child(loft_lamp)
	# Torn cloth strips hanging from the rafters (left).
	for cs in [[-2.35,4.6,0.55,-4.0],[-2.05,4.55,0.4,3.0],[-2.6,4.5,0.35,-8.0]]:
		var strip:=_box("Hanging cloth",Vector3(cs[0],cs[1]-cs[2]/2,-3.1),Vector3(.28,cs[2],.02),Color("6b5a48"),1.0)
		strip.rotation.z=deg_to_rad(cs[3])
	# STAY ALIVE banner over the map wall — the heart of the room.
	var banner:=_box("Banner",Vector3(0,2.46,-3.13),Vector3(2.4,.56,.025),Color("4e201b"),0.95); banner.rotation.z=deg_to_rad(-1.5)
	_label("STAY ALIVE",Vector3(0,2.44,-3.09),48,Color("b8ac9a"))
	# Map wall: the big evac map plus pinned papers, photos and route pins.
	var map:=_box("Pinned map",Vector3(0,1.85,-3.18),Vector3(1.0,.72,.018),Color("8f8674"),1.0); map.rotation.z=deg_to_rad(-1.0)
	_paper_label("EVAC ROUTE",Vector3(0,2.12,-3.15),13,Color("2b2620"))
	for mp in [[-0.38,0.2],[-0.08,-0.24],[0.32,0.22],[0.24,-0.22]]:
		_ball("Map route dot",Vector3(mp[0],1.85+mp[1],-3.15),Vector3(.026,.026,.02),Color("8e2a22"),0.6)
	var papers:=[[-0.78,2.14,.26,.32,"9a917c",-6.0],[0.78,2.12,.24,.3,"8d8471",4.0],[-0.8,1.56,.24,.28,"948a76",3.0],[0.8,1.6,.26,.34,"9a917c",-3.0],[-0.56,2.32,.18,.22,"857c69",8.0],[0.58,2.34,.2,.24,"948a76",-7.0]]
	for p in papers:
		var sheet:=_box("Pinned paper",Vector3(p[0],p[1],-3.15),Vector3(p[2],p[3],.012),Color(p[4]),1.0)
		sheet.rotation.z=deg_to_rad(p[5])
	for f in [[-0.62,1.86,.16,.2],[0.64,1.9,.17,.22],[-0.26,1.42,.14,.18],[0.3,1.4,.15,.19]]:
		var photo:=_box("Pinned photo",Vector3(f[0],f[1],-3.14),Vector3(f[2],f[3],.01),Color("33363c"),1.0)
		photo.rotation.z=deg_to_rad(f[0]*9.0)
	_ball("Map pin",Vector3(-0.44,2.12,-3.14),Vector3(.03,.03,.02),Color("a02c22"),0.5)
	_ball("Map pin 2",Vector3(0.42,2.08,-3.14),Vector3(.028,.028,.02),Color("a02c22"),0.5)
	_paper_label("2 CANS\nLEFT",Vector3(0.8,1.62,-3.14),11,Color("2b2620"))
	# The leather couch — scuffed, sagging, home.
	var leather:=Color("4e3018"); var cushion:=Color("583a20")
	_box("Couch base",Vector3(0,0.28,-2.42),Vector3(2.3,.34,.95),leather,0.62)
	_box("Couch back",Vector3(0,0.85,-2.8),Vector3(2.3,.68,.26),leather,0.62)
	for sx in [-1.0,1.0]: _box("Couch arm",Vector3(sx,0.56,-2.42),Vector3(.3,.58,.95),Color("462c16"),0.62)
	for sx in [-0.48,0.48]: _box("Couch seat",Vector3(sx,0.56,-2.36),Vector3(.9,.18,.78),cushion,0.7)
	for sx in [-0.48,0.48]:
		var back:=_box("Couch cushion",Vector3(sx,0.94,-2.68),Vector3(.92,.44,.2),cushion,0.7)
		back.rotation.x=deg_to_rad(-8.0)
	for sx in [-1.0,1.0]: for sz in [-2.75,-2.1]: _box("Couch leg",Vector3(sx,0.06,sz),Vector3(.07,.12,.07),Color("241a10"),0.8)
	# Coffee table: crate planks, a lantern, mugs and tomorrow's plan.
	_box("Table top",Vector3(0.05,0.4,-1.35),Vector3(1.15,.08,.6),Color("4c3a28"),0.85)
	_box("Table shelf",Vector3(0.05,0.16,-1.35),Vector3(1.0,.05,.5),Color("43331f"),0.85)
	for dx in [-0.5,0.5]: for dz in [-0.24,0.24]: _box("Table leg",Vector3(0.05+dx,0.2,-1.35+dz),Vector3(.07,.4,.07),Color("3a2c1c"),0.85)
	_box("Table papers",Vector3(0.32,0.45,-1.28),Vector3(.3,.015,.4),Color("b8b0a0"),1.0).rotation.y=deg_to_rad(6.0)
	_cyl("Enamel mug",Vector3(0.42,0.49,-1.5),0.045,0.1,Color("b9bfba"),0.5,0.2)
	_cyl("Enamel mug 2",Vector3(0.2,0.49,-1.55),0.045,0.1,Color("6e3b2f"),0.5,0.2)
	# The lantern on the table breathes (ember flicker channel).
	_cyl("Lantern base",Vector3(-0.32,0.52,-1.35),0.075,0.16,Color("2f2b26"),0.6,0.5)
	ember_mat=_glow(_ball("Lantern glass",Vector3(-0.32,0.63,-1.35),Vector3(.068,.085,.068),Color("d88a4a"),0.4),Color("ff9e4e"),2.0)
	_cyl("Lantern cap",Vector3(-0.32,0.71,-1.35),0.052,0.05,Color("2f2b26"),0.6,0.5)
	_cyl("Lantern chimney",Vector3(-0.32,0.76,-1.35),0.018,0.06,Color("24211d"),0.6,0.5)
	ember_light=OmniLight3D.new(); ember_light.position=Vector3(-0.32,0.85,-1.3); ember_light.light_color=Color("ff9e4e")
	ember_light.light_energy=0.85; ember_light.omni_range=2.8; add_child(ember_light)
	# Big red rug underfoot — worn centre, dark border.
	var rug:=_box("Old rug",Vector3(0.1,0.013,0.2),Vector3(2.7,.012,2.1),Color("5e2f26"),1.0); rug.rotation.y=deg_to_rad(2.0)
	_box("Rug border",Vector3(0.1,0.004,0.2),Vector3(2.76,.006,2.16),Color("3f241d"),1.0).rotation.y=deg_to_rad(2.0)
	_box("Rug inset",Vector3(0.1,0.021,0.2),Vector3(2.1,.003,1.55),Color("683730"),1.0).rotation.y=deg_to_rad(2.0)
	_box("Rug medallion",Vector3(0.1,0.023,0.2),Vector3(.9,.002,.7),Color("57302a"),1.0).rotation.y=deg_to_rad(2.0)
	for ws in [[-0.6,0.4],[0.65,-0.45],[0.25,0.65],[-0.3,-0.6]]:
		_box("Rug wear",Vector3(0.1+ws[0],0.024,0.2+ws[1]),Vector3(.45,.002,.32),Color("4c2a22"),1.0).rotation.y=deg_to_rad(2.0+ws[0]*20.0)
	# Industrial lamp on a cord buzzing over the rug (bulb flicker channel).
	_cyl("Lamp cord",Vector3(0.15,4.35,0.35),0.014,2.2,Color("17181a"),0.9)
	var shade:=MeshInstance3D.new(); var smesh:=CylinderMesh.new(); smesh.top_radius=0.06; smesh.bottom_radius=0.24; smesh.height=0.2; smesh.radial_segments=24
	shade.mesh=smesh; shade.position=Vector3(0.15,3.32,0.35); shade.material_override=_mat(Color("2f3233"),0.55,0.6); add_child(shade)
	bulb_mat=_glow(_ball("Lamp bulb",Vector3(0.15,3.24,0.35),Vector3(.1,.12,.1),Color("ffc98c"),0.3),Color("ffc98c"),2.4)
	bulb_light=SpotLight3D.new(); bulb_light.position=Vector3(0.15,3.26,0.35); bulb_light.light_color=Color("ffc384")
	bulb_light.light_energy=3.3; bulb_light.spot_range=9.0; bulb_light.spot_angle=46.0; add_child(bulb_light)
	bulb_light.look_at_from_position(ORIGIN+Vector3(0.15,3.26,0.35),ORIGIN+Vector3(0.15,0.6,0.1))
	# TV on a crate, tuned to a dead city's last broadcast.
	_box("TV crate",Vector3(-1.8,0.32,-2.5),Vector3(.85,.64,.7),Color("57503f"),0.9)
	_box("TV body",Vector3(-1.8,0.98,-2.5),Vector3(.85,.58,.12),Color("1d1f22"),0.6,0.3)
	var screen:=_box("TV screen",Vector3(-1.8,0.98,-2.44),Vector3(.72,.46,.02),Color("8fb0c9"),0.35)
	_glow(screen,Color("9fc2dd"),1.7)
	for i in range(3): _box("TV skyline",Vector3(-2.02+i*0.2,0.86+i*0.05,-2.43),Vector3(.14,.1+i*0.08,.015),Color("2c3644"),0.9)
	var tv_glow:=OmniLight3D.new(); tv_glow.position=Vector3(-1.8,1.1,-2.1); tv_glow.light_color=Color("9fc2dd")
	tv_glow.light_energy=0.6; tv_glow.omni_range=2.2; add_child(tv_glow)
	# Fridge in the corner (left edge of frame).
	_box("Fridge",Vector3(-2.75,0.95,-2.9),Vector3(.72,1.9,.66),Color("6a6f66"),0.6,0.35)
	_box("Fridge seam",Vector3(-2.75,1.32,-2.56),Vector3(.66,.02,.02),Color("4a4f47"),0.6,0.35)
	_box("Fridge handle",Vector3(-2.42,1.0,-2.56),Vector3(.04,.5,.04),Color("3c403a"),0.5,0.5)
	# Supply shelf left of the couch: jars, cans and the red first-aid cabinet.
	for y in [1.0,1.56]: _box("Shelf board",Vector3(-1.35,y,-3.05),Vector3(1.0,.05,.42),Color("4c3d2c"),0.85)
	for x in [-1.8,-0.9]: _box("Shelf upright",Vector3(x,1.28,-3.05),Vector3(.06,1.16,.42),Color("3a3126"),0.85)
	var jars:=[[-1.68,1.06,"7a6b4a"],[-1.5,1.06,"5c6148"],[-1.32,1.06,"6e3b2f"],[-1.14,1.06,"8a7a55"],[-1.6,1.62,"4a5560"],[-1.4,1.62,"7a6b4a"],[-1.2,1.62,"5c6148"]]
	for c in jars: _cyl("Jar",Vector3(c[0],c[1]+0.06,-3.05),0.045,0.13,Color(c[2]),0.55,0.15)
	_box("First aid cabinet",Vector3(-1.35,2.0,-3.08),Vector3(.4,.34,.14),Color("8e2a22"),0.6)
	_box("First aid cross v",Vector3(-1.35,2.0,-3.04),Vector3(.06,.18,.02),Color("d8d2c4"),0.7)
	_box("First aid cross h",Vector3(-1.35,2.0,-3.04),Vector3(.18,.06,.02),Color("d8d2c4"),0.7)
	# EXIT door on the right, green sign humming over a mesh window.
	_box("Door frame",Vector3(2.0,1.18,-3.22),Vector3(1.1,2.36,.18),Color("2c2a26"),0.9)
	_box("Door",Vector3(2.0,1.13,-3.16),Vector3(.92,2.2,.08),Color("3d4438"),0.8)
	_box("Door window",Vector3(2.0,1.62,-3.12),Vector3(.5,.62,.02),Color("23303c"),0.5)
	for i in range(4): _box("Door mesh v",Vector3(1.82+i*0.12,1.62,-3.11),Vector3(.015,.62,.012),Color("181c20"),0.7,0.4)
	for i in range(5): _box("Door mesh h",Vector3(2.0,1.36+i*0.13,-3.11),Vector3(.5,.015,.012),Color("181c20"),0.7,0.4)
	_box("Door handle",Vector3(1.62,1.1,-3.1),Vector3(.05,.16,.05),Color("6a6f66"),0.5,0.6)
	var exit_sign:=_box("EXIT sign",Vector3(2.0,2.5,-3.14),Vector3(.46,.18,.06),Color("12351c"),0.5)
	_glow(exit_sign,Color("1d5c32"),1.4)
	_label("EXIT",Vector3(2.0,2.48,-3.1),30,Color("7dff9a"))
	var exit_glow:=OmniLight3D.new(); exit_glow.position=Vector3(2.0,2.55,-2.9); exit_glow.light_color=Color("4dd07f")
	exit_glow.light_energy=0.5; exit_glow.omni_range=1.8; add_child(exit_glow)
	# Sandbag nest guarding the door.
	for sb in [[1.55,0.16,-0.9],[2.0,0.16,-0.72],[1.75,0.16,-1.25],[2.2,0.16,-1.05],[1.6,0.45,-0.95],[1.95,0.44,-1.1]]:
		var bag:=_ball("Sandbag",Vector3(sb[0],sb[1],sb[2]),Vector3(.66,.32,.44),Color("6a5c43"))
		bag.rotation.y=deg_to_rad(sb[0]*37.0)
	# Fuel barrels by the door.
	_cyl("Barrel",Vector3(2.6,0.46,-1.75),0.3,0.92,Color("4a3b2a"),0.7,0.4,24)
	_cyl("Barrel rim",Vector3(2.6,0.9,-1.75),0.31,0.04,Color("33291d"),0.65,0.5,24)
	_cyl("Barrel 2",Vector3(2.95,0.42,-2.2),0.28,0.84,Color("3d4148"),0.7,0.4,24)
	# Crate stacks in the foreground corners.
	_box("Crate L1",Vector3(-1.95,0.28,1.15),Vector3(.7,.56,.6),Color("57503f"),0.9)
	_box("Crate L2",Vector3(-1.85,0.82,1.2),Vector3(.55,.5,.5),Color("4c4636"),0.9).rotation.y=deg_to_rad(9.0)
	_box("Crate R1",Vector3(2.1,0.26,0.9),Vector3(.66,.52,.56),Color("57503f"),0.9)
	# Backpack dumped by the couch — always ready to run.
	_ball("Backpack",Vector3(-1.3,0.24,-2.5),Vector3(.26,.34,.22),Color("4c4636"),0.95)
	_cyl("Backpack roll",Vector3(-1.3,0.44,-2.5),0.07,0.24,Color("5c6148"),0.95).rotation.z=deg_to_rad(90)
	# Cool rim light from the window side so the survivor reads against the gloom.
	var rim:=OmniLight3D.new(); rim.position=Vector3(0.2,2.1,-2.4); rim.light_color=Color("5d7488")
	rim.light_energy=0.4; rim.omni_range=3.5; add_child(rim)
	# Gentle frontal fill so faces and hands stay readable in the gloom.
	var fill:=OmniLight3D.new(); fill.position=Vector3(0,1.65,3.3); fill.light_color=Color("d9c9b8")
	fill.light_energy=0.38; fill.omni_range=5.5; add_child(fill)
