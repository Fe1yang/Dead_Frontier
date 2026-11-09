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
	await create_timer(0.6).timeout
	main.set("all_access", true)
	main.call("set_lobby_tab", 0)
	await create_timer(0.4).timeout
	print("owned(1)=", main.call("character_owned", 1), " choice=", main.get("character_choice"))
	var card: Rect2 = main.call("lobby_card_rect", 1)
	main.call("_lobby_tap", card.get_center())
	await create_timer(0.3).timeout
	print("after card tap: menu=", main.get("equip_menu_index"))
	var menu: Rect2 = main.call("equip_menu_rect")
	main.call("_lobby_tap", menu.get_center())
	await create_timer(0.3).timeout
	print("after menu tap: choice=", main.get("character_choice"), " menu=", main.get("equip_menu_index"))
	print("EQUIP_DONE")
	quit()
