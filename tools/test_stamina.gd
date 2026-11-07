extends SceneTree

const OUT:="C:/Users/user/Documents/kimi/tasks/2026-11-04/00-09-49-288c0219/diagnostics"

func _initialize() -> void:
	call_deferred("_run")

func _capture(path: String) -> void:
	await create_timer(0.22).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(path)==OK)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game.stamina.set_process(false)
	var s: Node=game.stamina
	assert(s.CAP==50 and s.RUN_COST==10 and s.REGEN_SECONDS==216)

	s.value=50; s.updated_at=s.now(); game.enter_lobby(); game.start_run()
	assert(s.value==40 and game.state in ["intro","playing"])
	print("STAMINA_CONSUME_PASS 50 -> 40")

	s.value=20; s.updated_at=s.now()-7*s.REGEN_SECONDS; s.refresh(false)
	assert(s.value==27)
	print("STAMINA_REGEN_PASS 20 + 7 steps -> 27")

	s.value=48; s.updated_at=s.now()-10*s.REGEN_SECONDS; s.refresh(false)
	assert(s.value==50)
	print("STAMINA_CAP_PASS 48 + overtime -> 50")

	s.value=50; s.updated_at=s.now()
	assert(game._iap_grant("cans_6","stamina-test-pack"))
	assert(s.value==650)
	print("STAMINA_PURCHASE_PASS 50 + 600 -> 650")

	s.value=5; s.updated_at=s.now(); game.enter_lobby(); game.start_run()
	assert(s.value==5 and game.state=="resource_pack" and game.resource_pack_id=="cans_1")
	assert(game.resource_pack_return_state=="character_select")
	assert(game.store_toast_text==game.StoreCatalog.text(game.language_code,"no_cans"))
	print("RESOURCE_CAN_SHORTAGE_PASS balance=5 pack=cans_1")
	await _capture(OUT+"/resource-cans-popup.png")
	game._pointer_down(game.OFFER_BUY.get_center())
	assert(s.value==15 and game.state=="character_select")
	print("RESOURCE_CAN_PURCHASE_PASS 5 + 10 -> 15")

	s.value=5; s.updated_at=s.now(); game.enter_lobby(); game.ad_run_used=false; game.store_toast=0.0
	game._pointer_down(game.LOBBY_START.get_center())
	assert(s.value==5 and game.state=="character_select")
	print("STAMINA_DISABLED_START_PASS balance=5 state=character_select")
	await _capture(OUT+"/stamina-low-lobby.png")

	game._pointer_down(game.LOBBY_AD_RUN.get_center())
	assert(game.ad_pending=="free_run")
	await create_timer(0.55).timeout
	assert(s.value==5 and game.state in ["intro","playing"] and game.ad_run_used)
	print("STAMINA_AD_RUN_PASS balance=5 used=true")
	game.enter_lobby()
	assert(not game.request_reward_ad("free_run"))
	print("STAMINA_AD_ONCE_PASS second_request=refused")

	game.offer_id="offer_supply"; game.offer_expires=game.now_unix()+3600; game.open_offer()
	await _capture(OUT+"/offer-popup.png")
	game.close_offer(); game.store_toast=0.0
	await _capture(OUT+"/offer-badge.png")

	s.value=20; s.updated_at=s.now(); game.offer_id="offer_cans"; game.offer_expires=game.now_unix()+3600
	assert(game._iap_grant("offer_cans","stamina-test-can-offer"))
	assert(s.value==170 and not game.offer_active())
	print("STAMINA_CAN_OFFER_PASS 20 + 150 -> 170")
	game.offer_id="offer_cans"; game.offer_expires=game.now_unix()+3600; game.open_offer()
	await _capture(OUT+"/offer-cans-popup.png")
	game.close_offer()

	s.value=50; s.updated_at=s.now(); game.store_toast=0.0; game.enter_lobby()
	await _capture(OUT+"/stamina-lobby.png")
	game.open_store(); game.can_ad_day=""; game.can_ad_count=0
	var ad_item: Dictionary={}
	for item in game.store_layout():
		if item.get("can_ad",false): ad_item=item
		if item.get("header","")=="cans":
			game.store_scroll=clampf((item.rect as Rect2).position.y-8.0,0.0,game.store_max_scroll())
	assert(not ad_item.is_empty() and game.can_ads_left()==10)
	await _capture(OUT+"/stamina-store-cans.png")
	var ad_pos: Vector2=game.store_screen_rect(ad_item).get_center()
	game._pointer_down(ad_pos); game._store_release(ad_pos)
	assert(game.ad_pending=="can_refill")
	await create_timer(0.55).timeout
	assert(s.value==55 and game.can_ad_count==1 and game.can_ads_left()==9)
	print("STAMINA_STORE_AD_PASS 50 + 5 -> 55 remaining=9")
	game.can_ad_day=game.today(); game.can_ad_count=10
	assert(game.can_ads_left()==0 and not game.request_reward_ad("can_refill"))
	game.can_ad_day="2000-01-01"
	assert(game.can_ads_left()==10)
	print("STAMINA_STORE_AD_LIMIT_PASS cap=10 daily_reset=yes")

	game.close_store(); game.open_shop()
	var gear: Dictionary=game.shop_items[0]
	game.meta_upgrades[gear.id]=0; game.bank_coins=0
	assert(not game.buy_item(String(gear.id)))
	assert(game.state=="resource_pack" and game.resource_pack_id=="coins_1" and game.resource_pack_return_state=="shop")
	await _capture(OUT+"/resource-coins-popup.png")
	game._pointer_down(game.OFFER_BUY.get_center())
	assert(game.bank_coins==300 and game.state=="shop")
	print("RESOURCE_COIN_SHORTAGE_PASS upgrade_failed=true pack=coins_1 purchase=300")
	game.bank_coins=game.item_cost(gear)
	assert(game.buy_item(String(gear.id)) and game.bank_coins==0 and game.state=="shop")
	print("RESOURCE_EXACT_SPEND_PASS coins=0 popup=closed")

	game.close_shop(); game.bank_vouchers=0
	assert(not game.spend_vouchers(1))
	assert(game.state=="resource_pack" and game.resource_pack_id=="vouchers_1" and game.resource_pack_return_state=="character_select")
	await _capture(OUT+"/resource-vouchers-popup.png")
	game._pointer_down(game.OFFER_BUY.get_center())
	assert(game.bank_vouchers==1 and game.state=="character_select")
	assert(game.spend_vouchers(1) and game.bank_vouchers==0 and game.state=="character_select")
	print("RESOURCE_VOUCHER_SHORTAGE_PASS pack=vouchers_1 purchase=1 exact_spend=no_popup")

	print("STAMINA_TEST_PASS consume=10 regen=216s cap=50 overfill=yes disabled_start=yes one_ad_run=yes store_ads=yes can_offer=yes resource_packs=yes")
	quit()
