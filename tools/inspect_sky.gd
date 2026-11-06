extends SceneTree
func _initialize() -> void:
	for path in ["res://assets/sky/kloofendal_48d_partly_cloudy_2k.hdr","res://assets/sky/kloofendal_48d_partly_cloudy_puresky_2k.hdr","res://assets/sky/day_cloudy.hdr"]:
		var texture=load(path)
		print(path," exists=",ResourceLoader.exists(path)," texture=",texture," size=",texture.get_size() if texture else Vector2i.ZERO)
	quit()
