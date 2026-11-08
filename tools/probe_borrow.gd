extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var AL = load("res://scripts/anim_library.gd")
	var src = AL._source_player("ual1")
	print("SRC=", src)
	if src:
		var names = src.get_animation_list()
		print("SRC_ANIMS=", names.size(), " has Idle_Loop=", src.has_animation("Idle_Loop"))
		print("first: ", names.slice(0, 6))
	var scene = load("res://assets/models/actors/survivor_riley_universal.glb").instantiate()
	root.add_child(scene)
	await process_frame
	var ap = scene.find_child("AnimationPlayer", true, false)
	print("ACTOR_AP=", ap, " anims=", ap.get_animation_list() if ap else [])
	var got = AL.borrow(ap, "Idle_Loop", "ual1")
	print("BORROW_RESULT='", got, "'")
	print("BORROW_DONE")
	quit()
