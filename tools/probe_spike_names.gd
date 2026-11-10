extends SceneTree

## Diagnostic only: records what becomes visible in the frames that hitch.
## Nothing here changes the game; it just names the meshes and materials that appear.

var main: Node
var last_snapshot: Dictionary = {}   # mesh name -> instance id
var snapshot_age := 0
var spikes := 0

func _initialize() -> void:
	call_deferred("_run")

func _snapshot() -> Dictionary:
	var d := {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or not mi.is_visible_in_tree() or mi.mesh == null:
			continue
		d[String(mi.name) + "@" + str(mi.get_instance_id())] = true
	return d

func _material_count(mesh_names: Array) -> int:
	var mats := {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or not mi.is_visible_in_tree() or mi.mesh == null:
			continue
		for s in range(mi.mesh.get_surface_count()):
			var m = mi.get_active_material(s)
			if m != null:
				mats[m.get_instance_id()] = true
	return mats.size()

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

	last_snapshot = _snapshot()
	var t0 := Time.get_ticks_usec()
	var last := t0
	var frame := 0
	while Time.get_ticks_usec() - t0 < 22000000:
		await process_frame
		frame += 1
		var now := Time.get_ticks_usec()
		var ms := (now - last) / 1000.0
		last = now
		snapshot_age += 1
		if ms > 50.0 and spikes < 8:
			spikes += 1
			var current := _snapshot()
			var fresh: Array = []
			for k in current.keys():
				if not last_snapshot.has(k):
					fresh.append(String(k).split("@")[0])
			var proc_ms := Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
			var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
			print("SPIKE f=%d %.0fms proc=%.1f draws=%.0f new_meshes=%d mats=%d  NEW=%s" % [
				frame, ms, proc_ms, draws, fresh.size(), _material_count(fresh),
				", ".join(fresh.slice(0, 12))])
			last_snapshot = current
			snapshot_age = 0
		elif snapshot_age >= 12:
			last_snapshot = _snapshot()
			snapshot_age = 0
	print("SPIKES total=%d" % spikes)
	print("SP_DONE")
	quit()
