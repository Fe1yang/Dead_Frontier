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
	await create_timer(0.4).timeout
	main.set("character_choice", 1)
	main.call("_lobby_tap", (main.call("lobby_card_rect", 1) as Rect2).get_center())
	await create_timer(0.8).timeout
	print("choice after tap=", main.get("character_choice"), " asset=", main.call("character_asset", 1))
	var lobby = main.get("lobby")
	print("lobby char node=", lobby.get("character") if lobby.get("character")!=null else "null")
	var c = lobby.get("character")
	if c != null and is_instance_valid(c):
		print("lobby char pos=", c.position, " scale=", c.scale)
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	print("choice in run=", main.get("character_choice"))
	var p = main.get("player")
	for ch in p.get_children():
		var nm := String(ch.name)
		if nm.contains("Rig") or nm.contains("survivor") or nm.contains("Armature"):
			print("player child=", nm, " children=", ch.get_child_count())
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/riley_run2.png")
	print("RILEY2_DONE")
	quit()
