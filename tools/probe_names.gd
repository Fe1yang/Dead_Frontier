extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var S = load("res://scripts/shop_text.gd")
	for code in ["en","zh_CN","ja","ar","th"]:
		print(code, " suomi=", S.text(code,"n_suomi"), " makarov=", S.text(code,"n_makarov"), " flame=", S.text(code,"n_flame"))
	print("NAMES_DONE")
	quit()
