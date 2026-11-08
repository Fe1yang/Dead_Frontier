extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var z = load("res://assets/models/actors/zombie_walker_universal.glb").instantiate()
	var ap = z.find_child("AnimationPlayer", true, false)
	print("ZOMBIE_CLIPS ", ap.get_animation_list())
	var lib = load("res://assets/animation-library/ual1/UAL1_Standard.glb").instantiate()
	var lp = lib.find_child("AnimationPlayer", true, false)
	var names = lp.get_animation_list()
	print("UAL1 count=", names.size())
	print("UAL1_CLIPS ", names)
	z.free(); lib.free()
	quit()
