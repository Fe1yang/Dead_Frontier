extends SceneTree
func _initialize() -> void:
	for tag in ["survivor_riley_universal", "survivor_maya_universal", "survivor_male_universal"]:
		var scene: PackedScene = load("res://assets/models/actors/" + tag + ".glb")
		var inst := scene.instantiate()
		var ap := inst.find_child("AnimationPlayer", true, false) as AnimationPlayer
		print("ANIMS ", tag, " ", ap.get_animation_list() if ap else "NO_PLAYER")
	quit()
