extends RefCounted
## Persistent disaster storytelling on every city block. Nothing here depends on a
## player kill: dried blood, drag marks, filth and rubble already cover the street.

static var materials: Dictionary={}

static func apply(road: Node3D,index: int,zombie_script: GDScript) -> void:
	var root:=Node3D.new(); root.name="DisasterDressing"; road.add_child(root)
	var rng:=RandomNumberGenerator.new(); rng.seed=741103+index*7919
	# Sparse, faint dried stains: most blocks remain completely clean.
	if index%5==0:
		var pos:=Vector3(rng.randf_range(-2.9,2.9),0.018,rng.randf_range(-6.8,6.8))
		var color:=Color(0.34,0.17,0.13,0.34)
		_irregular_patch(root,pos,rng.randf_range(.18,.38),rng.randf_range(.28,.58),color,rng,24)
		for drop in range(2):
			var p:=pos+Vector3(rng.randf_range(-.48,.48),0.001,rng.randf_range(-.55,.55))
			_irregular_patch(root,p,rng.randf_range(.018,.045),rng.randf_range(.025,.060),color,rng,10)
	if index%7==3:
		var side:=-1 if index%2==0 else 1
		var pos:=Vector3(side*rng.randf_range(4.8,6.7),0.158,rng.randf_range(-6.5,6.5))
		_irregular_patch(root,pos,.30,.52,Color(0.20,0.18,0.15,0.20),rng,20)
	# One small, grouped debris site every few blocks, not a continuous carpet.
	if index%4==2:
		_scatter_debris(root,-1 if index%8==2 else 1,rng)
	# Ambient watchers on the pavement: some stand and sway, some sit slumped on a crate, all
	# watching the road. They can be shot (kills and coins count) and travel with the city loop.
	if index%2==0:
		spawn_watcher(road,index,zombie_script,rng)

const AnimLibrary=preload("res://scripts/anim_library.gd")
const LegsOut=preload("res://scripts/legs_out.gd")

static func spawn_watcher(road: Node3D,index: int,zombie_script: GDScript,rng: RandomNumberGenerator) -> Node3D:
	var side:=-1 if (index/2)%2==0 else 1
	var watcher: Node3D=zombie_script.new()
	watcher.configure("walker",1.0)
	watcher.set_meta("watcher",true)
	watcher.speed=0.0
	watcher.position=Vector3(side*rng.randf_range(5.0,5.6),0.16,rng.randf_range(-5.8,5.8))
	watcher.model.rotation.y=-side*PI/2+rng.randf_range(-0.35,0.35) # facing the road
	var anim: AnimationPlayer=watcher.animation_player
	var sitting:=rng.randf()<0.5
	if sitting and is_instance_valid(anim):
		var clip:=AnimLibrary.borrow(anim,"Sitting_Idle")
		var skel:=watcher.model.find_child("Skeleton3D",true,false) as Skeleton3D
		if clip!="" and skel:
			# Slumped on the pavement: seated upper body, legs laid out along the ground.
			var legs:=LegsOut.new(); legs.body=watcher.model; skel.add_child(legs)
			watcher.model.position.y-=0.40
			anim.get_animation(clip).loop_mode=Animation.LOOP_LINEAR
			anim.play(clip); anim.speed_scale=rng.randf_range(0.8,1.0); anim.seek(rng.randf()*3.0,true)
		else: sitting=false
	if not sitting and is_instance_valid(anim):
		# Standing upright and swaying (the zombie pack's own idle is a half-crouch).
		var idle:=AnimLibrary.borrow(anim,"Idle")
		if idle=="" and anim.has_animation("Zombie_Idle"): idle="Zombie_Idle"
		if idle!="":
			anim.get_animation(idle).loop_mode=Animation.LOOP_LINEAR
			anim.play(idle); anim.speed_scale=rng.randf_range(0.7,0.9); anim.seek(rng.randf()*2.0,true)
	watcher.set_meta("sitting",sitting)
	watcher.set_meta("base_yaw",watcher.model.rotation.y)
	watcher.set_meta("next_act",rng.randf_range(1.0,4.0))
	if is_instance_valid(anim):
		# Extra clips for the little routines in main_3d._tick_watchers.
		for clip_name in (["Sitting_Talking"] if sitting else ["Walk","Idle_Talking"]):
			var c:=AnimLibrary.borrow(anim,clip_name)
			if c!="": anim.get_animation(c).loop_mode=Animation.LOOP_LINEAR
	road.add_child(watcher)
	road.set_meta("watcher",watcher)
	return watcher

static func _material(color: Color,roughness:=0.96) -> StandardMaterial3D:
	var key:=str(color)+str(roughness)
	if materials.has(key): return materials[key]
	var m:=StandardMaterial3D.new(); m.albedo_color=color; m.roughness=roughness
	m.metallic_specular=0.0
	if color.a<0.999: m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode=BaseMaterial3D.CULL_DISABLED
	materials[key]=m; return m

static func _irregular_patch(parent: Node3D,pos: Vector3,rx: float,rz: float,color: Color,rng: RandomNumberGenerator,points: int) -> void:
	var st:=SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var ring: Array[Vector3]=[]
	for i in range(points):
		var angle:=TAU*i/points
		var radius:=rng.randf_range(.68,1.12)
		ring.append(Vector3(cos(angle)*rx*radius,0,sin(angle)*rz*radius))
	for i in range(points):
		st.set_normal(Vector3.UP); st.add_vertex(pos)
		st.set_normal(Vector3.UP); st.add_vertex(pos+ring[(i+1)%points])
		st.set_normal(Vector3.UP); st.add_vertex(pos+ring[i])
	var node:=MeshInstance3D.new(); node.mesh=st.commit(); node.material_override=_material(color)
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF; parent.add_child(node)

static func _drag_stain(parent: Node3D,pos: Vector3,direction: float,length: float,rng: RandomNumberGenerator) -> void:
	var color:=Color("511916")
	for i in range(5):
		var t:=i/4.0
		var p:=pos+Vector3(direction*t*length,0,t*length)
		_irregular_patch(parent,p,.14*(1.0-t*.72),.48,color,rng,12)
		for side in [-1,1]:
			_irregular_patch(parent,p+Vector3(side*.15*(1.0-t*.5),.001,.10),.045,.30,color,rng,8)

const DEBRIS_PATHS:=[
	"res://assets/models/props/debris_concrete_00.glb",
	"res://assets/models/props/debris_concrete_01.glb",
	"res://assets/models/props/debris_brick.glb",
	"res://assets/models/props/debris_board.glb",
	"res://assets/models/props/debris_can.glb",
	"res://assets/models/props/debris_newspaper.glb"
]
static var debris_cache: Dictionary={}

static func _debris(parent: Node3D,pos: Vector3,index: int,rng: RandomNumberGenerator,scale:=1.0) -> void:
	if not debris_cache.has(index):
		var prototype:=load(DEBRIS_PATHS[index]).instantiate() as Node3D
		var meshes:=prototype.find_children("*","MeshInstance3D",true,false)
		var source:=meshes[0] as MeshInstance3D if not meshes.is_empty() else null
		if source==null:
			push_error("Detailed street debris mesh missing: "+DEBRIS_PATHS[index])
			prototype.free(); return
		debris_cache[index]=source.mesh
		prototype.free()
	var node:=MeshInstance3D.new(); node.mesh=debris_cache[index]
	node.position=pos; node.rotation.y=rng.randf_range(0,TAU); node.scale=Vector3.ONE*scale
	if index==4: node.rotation.z=PI/2 # discarded cans lie on their sides
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	parent.add_child(node)

static func _scatter_debris(parent: Node3D,side: int,rng: RandomNumberGenerator) -> void:
	# A single small site: two chips and one paper, with an occasional board or can.
	var center_z:=rng.randf_range(-6.2,6.2)
	for i in range(2):
		var x:=side*rng.randf_range(4.65,5.75)
		_debris(parent,Vector3(x,.155,center_z+rng.randf_range(-.40,.40)),rng.randi_range(0,2),rng,rng.randf_range(.72,1.05))
	_debris(parent,Vector3(side*rng.randf_range(4.8,5.9),.158,center_z+rng.randf_range(-.55,.55)),5,rng,1.0)
	if rng.randf()<.35:
		_debris(parent,Vector3(side*5.25,.16,center_z+.65),3,rng,1.0)
	elif rng.randf()<.35:
		_debris(parent,Vector3(side*5.15,.205,center_z-.55),4,rng,1.0)
