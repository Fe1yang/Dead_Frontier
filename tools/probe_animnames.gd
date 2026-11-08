extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var AL = load("res://scripts/anim_library.gd")
	for s in ["ual1","ual2"]:
		var p = AL._source_player(s)
		print("==", s, "==")
		print(", ".join(p.get_animation_list()))
	print("NAMES_DONE")
	quit()
