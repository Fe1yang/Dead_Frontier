extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.8).timeout
	print("LOBBY video_mem=", Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)/1048576.0, " MB",
		" tex_mem=", Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)/1048576.0, " MB")
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
	await create_timer(1.0).timeout
	print("RUN video_mem=", Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)/1048576.0, " MB",
		" tex_mem=", Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)/1048576.0, " MB",
		" objects=", Performance.get_monitor(Performance.OBJECT_COUNT))
	print("VR_DONE")
	quit()
