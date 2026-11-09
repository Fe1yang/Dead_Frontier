extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var paths := [
		"res://assets/models/weapons/shotgun.glb","res://assets/models/weapons/sniper.glb",
		"res://assets/models/rifle.glb","res://assets/models/weapons/smg.glb",
		"res://assets/models/weapons/launcher.glb","res://assets/models/weapons/pistol.glb",
		"res://assets/models/medkit.glb","res://assets/models/armor.glb","res://assets/models/helmet.glb",
		"res://assets/models/frag_grenade.glb","res://assets/models/flashbang.glb",
		"res://assets/models/ammo_pickup.glb","res://assets/models/barrel.glb",
		"res://assets/models/supply_truck.glb","res://assets/models/fire_round.glb"]
	for p in paths:
		var ex := ResourceLoader.exists(p)
		var res = load(p)
		print(("OK  " if res != null else "NULL"), " exists=", ex, "  ", p)
	print("SL_DONE")
	quit()
