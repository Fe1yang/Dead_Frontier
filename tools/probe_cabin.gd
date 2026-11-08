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
	var room = lobby.find_child("SurvivalCabin", true, false)
	print("cabin node=", room != null, " cabin_lobby=", lobby.get("cabin_lobby"))
	if room != null:
		var box := AABB(); var first := true
		for mi in room.find_children("*","MeshInstance3D",true,false):
			var m: MeshInstance3D = mi
			if m.mesh == null: continue
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("cabin world aabb=", box)
	var cam: Camera3D = main.get("camera")
	print("cam pos=", cam.global_position, " look target=", lobby.call("camera_target"))
	print("CABIN_PROBE_DONE")
	quit()
