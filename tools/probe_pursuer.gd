extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.3).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(2.2).timeout
	var boss = main.get("chaser")
	print("chaser=", boss != null)
	if boss != null:
		print("boss pos=", boss.position, " visible=", boss.visible)
		var ap: AnimationPlayer = boss.find_child("AnimationPlayer", true, false)
		print("boss clip=", ap.current_animation if ap else "none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pursuer_check.png")
	print("PURSUER_DONE")
	quit()
