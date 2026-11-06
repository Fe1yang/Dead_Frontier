extends SkeletonModifier3D
## Lobby idle life, layered on the static standing pose.
## Always on: slow breathing in the chest only (the shoulders stay still, so the arms never move
## together) and a head that looks around now and then.
## Every few seconds one one-sided action plays: glance at a watch, rest a hand at the belt, roll
## one shoulder, look back over a shoulder, stretch the neck. Arm actions drive ArmsRelaxed's
## per-side `lift` / `bend` (elbow bends forward only, which the forearm skin handles); this node
## moves spine, clavicle, neck and head by a few degrees. Runs before ArmsRelaxed.

var arms: Node # ArmsRelaxed of the same skeleton
var bones:={}
var up:=Vector3.UP
var right:=Vector3.RIGHT
var forward:=Vector3.BACK
var t:=0.0
var last_ms:=0
var rng:=RandomNumberGenerator.new()
# head look (yaw, pitch, roll in degrees): +yaw = toward the character's left, +pitch = up
var look:=Vector3.ZERO
var look_target:=Vector3.ZERO
var look_timer:=1.5
# current action
var action:=""
var side:="l"
var action_t:=0.0
var action_len:=0.0
var rest_timer:=3.0
var last_action:=""

const ACTIONS:={
	"look_back":2.8,  # turn the upper body and look over a shoulder
	"neck":2.6,       # tilt the head to one side, then the other
}

func setup(sk: Skeleton3D) -> void:
	for n in ["spine_01","spine_02","spine_03","clavicle_l","clavicle_r","neck_01","Head","upperarm_l","upperarm_r","pelvis"]:
		bones[n]=sk.find_bone(n)
	if bones.values().any(func(v): return int(v)<0): bones.clear(); return
	var head:=sk.get_bone_global_rest(bones.Head).origin
	var hip:=sk.get_bone_global_rest(bones.pelvis).origin
	up=(head-hip).normalized()
	right=(sk.get_bone_global_rest(bones.upperarm_r).origin-sk.get_bone_global_rest(bones.upperarm_l).origin)
	right=(right-up*right.dot(up)).normalized()
	forward=up.cross(right).normalized()
	rng.randomize(); t=rng.randf()*20.0; rest_timer=rng.randf_range(2.0,4.0)

func _rot(sk: Skeleton3D,bone: int,axis: Vector3,deg: float) -> void:
	if absf(deg)<0.001: return
	var g:=sk.get_bone_global_pose(bone).basis.get_rotation_quaternion()
	var r:=Quaternion(axis.normalized(),deg_to_rad(deg))
	var l:=sk.get_bone_pose_rotation(bone)
	sk.set_bone_pose_rotation(bone,(l*(g.inverse()*r*g)).normalized())

## 0..1..0 over an action: eases in, holds, eases out.
func _env(x: float,length: float,ramp:=0.6) -> float:
	var a:=clampf(x/ramp,0.0,1.0); var b:=clampf((length-x)/ramp,0.0,1.0)
	var w:=minf(a,b)
	return w*w*(3.0-2.0*w)

func start_action(name: String,on_side:="") -> void:
	action=name; action_t=0.0; action_len=float(ACTIONS[name]); last_action=name
	side=on_side if on_side!="" else ("l" if rng.randf()<0.5 else "r")
	# arm actions use the left arm: the watch is worn on the left, and the inward roll that
	# brings the forearm across the body only looks right on that side for both meshes
	if name in ["watch","belt"]: side="l"

func _process_modification() -> void:
	var sk:=get_skeleton()
	if sk==null or bones.is_empty(): return
	var now:=Time.get_ticks_msec()
	var dt:=clampf((now-last_ms)/1000.0,0.0,0.1) if last_ms>0 else 0.016
	last_ms=now; t+=dt
	var s:=1.0 if side=="l" else -1.0 # mirror: +1 toward the character's left
	# --- pick the next action ---
	if action=="":
		rest_timer-=dt
		if rest_timer<=0.0:
			var names:=ACTIONS.keys().filter(func(n): return n!=last_action)
			start_action(names[rng.randi()%names.size()])
	else:
		action_t+=dt
		if action_t>=action_len: action=""; rest_timer=rng.randf_range(3.5,7.0)
	var w:=_env(action_t,action_len) if action!="" else 0.0
	# --- breathing (chest only) and a slow weight shift ---
	var breath:=sin(t*TAU/4.2)
	var sway:=sin(t*TAU/9.0)
	var lean:=sway*1.4
	var turn:=sway*0.8
	var arm_lift:={"l":0.0,"r":0.0}; var arm_bend:={"l":0.0,"r":0.0}; var arm_roll:={"l":0.0,"r":0.0}
	var head:=Vector3.ZERO
	match action:
		"watch":
			arm_lift[side]=0.22*w; arm_bend[side]=88.0*w; arm_roll[side]=-55.0*w
			head=Vector3(14.0*s,-16.0,0)*w
		"belt":
			arm_lift[side]=0.10*w; arm_bend[side]=62.0*w; arm_roll[side]=-45.0*w
			lean+=-2.2*s*w; head=Vector3(-6.0*s,-3.0,0)*w
		"shoulder":
			var ph:=clampf(action_t/action_len,0.0,1.0)*TAU
			_rot(sk,bones["clavicle_"+side],forward,6.0*sin(ph)*s*-1.0*w)
			_rot(sk,bones["clavicle_"+side],up,4.0*cos(ph)*s*w)
		"look_back":
			turn+=10.0*s*w; head=Vector3(26.0*s,-2.0,0)*w
		"neck":
			var ph2:=sin(clampf(action_t/action_len,0.0,1.0)*TAU)
			head=Vector3(0,-4.0,13.0*ph2)*w
	if arms:
		arms.lift=arm_lift; arms.bend=arm_bend; arms.roll=arm_roll
	_rot(sk,bones.spine_01,forward,lean)
	_rot(sk,bones.spine_01,up,turn)
	_rot(sk,bones.spine_02,right,-1.3*breath)
	_rot(sk,bones.spine_03,right,-1.0*breath)
	# --- head: idle glances when no action is steering it ---
	look_timer-=dt
	if look_timer<=0.0:
		var roll:=rng.randf()
		if roll<0.45: look_target=Vector3.ZERO
		elif roll<0.85: look_target=Vector3(rng.randf_range(10.0,20.0)*(1 if rng.randf()<0.5 else -1),rng.randf_range(-5.0,3.0),0)
		else: look_target=Vector3(rng.randf_range(-6.0,6.0),-8.0,0)
		look_timer=rng.randf_range(2.2,4.8)
	look=look.lerp(look_target*(1.0-w),1.0-exp(-dt*2.6))
	var h:=look+head
	var counter:=-turn # keep the head facing where it looks while the spine turns
	for pair in [[bones.neck_01,0.45],[bones.Head,0.55]]:
		_rot(sk,pair[0],up,(h.x+counter)*pair[1])
		_rot(sk,pair[0],right,(h.y+0.4*breath)*pair[1])
		_rot(sk,pair[0],forward,(h.z-lean)*pair[1])
