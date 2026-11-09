import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) the gear icon must go through clean_ops, otherwise the panel painted after it hides it
p = ROOT + r"\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()

old = '''func _gear_icon(c: Vector2,k:=1.0,tint: Color=WHITE) -> void:
	draw_arc(c,13*k,0,TAU,24,tint,3.0*k)
	for i in range(8):
		var a:=i*TAU/8.0
		draw_line(c+Vector2(cos(a),sin(a))*13*k,c+Vector2(cos(a),sin(a))*19*k,tint,5.0*k)
	draw_circle(c,5*k,tint)'''

new = '''func _gear_icon(c: Vector2,k:=1.0,tint: Color=WHITE) -> void:
	# drawn through the clean layer: an immediate draw_arc sits BEHIND the panel fill and the
	# white gear comes out grey
	var ring := PackedVector2Array()
	for i in range(25):
		var a := TAU * float(i) / 24.0
		ring.append(c + Vector2(cos(a), sin(a)) * 13.0 * k)
	clean_ops.append(["line", ring, tint, 3.0 * k])
	for i in range(8):
		var a:=i*TAU/8.0
		clean_ops.append(["line", PackedVector2Array([c+Vector2(cos(a),sin(a))*13*k,c+Vector2(cos(a),sin(a))*19*k]), tint, 5.0*k])
	clean_ops.append(["circle", c, 5.0 * k, tint])'''

assert h.count(old) == 1, h.count(old)
h = h.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("gear icon routed through clean_ops")

# 2) push the right-hand column to the screen edge
p2 = ROOT + r"\scripts\main_3d.gd"
t = io.open(p2, encoding="utf-8").read()
moved = 0
for y in (118, 198, 358, 438, 518, 598):
    old_r = "Rect2(464,%d,70,76)" % y
    if old_r in t:
        t = t.replace(old_r, "Rect2(470,%d,70,76)" % y)
        moved += 1
io.open(p2, "w", encoding="utf-8", newline="\n").write(t)
print("side icons moved to x=470:", moved)
