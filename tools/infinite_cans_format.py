import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# the can counter shows current/cap, so endless reads as infinity over infinity
t = t.replace(
    'var cans: String="∞" if game.infinite_resources() else "%d/%d"%[game.stamina.value,game.stamina.CAP]',
    'var cans: String="∞/∞" if game.infinite_resources() else "%d/%d"%[game.stamina.value,game.stamina.CAP]',
)
t = t.replace(
    'var cans: String="∞" if inf else "%d/%d"%[game.stamina.value,game.stamina.CAP]',
    'var cans: String="∞/∞" if inf else "%d/%d"%[game.stamina.value,game.stamina.CAP]',
)
t = t.replace(
    'bold.get_string_size(cans,HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x',
    'bold.get_string_size(cans,HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x',
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("can counter reads infinity/infinity")
