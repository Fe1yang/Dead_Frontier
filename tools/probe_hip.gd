extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var lib = load("res://assets/animation-library/ual1/UAL1_Standard.glb").instantiate()
	var lp = lib.find_child("AnimationPlayer", true, false)
	for name in ["Walk", "Walk_Formal", "Push", "Crouch_Fwd", "Jog_Fwd", "Sprint"]:
		if not lp.has_animation(name): continue
		var a: Animation = lp.get_animation(name)
		var lo := 1.0e9
		var hi := -1.0e9
		for t in range(a.get_track_count()):
			if a.track_get_type(t) != Animation.TYPE_POSITION_3D: continue
			if not str(a.track_get_path(t)).ends_with(":pelvis"): continue
			for k in range(a.get_track_key_count(t)):
				var v: Vector3 = a.track_get_key_value(t, k)
				lo = minf(lo, v.y); hi = maxf(hi, v.y)
		print(name, " pelvis y=", snappedf(lo, 0.001), "..", snappedf(hi, 0.001))
	print("HIP_DONE")
	quit()
