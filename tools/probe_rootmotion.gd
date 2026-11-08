extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.8).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.3).timeout
	main.call("start_run", true, true)
	await create_timer(0.3).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -7.0, "walker")
	await create_timer(0.3).timeout
	var z = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q): z = q
	var ap = z.get("animation_player")
	for name in ["Zombie_Walk_Fwd", "Death01"]:
		var a: Animation = ap.get_animation(name)
		for t in range(a.get_track_count()):
			if a.track_get_type(t) != Animation.TYPE_POSITION_3D: continue
			var lo := Vector3.INF
			var hi := -Vector3.INF
			for k in range(a.track_get_key_count(t)):
				var v: Vector3 = a.track_get_key_value(t, k)
				lo = lo.min(v); hi = hi.max(v)
			print("TRACK ", name, " ", a.track_get_path(t), " x=", snappedf(lo.x,0.001), "..", snappedf(hi.x,0.001), " z=", snappedf(lo.z,0.001), "..", snappedf(hi.z,0.001))
	var z0: float = z.position.z
	main.call("_hit_zombie", z, 1000000.0, "torso", z.global_position + Vector3(0,1.2,0))
	await create_timer(0.5).timeout
	var z1: float = z.position.z if is_instance_valid(z) else 0.0
	await create_timer(0.7).timeout
	print("SLIDE dz=", snappedf(z1 - z0, 0.001), " freed=", not is_instance_valid(z))
	print("ROOTMOTION_DONE")
	quit()
