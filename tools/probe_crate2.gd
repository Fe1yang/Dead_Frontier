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
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_spawn_crates")
	await create_timer(0.8).timeout
	var crates = main.get("crates")
	var c = crates[0]
	var names := []
	for ch in c.get("body").get_children():
		names.append(ch.name)
	print("BODY_CHILDREN ", names)
	var box := AABB(); var first := true
	for mi in c.find_children("*","MeshInstance3D",true,false):
		var m: MeshInstance3D = mi
		if m.mesh == null: continue
		var b: AABB = m.global_transform * m.get_aabb()
		box = b if first else box.merge(b)
		first = false
	print("CRATE_AABB ", box)
	print("CRATE2_DONE")
	quit()
