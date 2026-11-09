import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

repl = (
    # lift the loose gear off the crates and pull it towards the aisle so nothing intersects
    ('_prop("res://assets/models/medkit.glb",0.30,Vector3(-0.35,top,-0.70),0.15)',
     '_prop("res://assets/models/medkit.glb",0.30,Vector3(-0.35,top+0.07,-0.55),0.15)'),
    ('_prop("res://assets/models/medkit.glb",0.30,Vector3(0.00,top,-0.72),-0.1)',
     '_prop("res://assets/models/medkit.glb",0.30,Vector3(0.00,top+0.07,-0.57),-0.1)'),
    ('_prop("res://assets/models/helmet.glb",0.30,Vector3(0.45,top,-0.70),0.6)',
     '_prop("res://assets/models/helmet.glb",0.30,Vector3(0.45,top+0.07,-0.55),0.6)'),
    ('_prop("res://assets/models/helmet.glb",0.30,Vector3(0.82,top,-0.72),-0.4)',
     '_prop("res://assets/models/helmet.glb",0.30,Vector3(0.82,top+0.07,-0.57),-0.4)'),
    ('_prop("res://assets/models/ammo_pickup.glb",0.28,Vector3(2.32,1.57,-0.66),0.2)',
     '_prop("res://assets/models/ammo_pickup.glb",0.28,Vector3(2.32,1.64,-0.52),0.2)'),
)

for old, new in repl:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("shelf gear lifted and pulled forward clear of the crates")
