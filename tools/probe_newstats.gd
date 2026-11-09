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
	await create_timer(0.5).timeout
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(0.8).timeout
	var p = main.get("player")
	for wid in ["PISTOL", "MAKAROV", "SNIPER", "SUOMI", "SMG"]:
		p.call("set_weapon", wid)
		await process_frame
		var wm = p.get("weapon_model")
		var box := AABB(); var first := true
		for m in wm.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		print(wid, " dmg=", snappedf(p.get("damage"), 1.0), " mag=", p.get("magazine_size"), " interval=", snappedf(p.get("fire_interval"), 0.01), " len=", snappedf(box.size.z, 0.01))
	print("NS_DONE")
	quit()
