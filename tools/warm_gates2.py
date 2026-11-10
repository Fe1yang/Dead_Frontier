import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

start = t.find("func _warm_gates() -> void:")
assert start > 0
end = t.find("func _finish_loading() -> void:", start)
assert end > start

replacement = '''## Gates are assembled on the frame they appear, and the expensive part turned out to be the
## Label3D text: every new string grows the font atlas and re-uploads it. Build two gates here
## using the REAL buff ids and texts for the current language, so every glyph is already baked.
func _warm_gates() -> void:
	var ids: Array = []
	for id in BuffCatalog.BUFFS.keys():
		ids.append(id)
	if ids.is_empty():
		return
	var chunks: Array = []
	var i := 0
	while i < ids.size():
		chunks.append(ids.slice(i, mini(i + 3, ids.size())))
		i += 3
	for chunk in chunks:
		var opts: Array = []
		for id in chunk:
			opts.append(_gate_option(String(id), 3))
		var g: Node3D = GateScript.new()
		g.position = Vector3(0, -60, 0)
		add_child(g)
		if g.has_method("setup"):
			g.setup(opts, language_code)
		g.visible = false
		g.queue_free()


'''
t = t[:start] + replacement + t[end:]
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("gate warm-up now uses the real buff text")
