import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func _finish_loading() -> void:
	if state!="loading": return
	var target:=loading_target'''
new = '''func _teardown_warmup() -> void:
	## The warm-up viewport holds throwaway zombies, pickups and crates. If the queue had not
	## drained by the time loading finished, they stayed alive at the origin and showed up as a
	## pile of zombies marching in place.
	warmup_queue.clear()
	for n in warmup_nodes:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.queue_free()
	warmup_nodes.clear()
	if is_instance_valid(warmup_view):
		warmup_view.queue_free()
	warmup_view = null
	warmup_root = null
	warmup_done = true


func _finish_loading() -> void:
	if state!="loading": return
	_teardown_warmup()
	var target:=loading_target'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("warm-up teardown added to _finish_loading")
