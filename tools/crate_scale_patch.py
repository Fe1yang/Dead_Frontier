import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

start = next(i for i, l in enumerate(lines) if l.strip().startswith("var c := MeshInstance3D.new(); c.mesh = crate_mesh"))
end = start
while not lines[end + 1].strip().startswith("if latch_mesh"):
    end += 1

block = [
    "\t\t# Size the case from its own bounds: the old fixed 2.9 multiplier only looked right",
    "\t\t# while the ammo can was the body. The truck is authored much larger, so at 2.9 it",
    "\t\t# turned into a wall of green across the road.",
    "\t\tvar c := MeshInstance3D.new()",
    "\t\tc.mesh = crate_mesh",
    "\t\tvar span := c.get_aabb()",
    "\t\tvar longest: float = maxf(span.size.x, maxf(span.size.y, span.size.z))",
    "\t\tvar k: float = 1.70 / maxf(longest, 0.01)",
    "\t\tc.scale = Vector3.ONE * k",
    "\t\tc.position = Vector3(-span.get_center().x * k, -span.position.y * k, -span.get_center().z * k)",
    "\t\tbody.add_child(c)",
]

lines[start:end + 1] = block
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("crate case now normalised by its own bounds (1.7 m)")
