extends SceneTree

## Diagnostic: for the meshes that appear in a hitching frame, print their parent chain so we
## can tell which system created them. Read-only.

var main: Node
var last_snapshot: Dictionary = {}
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
		d[mi.get_instance_id()] = mi
	return d

func _chain(n: Node) -> String:
	var parts: Array = []
	var cur := n
	var depth := 0
	while cur != null and depth < 4:
		parts.append(String(cur.name))
		cur = cur.get_parent()
		depth += 1
	return " < ".join(parts)

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
		if ms > 80.0 and spikes < 3:
			spikes += 1
			var current := _snapshot()
			print("SPIKE f=%d %.0fms new=%d" % [frame, ms, current.size() - last_snapshot.size()])
			var shown := 0
			for id in current.keys():
				if last_snapshot.has(id):
					continue
				if shown >= 10:
					break
				shown += 1
				var mi2: MeshInstance3D = current[id]
				var mat_names: Array = []
				if mi2.mesh != null:
					for s in range(mini(3, mi2.mesh.get_surface_count())):
						var m = mi2.get_active_material(s)
						if m != null:
							mat_names.append(String(m.resource_name) if m.resource_name != "" else "mat#%d" % m.get_instance_id())
				print("   ", _chain(mi2), "  mats=", mat_names)
			last_snapshot = current
			snapshot_age = 0
		elif snapshot_age >= 10:
			last_snapshot = _snapshot()
			snapshot_age = 0
	print("SPIKES=%d" % spikes)
	print("SP_DONE")
	quit()
