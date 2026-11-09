import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

# _prop centred the model on the wall plane, so half of every gun's depth sat behind the pegboard.
old_sig = "func _prop(path: String,length: float,pos: Vector3,yaw:=0.0,lay_long_axis_on_x:=false,rest:=true) -> Node3D:"
new_sig = "func _prop(path: String,length: float,pos: Vector3,yaw:=0.0,lay_long_axis_on_x:=false,rest:=true,stand_off:=false) -> Node3D:"
assert t.count(old_sig) == 1
t = t.replace(old_sig, new_sig, 1)

old_pos = "\tmodel.position+=offset\n\tholder.position=pos; holder.rotation.y=yaw"
new_pos = ("\tmodel.position+=offset\n"
           "\tif stand_off:\n"
           "\t\t# hung on the wall: keep the whole body in front of the pegboard\n"
           "\t\tmodel.position.z += box.size.z * 0.5 + 0.02\n"
           "\tholder.position=pos; holder.rotation.y=yaw")
assert t.count(old_pos) == 1
t = t.replace(old_pos, new_pos, 1)

old_call = "\t\tvar held:=_prop(item[0],item[1],item[2],PI if is_pistol else 0.0,true,false)"
new_call = "\t\tvar held:=_prop(item[0],item[1],item[2],PI if is_pistol else 0.0,true,false,true)"
assert t.count(old_call) == 1
t = t.replace(old_call, new_call, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("rack guns stand off the pegboard instead of sinking into it")
