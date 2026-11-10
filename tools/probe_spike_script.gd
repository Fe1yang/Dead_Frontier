extends SceneTree
var main: Node
var last: Dictionary = {}
var age := 0
var spikes := 0
func _initialize() -> void:
	call_deferred("_run")
func _snap() -> Dictionary:
	var d := {}
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi and mi.is_visible_in_tree() and mi.mesh != null:
			d[mi.get_instance_id()] = mi
	return d
func _script_of(n: Node) -> String:
	var cur := n
	for i in range(5):
		if cur == null: break
		if cur.get_script() != null:
			return String((cur.get_script() as Script).resource_path).get_file()
		cur = cur.get_parent()
	return "?"
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
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	last = _snap()
	var t0 := Time.get_ticks_usec()
	var prev := t0
	var frame := 0
	while Time.get_ticks_usec() - t0 < 22000000:
		await process_frame
		frame += 1
		var now := Time.get_ticks_usec()
		var ms := (now - prev) / 1000.0
		prev = now
		age += 1
		if ms > 90.0 and spikes < 2:
			spikes += 1
			var cur := _snap()
			var owners := {}
			for id in cur.keys():
				if last.has(id): continue
				var mi2: MeshInstance3D = cur[id]
				var s := _script_of(mi2)
				owners[s] = int(owners.get(s, 0)) + 1
			print("SPIKE f=%d %.0fms new=%d owners=%s" % [frame, ms, cur.size() - last.size(), str(owners)])
			last = cur
			age = 0
		elif age >= 10:
			last = _snap()
			age = 0
	print("SP_DONE")
	quit()
