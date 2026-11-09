import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) the wolfdog was facing away from the camera
old_wolf = '{"asset":"res://assets/models/pets/czech_wolfdog.glb","name":"捷克狼犬","length":0.98,"yaw":1.5708}'
new_wolf = '{"asset":"res://assets/models/pets/czech_wolfdog.glb","name":"捷克狼犬","length":0.98,"yaw":-1.5708}'
assert t.count(old_wolf) == 1
t = t.replace(old_wolf, new_wolf, 1)

# 2) never let two animals share the stage: sweep any stragglers before the new one is added
old_add = "\tadd_child(pet); ModelFix.double_sided(pet)"
new_add = (
    "\t# queue_free is deferred, so a fast switch could leave the previous animal on stage and\n"
    "\t# the tiger and lion ended up standing inside each other. Sweep every tagged pet first.\n"
    "\tfor child in get_children():\n"
    "\t\tif child.has_meta(\"lobby_pet\"):\n"
    "\t\t\tchild.visible = false\n"
    "\t\t\tif child.get_parent() != null:\n"
    "\t\t\t\tchild.get_parent().remove_child(child)\n"
    "\t\t\tchild.queue_free()\n"
    "\tadd_child(pet); pet.set_meta(\"lobby_pet\", true); ModelFix.double_sided(pet)"
)
assert t.count(old_add) == 1
t = t.replace(old_add, new_add, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("wolfdog faces the camera; pet switching sweeps stragglers")
