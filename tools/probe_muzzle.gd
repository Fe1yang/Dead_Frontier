extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(0.8).timeout
	var p = main.get("player")
	for wid in ["FLAME", "PISTOL"]:
		p.call("set_weapon", wid)
		await process_frame
		await process_frame
		var m: Vector3 = p.call("muzzle_position")
		var base: Vector3 = p.global_position
		var rel: Vector3 = m - base
		print(wid, " muzzle rel=", Vector3(snappedf(rel.x,0.01), snappedf(rel.y,0.01), snappedf(rel.z,0.01)))
	print("MZ_DONE")
	quit()
