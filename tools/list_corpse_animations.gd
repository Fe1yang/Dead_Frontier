extends SceneTree
func _initialize() -> void:
	for path in ["res://assets/animation-library/ual1/UAL1_Standard.glb","res://assets/animation-library/ual2/UAL2_Standard.glb","res://assets/models/actors/zombie_walker_universal.glb","res://assets/models/actors/zombie_female_universal.glb"]:
		var scene: Node=load(path).instantiate()
		var player:=scene.find_child("AnimationPlayer",true,false) as AnimationPlayer
		print("ANIMATION_SOURCE ",path)
		if player:
			for clip in player.get_animation_list():
				if "death" in clip.to_lower() or "dead" in clip.to_lower() or "lying" in clip.to_lower() or "crawl" in clip.to_lower(): print("CORPSE_CLIP ",clip)
		scene.free()
	quit()
