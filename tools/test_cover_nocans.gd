extends SceneTree
## Regression: no-cans must never force the purchase popup. The cover tap walks into the
## lobby with just a toast; the lobby START button also only toasts; the wallet's little
## "+" icon stays as the voluntary way into the store.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.4).timeout
	assert(game.state=="cover")
	game.stamina.value=0; game.stamina.updated_at=game.stamina.now()
	# cover tap: straight to the lobby, toast only, no popup
	game._pointer_down(Vector2(270,480))
	await create_timer(0.6).timeout
	print("STATE_AFTER_TAP ",game.state)
	assert(game.state!="resource_pack")
	assert(game.state in ["character_select","signin","offer"])
	assert(game.store_toast>0.0)
	# settle any sign-in/offer overlay back to the plain lobby
	while game.state in ["signin","offer"]:
		game._pointer_down(game.OFFER_CLOSE.get_center()); await create_timer(0.2).timeout
	assert(game.state=="character_select")
	# lobby START with 0 cans: toast again, still no popup, still in the lobby
	game.store_toast=0.0
	game._pointer_down(game.LOBBY_START.get_center())
	await create_timer(0.2).timeout
	print("STATE_AFTER_START ",game.state)
	assert(game.state=="character_select" and game.store_toast>0.0)
	# the voluntary path: the wallet "+" opens the store only when the player asks
	game._pointer_down(game.wallet_layout(game.WALLET_LOBBY,game.LOBBY_WALLET_SCALE).can_plus.get_center())
	await create_timer(0.2).timeout
	print("STATE_AFTER_PLUS ",game.state)
	assert(game.state=="store")
	print("COVER_NOCANS_PASS")
	game.queue_free(); await process_frame; quit()
