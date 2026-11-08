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
	main.set("character_choice", 4)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -9.0, "walker")
	await create_timer(0.6).timeout
	var p = main.get("player")
	var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
	var hand: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("hand_r")).origin
	var wm = p.get("weapon_model")
	var gun: Vector3 = wm.global_position
	print("HAND=", Vector3(snappedf(hand.x,0.01), snappedf(hand.y,0.01), snappedf(hand.z,0.01)))
	print("GUN =", Vector3(snappedf(gun.x,0.01), snappedf(gun.y,0.01), snappedf(gun.z,0.01)))
	print("GAP =", Vector3(snappedf(gun.x-hand.x,0.01), snappedf(gun.y-hand.y,0.01), snappedf(gun.z-hand.z,0.01)), " dist=", snappedf((gun-hand).length(),0.01))
	print("GAP_DONE")
	quit()
