import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# keep one chaser alive from loading time: building it at the intro cost a visible hitch
if "var chaser_pooled" not in t:
    anchor = "var chaser: Node3D"
    if t.count(anchor) != 1:
        anchor = "var chaser:Node3D"
    assert t.count(anchor) >= 1, "chaser declaration not found"
    t = t.replace(anchor, anchor.replace("var chaser", "var chaser_pooled: Node3D\nvar chaser"), 1)

# build it once the loading screen ends
if "_warm_chaser()" not in t:
    helper = '''## The intro chaser is a 13 MB skinned model; building it on the intro frame was a visible
## stall. Make one during loading and just move it into shot when the intro starts.
func _warm_chaser() -> void:
	if chaser_pooled != null or not ResourceLoader.exists(BossChaserScript.MODEL_PATH):
		return
	chaser_pooled = BossChaserScript.new()
	add_child(chaser_pooled)
	chaser_pooled.visible = false
	chaser_pooled.position = Vector3(0, -80, 0)


'''
    anchor2 = "func _finish_loading() -> void:"
    assert t.count(anchor2) == 1
    t = t.replace(anchor2, helper + anchor2, 1)

# call it with the other warm-up work
old_warm = "\t_warm_drop_pool()"
new_warm = "\t_warm_drop_pool()\n\t_warm_chaser()"
if t.count(old_warm) == 1:
    t = t.replace(old_warm, new_warm, 1)

# the intro reuses it instead of constructing a new one
old_intro = '''	if ResourceLoader.exists(BossChaserScript.MODEL_PATH):
		chaser=BossChaserScript.new(); add_child(chaser); chaser.position=player.position+CHASER_OFFSET'''
new_intro = '''	if chaser_pooled != null:
		chaser = chaser_pooled
		chaser_pooled = null
		chaser.visible = true
		chaser.position = player.position + CHASER_OFFSET
	elif ResourceLoader.exists(BossChaserScript.MODEL_PATH):
		chaser=BossChaserScript.new(); add_child(chaser); chaser.position=player.position+CHASER_OFFSET'''
assert t.count(old_intro) == 1, t.count(old_intro)
t = t.replace(old_intro, new_intro, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("chaser is built during loading and reused at the intro")
