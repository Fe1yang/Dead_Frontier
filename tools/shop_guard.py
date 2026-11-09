import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if not ResourceLoader.exists(path): return null
	var holder:=Node3D.new(); add_child(holder)
	var model:=load(path).instantiate() as Node3D; holder.add_child(model)'''
new = '''	if not ResourceLoader.exists(path): return null
	# A stale import (the .glb is on disk but its imported scene is broken) used to crash the
	# whole shop with "instantiate on a null instance".
	var packed:=load(path) as PackedScene
	if packed==null:
		push_warning("shop prop failed to load: "+path)
		return null
	var holder:=Node3D.new(); add_child(holder)
	var model:=packed.instantiate() as Node3D
	if model==null:
		holder.queue_free()
		return null
	holder.add_child(model)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# the rack must survive a missing gun
old_rack = '''		var held:=_prop(item[0],item[1],item[2],PI if is_pistol else 0.0,true,false,true)
		var file: String=String(item[0]).get_file()
		if RACK_KEYS.has(file) and not props.has(RACK_KEYS[file]): _register(RACK_KEYS[file],held)'''
new_rack = '''		var held:=_prop(item[0],item[1],item[2],PI if is_pistol else 0.0,true,false,true)
		var file: String=String(item[0]).get_file()
		if held!=null and RACK_KEYS.has(file) and not props.has(RACK_KEYS[file]): _register(RACK_KEYS[file],held)'''
assert t.count(old_rack) == 1, t.count(old_rack)
t = t.replace(old_rack, new_rack, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("shop survives a broken prop import")
