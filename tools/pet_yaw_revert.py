import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pet_companion_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The lobby needs that offset to face the camera; in a run the models already point down the
# road, so applying it made the wolfdog, tiger and lion run sideways.
t = t.replace("\trotation.y=lerp_angle(rotation.y,atan2(Vector3.FORWARD.x,Vector3.FORWARD.z)+yaw_offset,1.0-exp(-delta*12.0))",
              "\trotation.y=lerp_angle(rotation.y,atan2(Vector3.FORWARD.x,Vector3.FORWARD.z),1.0-exp(-delta*12.0))", 1)
t = t.replace("\trotation.y=lerp_angle(rotation.y,yaw+yaw_offset,1.0-exp(-delta*12.0))",
              "\trotation.y=lerp_angle(rotation.y,yaw,1.0-exp(-delta*12.0))", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("run facing restored")
