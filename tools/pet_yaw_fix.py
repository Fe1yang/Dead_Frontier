import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pet_companion_3d.gd"
t = io.open(p, encoding="utf-8").read()

# per-breed facing correction, taken from the same table the lobby uses
if "var yaw_offset" not in t:
    anchor = "var anim: AnimationPlayer"
    assert t.count(anchor) == 1
    t = t.replace(anchor, "var yaw_offset := 0.0   # the model's own forward axis, per breed\nvar anim: AnimationPlayer", 1)

old_setup = "\tbase_y=ModelFix.fit_pet(model,float(LobbyScene.PETS[breed].get(\"length\",1.1)))"
new_setup = ("\tyaw_offset=float(LobbyScene.PETS[breed].get(\"yaw\",0.0))\n"
             "\tbase_y=ModelFix.fit_pet(model,float(LobbyScene.PETS[breed].get(\"length\",1.1)))")
assert t.count(old_setup) == 1
t = t.replace(old_setup, new_setup, 1)

# the intro path forced one constant heading, so the dog ran sideways wherever it started
old_beside = "\trotation.y=lerp_angle(rotation.y,atan2(Vector3.FORWARD.x,Vector3.FORWARD.z),1.0-exp(-delta*12.0))"
new_beside = "\trotation.y=lerp_angle(rotation.y,atan2(Vector3.FORWARD.x,Vector3.FORWARD.z)+yaw_offset,1.0-exp(-delta*12.0))"
assert t.count(old_beside) == 1
t = t.replace(old_beside, new_beside, 1)

# run facing: add the breed offset so the wolfdog's nose points down the road
old_yaw = "\trotation.y=lerp_angle(rotation.y,yaw,1.0-exp(-delta*12.0))"
new_yaw = "\trotation.y=lerp_angle(rotation.y,yaw+yaw_offset,1.0-exp(-delta*12.0))"
assert t.count(old_yaw) == 1
t = t.replace(old_yaw, new_yaw, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pets honour their per-breed facing offset")
