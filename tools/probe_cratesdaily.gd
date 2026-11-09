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
	main.set("airdrop_day", String(Time.get_date_string_from_system()))
	main.set("airdrop_count_today", 0)
	main.set("runs_total", 0)
	main.set("airdrop_at_run", -5)
	print("fresh: available=", main.call("airdrop_available"))
	main.call("_open_airdrop")
	print("after 1 open: count=", main.get("airdrop_count_today"), " available=", main.call("airdrop_available"))
	main.set("runs_total", main.get("runs_total") + 5)
	print("after 5 runs: available=", main.call("airdrop_available"))
	main.call("_open_airdrop")
	main.set("runs_total", main.get("runs_total") + 5)
	main.call("_open_airdrop")
	main.set("runs_total", main.get("runs_total") + 5)
	print("three opened: count=", main.get("airdrop_count_today"), " available=", main.call("airdrop_available"))
	print("CD_DONE")
	quit()
