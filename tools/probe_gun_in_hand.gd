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
	await create_timer(0.4).timeout
	main.set("character_choice", 1); main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.6).timeout
	var p = main.get("player")
	var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
	for w in ["PISTOL","SMG","SHOTGUN","SNIPER","RIFLE","LAUNCHER"]:
		p.call("take_weapon", w)
		await create_timer(0.25).timeout
		var wm: Node3D = p.get("weapon_model")
		var hr: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("hand_r")).origin
		var hl: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("hand_l")).origin
		if wm == null:
			print(w, " no model"); continue
		var wp: Vector3 = wm.global_position
		print("%-9s gun->handR %.2f m  gun->handL %.2f m  muzzle->handR %.2f m" % [
			w, wp.distance_to(hr), wp.distance_to(hl), p.call("muzzle_position").distance_to(hr)])
	print("GUNHAND_DONE")
	quit()
