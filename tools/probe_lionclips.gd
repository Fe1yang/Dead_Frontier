extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	for path in ["res://assets/models/pets/lion.glb", "res://assets/models/pets/white_tiger.glb", "res://assets/models/pets/czech_wolfdog.glb"]:
		var packed = load(path)
		if packed == null:
			print("MISS ", path); continue
		var n = packed.instantiate()
		root.add_child(n)
		var ap = n.find_child("AnimationPlayer", true, false)
		if ap:
			print(path.get_file(), " -> ", ap.get_animation_list())
		else:
			print(path.get_file(), " -> no AnimationPlayer")
		n.queue_free()
	print("LC_DONE")
	quit()
