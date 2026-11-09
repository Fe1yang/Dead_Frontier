import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "DogGallop" not in t:
    anchor = "const JOCKEY_LEAN_DEG:=42.0"
    assert t.count(anchor) == 1
    t = t.replace(
        anchor,
        'const DogGallop=preload("res://scripts/dog_gallop.gd")\n## Quadruped gallop driver for the jockey: its baked Dog_Run clip barely moves the legs, so the\n## procedural stride does the work (same helper the pets use).\nvar jockey_gallop: RefCounted\n' + anchor,
        1,
    )

# build the gallop once the skeleton exists
old_build = '\tif kind=="jockey":\n\t\tmodel.scale *= JOCKEY_SCALE'
if old_build in t and "jockey_gallop=DogGallop" not in t:
    t = t.replace(
        old_build,
        old_build + '\n\t\tvar sk: Skeleton3D = model.find_child("Skeleton3D", true, false) as Skeleton3D\n\t\tif sk != null:\n\t\t\tjockey_gallop = DogGallop.new(sk, {})',
        1,
    )

# advance the stride with the zombie's own movement
old_move = "\tposition.z += speed*move_scale*delta"
if "jockey_gallop.step" not in t:
    t = t.replace(
        old_move,
        old_move + '\n\tif kind=="jockey" and jockey_gallop != null:\n\t\tjockey_gallop.step(delta, 1.25)',
        1,
    )

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey drives the procedural gallop")
