extends Node3D
## Character lobby: the chosen survivor stands full-body on a lit platform in an idle loop,
## like a fitting room. Characters (and later skins) swap in with a short turn; dragging spins
## the model. Pets get their own slot beside the character once their models exist.

const AnimLibrary=preload("res://scripts/anim_library.gd")
const ArmsRelaxed=preload("res://scripts/arms_relaxed.gd")
const GunGripIK=preload("res://scripts/gun_grip_ik.gd")
const CHARACTERS:=[
	{"asset":"res://assets/models/actors/survivor_male_universal.glb","name":"MASON"},
	{"asset":"res://assets/models/actors/survivor_female_universal.glb","name":"RILEY","palm_twist":90.0}]
const ORIGIN:=Vector3(-200,0,0) # far from the road so nothing from the run leaks into the shot
const STAND:=Vector3(0,0.18,0)  # top of the platform
const CAMERA_POS:=Vector3(0.0,1.3,5.4)
const CAMERA_TARGET:=Vector3(0.0,0.98,0.0) # full body sits in the open window between the HUD bars
const CAMERA_FOV:=34.0
const PET_SPOT:=Vector3(0.95,0.18,0.35) # where a pet will sit beside the survivor

var actor: Node3D
var actor_anim: AnimationPlayer
var actor_index:=-1
var spin:=0.0          # user drag rotation
var spin_velocity:=0.0
var intro_turn:=0.0    # eases a newly selected character into facing the camera
var time:=0.0
var pet: Node3D

func _ready() -> void:
	position=ORIGIN
	_build_set()

func camera_position() -> Vector3:
	return ORIGIN+CAMERA_POS+Vector3(sin(time*0.3)*0.04,sin(time*0.45)*0.02,0)

func camera_target() -> Vector3:
	return ORIGIN+CAMERA_TARGET

func show_character(index: int) -> void:
	index=clampi(index,0,CHARACTERS.size()-1)
	if index==actor_index and is_instance_valid(actor): return
	if is_instance_valid(actor): actor.queue_free()
	actor_index=index
	actor=(load(CHARACTERS[index].asset) as PackedScene).instantiate() as Node3D
	actor.position=STAND
	add_child(actor)
	actor_anim=actor.find_child("AnimationPlayer",true,false) as AnimationPlayer
	if actor_anim: actor_anim.stop() # the lobby is a static, natural standing pose only
	var skeleton:=actor.find_child("Skeleton3D",true,false) as Skeleton3D
	if skeleton:
		skeleton.reset_bone_poses()
		var arms:=ArmsRelaxed.new(); arms.body=actor
		arms.hand_offset={"r":GunGripIK.mesh_offset(actor,"hand_r"),"l":GunGripIK.mesh_offset(actor,"hand_l")}
		arms.setup_from_model(actor,skeleton)
		arms.palm_twist_deg=0.0
		skeleton.add_child(arms) # straight wrists, relaxed arms, palms facing the thighs
	intro_turn=1.0; spin=0.0; spin_velocity=0.0

## Pets are modelled separately; pass a scene path once one exists.
func show_pet(path: String) -> void:
	if is_instance_valid(pet): pet.queue_free(); pet=null
	if path=="" or not ResourceLoader.exists(path): return
	pet=(load(path) as PackedScene).instantiate() as Node3D
	pet.position=PET_SPOT; add_child(pet)

func drag(dx: float) -> void:
	spin+=dx*0.012; spin_velocity=dx*0.012*60.0

func _process(delta: float) -> void:
	if not visible: return
	time+=delta
	intro_turn=maxf(0.0,intro_turn-delta*1.8)
	if absf(spin_velocity)>0.01:
		spin+=spin_velocity*delta; spin_velocity=lerpf(spin_velocity,0.0,1.0-exp(-delta*3.0))
	else:
		# Ease back to facing the camera when the player lets go.
		spin=lerp_angle(spin,0.0,1.0-exp(-delta*1.2))
	if is_instance_valid(actor):
		var t:=intro_turn*intro_turn*(3.0-2.0*intro_turn)
		actor.rotation.y=spin+t*1.1
		actor.position.y=STAND.y-t*0.05

func _mat(color: Color,rough:=0.8,metal:=0.0) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new(); m.albedo_color=color; m.roughness=rough; m.metallic=metal; return m

func _box(name: String,pos: Vector3,size: Vector3,color: Color,rough:=0.82,metal:=0.0) -> MeshInstance3D:
	var node:=MeshInstance3D.new(); node.name=name; var mesh:=BoxMesh.new(); mesh.size=size; node.mesh=mesh
	node.position=pos; node.material_override=_mat(color,rough,metal); add_child(node); return node

func _label(text: String,pos: Vector3,size: int,color: Color) -> void:
	var label:=Label3D.new(); label.text=text; label.font_size=size; label.pixel_size=.0045
	label.position=pos; label.modulate=color; label.outline_size=4; label.outline_modulate=Color("101719"); add_child(label)

func _build_set() -> void:
	# A purpose-built safehouse briefing room, not the supply-truck set.
	var ground:=MeshInstance3D.new(); var plane:=PlaneMesh.new(); plane.size=Vector2(18,18); ground.mesh=plane
	ground.material_override=_mat(Color("20282b"),0.76,0.08); add_child(ground)
	_box("Reinforced back wall",Vector3(0,2.3,-3.6),Vector3(9,4.6,.22),Color("253136"))
	_box("Left safehouse wall",Vector3(-4.4,2.3,0),Vector3(.20,4.6,7.4),Color("202a2e"))
	_box("Right safehouse wall",Vector3(4.4,2.3,0),Vector3(.20,4.6,7.4),Color("202a2e"))
	for x in [-2.75,0.0,2.75]:
		_box("Wall armour panel",Vector3(x,1.90,-3.45),Vector3(2.58,3.45,.10),Color("303d42"),.72,.18)
		_box("Panel lower seam",Vector3(x,.45,-3.36),Vector3(2.38,.035,.035),Color("121a1d"))
	for x in [-2.15,2.15]:
		var strip:=_box("Vertical briefing light",Vector3(x,2.0,-3.31),Vector3(.055,2.55,.055),Color("80cbd2"),.35,.15)
		var sm:=strip.material_override as StandardMaterial3D; sm.emission_enabled=true; sm.emission=Color("72c5d0"); sm.emission_energy_multiplier=1.25
	_box("Overhead lintel",Vector3(0,3.92,-3.30),Vector3(6.4,.15,.34),Color("141d20"),.55,.35)
	_label("DEAD FRONTIER",Vector3(0,3.28,-3.30),72,Color("d6dedd"))
	_label("SURVIVOR  /  BRIEFING",Vector3(0,2.92,-3.29),32,Color("80b5ba"))
	for x in [-1.28,1.28]: _box("Floor guidance inset",Vector3(x,.008,-1.25),Vector3(.035,.012,3.7),Color("52666a"),.72,.20)
	for side in [-1,1]:
		_box("Ventilation surround",Vector3(side*3.25,.85,-3.28),Vector3(.72,.72,.10),Color("182226"),.68,.35)
		for i in range(6): _box("Ventilation louvre",Vector3(side*3.25,.60+i*.10,-3.20),Vector3(.58,.035,.06),Color("526166"),.55,.45)
	# Platform: brushed steel disc with a restrained red perimeter.
	var disc:=MeshInstance3D.new(); var cyl:=CylinderMesh.new(); cyl.top_radius=.84; cyl.bottom_radius=.89; cyl.height=.18; cyl.radial_segments=64
	disc.mesh=cyl; disc.position=Vector3(0,.09,0); disc.material_override=_mat(Color("343d40"),.42,.68); add_child(disc)
	var rim:=MeshInstance3D.new(); var torus:=TorusMesh.new(); torus.inner_radius=.84; torus.outer_radius=.875; torus.rings=64; rim.mesh=torus
	var rim_mat:=_mat(Color("a72e29")); rim_mat.emission_enabled=true; rim_mat.emission=Color("e94237"); rim_mat.emission_energy_multiplier=.45
	rim.material_override=rim_mat; rim.position=Vector3(0,.18,0); add_child(rim)
	# Neutral key, cool rim and gentle frontal fill keep both hands and faces readable.
	var key:=SpotLight3D.new(); key.position=Vector3(-1.6,3.2,2.6); key.light_color=Color("ffe7cb"); key.light_energy=2.7
	key.spot_range=8.0; key.spot_angle=34.0; add_child(key)
	key.look_at_from_position(ORIGIN+Vector3(-1.6,3.2,2.6),ORIGIN+Vector3(0,1.0,0))
	var rim_light:=OmniLight3D.new(); rim_light.position=Vector3(1.2,2.2,-1.4); rim_light.light_color=Color("80d1da")
	rim_light.light_energy=1.35; rim_light.omni_range=4.0; add_child(rim_light)
	var top:=OmniLight3D.new(); top.position=Vector3(0,2.8,.6); top.light_color=Color("fff4e8"); top.light_energy=1.0; top.omni_range=3.5; add_child(top)
	var fill:=OmniLight3D.new(); fill.position=Vector3(0,1.55,3.1); fill.light_color=Color("dce8e8"); fill.light_energy=.65; fill.omni_range=5.0; add_child(fill)
	var red:=OmniLight3D.new(); red.position=Vector3(0,.35,.9); red.light_color=Color("ff4a3a"); red.light_energy=.32; red.omni_range=1.5; add_child(red)
