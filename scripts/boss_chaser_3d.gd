extends Node3D
## The opening pursuer: an original high-detail muscular abomination, not the old
## Juggernaut or BossSculpt. Its fitted skeleton and custom heavy run are embedded
## together so runtime retargeting cannot tear the skin.

const MODEL_PATH:="res://assets/models/actors/pursuer_abomination.glb"
const SCALE:=1.95

var model: Node3D
var anim: AnimationPlayer
var stomp_time:=0.0

func _ready() -> void:
	model=load(MODEL_PATH).instantiate() as Node3D
	model.scale=Vector3.ONE*SCALE
	model.rotation.y=PI # faces -Z, down the road after the survivor
	add_child(model)
	anim=model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	if is_instance_valid(anim) and anim.has_animation("Pursuer_Run"):
		var clip:=anim.get_animation("Pursuer_Run")
		clip.loop_mode=Animation.LOOP_LINEAR
		anim.speed_scale=0.78 # heavy, long strides for its size
		anim.play("Pursuer_Run")
	else:
		push_error("Pursuer custom run animation is missing")
	for m in model.find_children("*","MeshInstance3D",true,false):
		(m as MeshInstance3D).cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON

func height() -> float:
	return 1.84*SCALE
