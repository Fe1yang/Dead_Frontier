import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pet_companion_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "func _strip_root_motion" not in t:
    helper = '''## Some pet clips carry the walk cycle as root translation. Played in place that reads as the
## animal sliding forward while its skin stretches, so the horizontal part of every root track is
## flattened and only the vertical bob is kept.
func _strip_root_motion(player: AnimationPlayer) -> void:
	for name in player.get_animation_list():
		var clip := player.get_animation(String(name))
		if clip == null:
			continue
		for track in range(clip.get_track_count()):
			if clip.track_get_type(track) != Animation.TYPE_POSITION_3D:
				continue
			var path := String(clip.track_get_path(track))
			var lower := path.to_lower()
			if lower.find("root") < 0 and lower.find("hips") < 0 and lower.find("pelvis") < 0:
				continue
			var keys := clip.track_get_key_count(track)
			var base_y := 0.0
			if keys > 0:
				base_y = (clip.track_get_key_value(track, 0) as Vector3).y
			for k in range(keys):
				var v: Vector3 = clip.track_get_key_value(track, k)
				clip.track_set_key_value(track, k, Vector3(0.0, v.y - base_y, 0.0))


'''
    anchor = "func _animate(delta: float) -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

# apply it once the animations are found
old = "\tanim=model.find_child(\"AnimationPlayer\",true,false) as AnimationPlayer"
new = "\tanim=model.find_child(\"AnimationPlayer\",true,false) as AnimationPlayer\n\tif anim != null:\n\t\t_strip_root_motion(anim)"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("pet clips are played in place (no root translation)")
