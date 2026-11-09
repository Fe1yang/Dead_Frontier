import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '\tif kind=="jockey": clip_name="Jockey_Quad_Run"'
new = ('\tif kind=="jockey":\n'
       '\t\t# The current jockey is a quadruped shipped with dog clips; Jockey_Quad_Run only exists\n'
       '\t\t# in the old asset, so asking for it left the jockey sliding with no animation.\n'
       '\t\tclip_name = "Jockey_Quad_Run"\n'
       '\t\tif animation_player and not animation_player.has_animation(clip_name):\n'
       '\t\t\tclip_name = "Dog_Run" if animation_player.has_animation("Dog_Run") else clip_name')

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey falls back to its dog run clip")
