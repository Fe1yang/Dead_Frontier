extends Node3D
## Motionless corpses use the final frame of the authored Death01 clip, not a rotated walk pose.
## The same component serves isolated pavement bodies and physical road-blocking piles.

var seed_value: int=0
var body_count: int=1
var bodies: Array[Node3D]=[]
var _rng:=RandomNumberGenerator.new()

func _ready() -> void:
	_rng.seed=seed_value
	for i in range(body_count):
		_add_body(i)
	_make_blood()

func _make_blood() -> void:
	# One connected irregular pool, plus separated droplets. Everything sits just above
	# the ground and is generated once, so there are no animated decals or z-fighting quads.
	var st:=SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	_add_blood_pool(st,Vector3(0,0.014,0),1.04 if body_count>1 else 0.66,1.34 if body_count>1 else 1.10,32)
	for i in range(8 if body_count>1 else 5):
		var angle: float=_rng.randf_range(0,TAU)
		var distance: float=_rng.randf_range(0.82,1.42) if body_count>1 else _rng.randf_range(0.60,1.14)
		var center:=Vector3(cos(angle)*distance,0.014,sin(angle)*distance)
		_add_blood_pool(st,center,_rng.randf_range(0.035,0.11),_rng.randf_range(0.045,0.16),10)
	var blood:=MeshInstance3D.new()
	blood.name="Dried blood beneath corpses"
	blood.mesh=st.commit()
	var material:=StandardMaterial3D.new()
	material.albedo_color=Color(0.30,0.035,0.025,0.78)
	material.roughness=0.98
	material.metallic_specular=0.0
	material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	material.cull_mode=BaseMaterial3D.CULL_DISABLED
	blood.material_override=material
	blood.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(blood)

func _add_blood_pool(st: SurfaceTool,center: Vector3,rx: float,rz: float,points: int) -> void:
	var ring: Array[Vector3]=[]
	for i in range(points):
		var angle: float=TAU*i/points
		var radius: float=_rng.randf_range(0.72,1.13)
		ring.append(center+Vector3(cos(angle)*rx*radius,0,sin(angle)*rz*radius))
	for i in range(points):
		st.set_normal(Vector3.UP); st.add_vertex(center)
		st.set_normal(Vector3.UP); st.add_vertex(ring[(i+1)%points])
		st.set_normal(Vector3.UP); st.add_vertex(ring[i])

func _add_body(index: int) -> void:
	var female: bool=_rng.randf()<0.42
	var path: String="res://assets/models/actors/zombie_female_universal.glb" if female else "res://assets/models/actors/zombie_walker_universal.glb"
	var body:=Node3D.new()
	body.name="Corpse_%d"%index
	add_child(body)
	var model:=load(path).instantiate() as Node3D
	body.add_child(model)
	var anim:=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	if anim and anim.has_animation("Death01"):
		var clip:=anim.get_animation("Death01")
		anim.play("Death01")
		anim.seek(maxf(0.0,clip.length-0.002),true)
		anim.pause()
	else:
		push_error("Corpse death pose missing: "+path)
	var yaw: float=_rng.randf_range(0.0,TAU)
	var offset:=Vector3.ZERO
	if body_count>1:
		# Offset and alternate the bodies so the pile reads as limbs and torsos, not cloned stacks.
		var pile_offsets: Array=[Vector3(-0.34,0.0,0.12),Vector3(0.36,0.10,-0.16),Vector3(0.02,0.22,0.18),Vector3(0.16,0.30,-0.28)]
		offset=pile_offsets[index%pile_offsets.size()]
		yaw=(index%2)*PI+_rng.randf_range(-0.75,0.75)+index*0.38
	body.position=offset
	body.rotation.y=yaw
	body.rotation.z=_rng.randf_range(-0.035,0.035)
	bodies.append(body)
