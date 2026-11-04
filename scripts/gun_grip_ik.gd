extends SkeletonModifier3D
## Holds the survivors' arms in a straight-armed two-hand gun stance on top of the run clip.
## Their meshes have almost no forearm skin weights, so any strong elbow bend collapses the
## forearm ("short arm") and the bent clip pressed flat palms together ("seal hands").
## This modifier places both hands on the weapon with near-straight elbows and straight wrists.

## Where the support (left) hand sits relative to the firing hand, along the barrel (metres).
@export var support_forward:=0.03
@export var support_side:=0.11     # gap between the two hands so they don't overlap/cross
@export var support_drop:=0.03
@export var grip_drop:=0.10       # how far below shoulder height the gun is held
@export var straightness:=0.965   # fraction of full arm length used to reach the grip
@export var palm_roll_r:=0.0     # wrist roll around the forearm (0 = palm down under the gun)
@export var palm_roll_l:=0.0
@export var weight:=1.0

var b:={}
var lengths:={}
var forward:=Vector3(0,0,1)
var grip_point:=Vector3.ZERO      # skeleton space, last computed visible firing-hand position
## Offset from each hand bone to where that hand's mesh actually is (bone space). The female
## survivor shares the male skeleton but has shorter arms, so her visible hands sit short of
## the hand bones; IK aims the *visible* hands at the grip and the gun mounts there.
var hand_offset:={"r":Vector3.ZERO,"l":Vector3.ZERO}
var _ready_bones:=false

func _setup(sk: Skeleton3D) -> void:
	for n in ["upperarm_r","lowerarm_r","hand_r","upperarm_l","lowerarm_l","hand_l","spine_03","foot_l","ball_l"]:
		b[n]=sk.find_bone(n)
	for side in ["r","l"]:
		var u:=sk.get_bone_global_rest(b["upperarm_"+side]).origin
		var lo:=sk.get_bone_global_rest(b["lowerarm_"+side]).origin
		var h:=sk.get_bone_global_rest(b["hand_"+side]).origin
		lengths[side]=[u.distance_to(lo),lo.distance_to(h)]
	if b.foot_l>=0 and b.ball_l>=0:
		var toe:=sk.get_bone_global_rest(b.ball_l).origin-sk.get_bone_global_rest(b.foot_l).origin
		forward=Vector3(0,0,signf(toe.z) if absf(toe.z)>0.001 else 1.0)
	_ready_bones=true

func _process_modification() -> void:
	var sk:=get_skeleton()
	if sk==null or weight<=0.0: return
	if not _ready_bones: _setup(sk)
	var sr:=_g(sk,b.upperarm_r).origin
	var sl:=_g(sk,b.upperarm_l).origin
	var chest:=(sr+sl)*0.5
	var side_axis:=(sl-sr).normalized() # points from right shoulder to left shoulder
	var fwd:=(forward-side_axis*forward.dot(side_axis)).normalized()
	var down:=(Vector3.DOWN-fwd*Vector3.DOWN.dot(fwd)).normalized()
	var reach_r:=(float(lengths.r[0])+float(lengths.r[1]))*straightness
	var lateral:=sr.distance_to(chest)-0.02
	var depth:=sqrt(maxf(0.01,reach_r*reach_r-lateral*lateral-grip_drop*grip_drop))
	var want_r:=chest+fwd*depth+down*grip_drop-side_axis*0.02
	var want_l:=want_r+fwd*support_forward+down*support_drop+side_axis*support_side
	grip_point=_reach(sk,"r",want_r,-side_axis*0.8+down*0.6,palm_roll_r,fwd)
	_reach(sk,"l",want_l,side_axis*0.8+down*0.6,palm_roll_l,fwd)

## Solves so the visible hand (bone + mesh offset) lands on `want`; returns where it landed.
func _reach(sk: Skeleton3D,side: String,want: Vector3,pole: Vector3,roll: float,fwd: Vector3) -> Vector3:
	var target:=want
	var ih:int=b["hand_"+side]
	var off: Vector3=hand_offset[side]
	for i in range(3):
		_solve(sk,side,target,pole,roll,fwd)
		var visible:=_g(sk,ih)*off
		target+=want-visible
	return _g(sk,ih)*off

## Bone-space centre of the vertices skinned mostly to the hand (palm + fingers + thumb),
## i.e. where the hand mesh really is relative to the hand bone.
static func mesh_offset(model: Node,bone: String) -> Vector3:
	var suffix:=bone.substr(bone.length()-2) # "_r" / "_l"
	for m in model.find_children("*","MeshInstance3D",true,false):
		var mi:=m as MeshInstance3D
		if mi.skin==null: continue
		var hand_index:=-1; var group:={}
		for i in range(mi.skin.get_bind_count()):
			var name:=str(mi.skin.get_bind_name(i))
			if name==bone: hand_index=i
			if name==bone or (name.ends_with(suffix) and (name.begins_with("thumb") or name.begins_with("index") or name.begins_with("middle") or name.begins_with("ring") or name.begins_with("pinky"))): group[i]=true
		if hand_index<0: continue
		var arrays:=mi.mesh.surface_get_arrays(0)
		var verts: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var bones: PackedInt32Array=arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array=arrays[Mesh.ARRAY_WEIGHTS]
		var per:=bones.size()/maxi(1,verts.size())
		var sum:=Vector3.ZERO; var count:=0
		for v in range(verts.size()):
			var w:=0.0
			for k in range(per):
				if group.has(bones[v*per+k]): w+=weights[v*per+k]
			if w>0.6: sum+=verts[v]; count+=1
		if count==0: continue
		return mi.skin.get_bind_pose(hand_index)*(sum/count)
	return Vector3.ZERO

func _solve(sk: Skeleton3D,side: String,target: Vector3,pole: Vector3,roll: float,fwd: Vector3) -> void:
	var iu:int=b["upperarm_"+side]; var il:int=b["lowerarm_"+side]; var ih:int=b["hand_"+side]
	var root:=_g(sk,iu).origin
	var l1: float=lengths[side][0]; var l2: float=lengths[side][1]
	var to_t:=target-root
	var d:=clampf(to_t.length(),0.05,(l1+l2)*0.999)
	var n:=to_t.normalized()
	var along:=(l1*l1-l2*l2+d*d)/(2.0*d)
	var h:=sqrt(maxf(0.0,l1*l1-along*along))
	var p:=pole-n*pole.dot(n)
	if p.length()<0.001: p=Vector3.DOWN
	var elbow:=root+n*along+p.normalized()*h
	_aim(sk,iu,il,elbow)
	_aim(sk,il,ih,root+n*d)
	# Straight wrist: hand continues the forearm, then roll so the palm wraps the grip.
	var lg:=_g(sk,il)
	var hg:=_g(sk,ih)
	var forearm_axis:=(hg.origin-lg.origin).normalized()
	var hand_basis:=Basis(forearm_axis,roll)*lg.basis
	_set_g(sk,ih,Transform3D(hand_basis,hg.origin))

func _aim(sk: Skeleton3D,bone: int,child: int,point: Vector3) -> void:
	var g:=_g(sk,bone)
	var cur:=_g(sk,child).origin-g.origin
	var want:=point-g.origin
	if cur.length()<0.0001 or want.length()<0.0001: return
	var q:=Quaternion(cur.normalized(),want.normalized())
	_set_g(sk,bone,Transform3D(Basis(q)*g.basis,g.origin))

# Global poses from current local poses (the skeleton's global cache is stale mid-modifier).
func _g(sk: Skeleton3D,bone: int) -> Transform3D:
	var parent:=sk.get_bone_parent(bone)
	var local:=sk.get_bone_pose(bone)
	return local if parent<0 else _g(sk,parent)*local

func _set_g(sk: Skeleton3D,bone: int,global: Transform3D) -> void:
	var parent:=sk.get_bone_parent(bone)
	var local:=global if parent<0 else _g(sk,parent).affine_inverse()*global
	sk.set_bone_pose_position(bone,local.origin)
	sk.set_bone_pose_rotation(bone,local.basis.get_rotation_quaternion())
