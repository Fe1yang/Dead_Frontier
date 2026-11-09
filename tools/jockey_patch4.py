import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The asset only ships Dog_* clips, so "Zombie_Walk_Fwd" resolved to nothing and the jockey froze
# in its bind pose. Play the clip that is actually in the file.
old = '\tif kind=="jockey": clip_name="Zombie_Walk_Fwd"  # dog clips deform the human rig'
new = '\tif kind=="jockey": clip_name="Dog_Run"  # the only locomotion clip the asset ships'
assert t.count(old) == 1
t = t.replace(old, new, 1)

# ...and do not pitch the quadruped by hand: the clip already carries the crawl, and the extra
# 42 deg lean plus hip shift is what stretched the neck and pushed the hands into the road.
old_pose = '''	if kind=="jockey":
		var hip:=Vector3(0,0.53,0)
		var lean:=Basis(Vector3.RIGHT,deg_to_rad(JOCKEY_LEAN_DEG))
		model.transform=Transform3D(lean*model.basis,hip-lean*hip+Vector3(0,JOCKEY_DROP,0))'''
new_pose = '''	if kind=="jockey":
		# No hand-authored lean: the quadruped clip is the crawl. Only lift it clear of the road.
		model.transform=Transform3D(model.basis,Vector3(0,JOCKEY_DROP,0))'''
assert t.count(old_pose) == 1, t.count(old_pose)
t = t.replace(old_pose, new_pose, 1)

old_drop = "const JOCKEY_DROP:=0.02"
new_drop = "const JOCKEY_DROP:=0.10"
assert t.count(old_drop) == 1
t = t.replace(old_drop, new_drop, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey: Dog_Run plays again, no manual lean, lifted 0.10")
