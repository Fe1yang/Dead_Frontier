extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.2).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	await create_timer(0.4).timeout
	var p = main.get("player")
	var mz: Vector3 = p.call("muzzle_position")
	print("PLAYER pos=", p.position, " muzzle=", mz, " dz=", snappedf(mz.z - p.position.z, 0.01), " dx=", snappedf(mz.x - p.position.x, 0.01))
	main.call("_spawn_zombie", -10.0, "bomber")
	await create_timer(0.6).timeout
	for z in (main.get("zombies") as Array):
		if is_instance_valid(z) and String(z.get("kind")) == "bomber":
			var ap: AnimationPlayer = z.get("animation_player")
			print("BOMBER clip=", ap.current_animation if ap else "none", " playing=", ap.is_playing() if ap else false, " waddle=", z.get("needs_waddle"))
	print("FIX2_DONE")
	quit()
