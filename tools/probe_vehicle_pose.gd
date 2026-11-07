extends SceneTree
## One-off probe: how do the three paid bikes actually import in Godot, and what does
## the lobby's "standing on its nose" heuristic decide for each of them?

const PATHS := [
	"res://assets/models/vehicles/bike_paid.glb",
	"res://assets/models/vehicles/bike_paid2.glb",
	"res://assets/models/vehicles/bike_paid3.glb",
]

func _aabb(node: Node3D) -> AABB:
	var out := AABB()
	var first := true
	for mi in node.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m == null or m.mesh == null: continue
		var b: AABB = m.global_transform * m.get_aabb()
		if first: out = b; first = false
		else: out = out.merge(b)
	return out

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	for p in PATHS:
		var packed := load(p) as PackedScene
		if packed == null:
			print("LOAD_FAIL ", p); continue
		var n := packed.instantiate() as Node3D
		root.add_child(n)
		await process_frame
		var b := _aabb(n)
		var tallest := b.size.y > 1.5 * maxf(b.size.x, b.size.z)
		var tris := 0
		for mi in n.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			if m.mesh != null:
				for s in range(m.mesh.get_surface_count()):
					tris += (m.mesh.surface_get_array_len(s) / 3)
		# does the material carry an albedo texture?
		var has_tex := false
		for mi in n.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			for s in range(m.mesh.get_surface_count()):
				var mat := m.mesh.surface_get_material(s) as BaseMaterial3D
				if mat != null and mat.albedo_texture != null: has_tex = true
		print("BIKE %s min=%s max=%s size=%s tris=%d albedo_tex=%s tip_would_fire=%s" % [
			p.get_file(), str(b.position.snapped(Vector3(0.001,0.001,0.001))),
			str((b.position + b.size).snapped(Vector3(0.001,0.001,0.001))),
			str(b.size.snapped(Vector3(0.001,0.001,0.001))), tris, str(has_tex), str(tallest)])
		n.queue_free()
		await process_frame
	print("POSE_PROBE_DONE")
	quit()
