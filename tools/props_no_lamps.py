import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The districts already ship their own lamp posts (and the lights are wired to them), so adding a
# second set was what put duplicate poles near the kerb. Drop them.
start = t.find("\t# --- lamps: three block types")
end = t.find("\t# --- things that stand against the buildings")
assert start > 0 and end > start
t = t[:start] + t[end:]

# small props move to the inner half of the pavement, clear of the kerb line
repl = (
    ("var x_wall: float = side * 6.95", "var x_wall: float = side * 7.10"),
    ("side * 6.05", "side * 6.60"),
    ("side * 5.90", "side * 6.35"),
    ("side * 5.45", "side * 6.15"),
    ("side * 5.75 + decor_rng.randf_range(-0.15, 0.15)", "side * 6.20 + decor_rng.randf_range(-0.15, 0.15)"),
    ("decor_rng.randf_range(5.1, 7.2)", "decor_rng.randf_range(6.0, 7.4)"),
)
for old, new in repl:
    assert t.count(old) >= 1, old
    t = t.replace(old, new)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("duplicate lamps removed; small props pushed to the inner pavement")
