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
	await create_timer(0.8).timeout
	var lobby = main.get("lobby")
	print("wooden_lobby=", lobby.get("wooden_lobby"), " size=", lobby.get("wooden_size"), " center=", lobby.get("wooden_center"))
	var room = lobby.find_child("WoodenLobby", true, false)
	print("room node=", room != null)
	if room != null:
		var box := AABB(); var first := true
		for mi in room.find_children("*","MeshInstance3D",true,false):
			var m: MeshInstance3D = mi
			if m.mesh == null: continue
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("room world aabb=", box, " visible=", room.visible)
	var cam: Camera3D = main.get("camera")
	print("camera pos=", cam.global_position, " target_lobby=", lobby.call("camera_target"))
	print("WOOD_DONE")
	quit()
