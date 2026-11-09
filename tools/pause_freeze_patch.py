import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# Sound: a helper that freezes every one-shot voice (guns, flame spray) and resumes exactly where
# it stopped, the same way the chase track already behaves.
p = ROOT + r"\scripts\sound.gd"
t = io.open(p, encoding="utf-8").read()

if "func freeze_voices" not in t:
    anchor = "func state_paused() -> bool:"
    assert t.count(anchor) == 1
    helper = '''## Freeze / unfreeze every one-shot voice so a paused run is a still frame, sound included.
func freeze_voices(on: bool) -> void:
	for v in voices:
		if is_instance_valid(v):
			v.stream_paused = on
	if is_instance_valid(music):
		music.stream_paused = on


'''
    t = t.replace(anchor, helper + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("sound.freeze_voices added")

# main: freeze the flame jet and the voices on pause, unfreeze on resume
p2 = ROOT + r"\scripts\main_3d.gd"
h = io.open(p2, encoding="utf-8").read()

if "func _freeze_world" not in h:
    anchor2 = "func close_shop() -> void:"
    assert h.count(anchor2) == 1
    helper2 = '''## A paused run is a still frame: stop emitting, freeze the particles mid-flight and hold the
## sound. Called from every path that enters or leaves "paused".
func _freeze_world(on: bool) -> void:
	if is_instance_valid(sound):
		sound.freeze_voices(on)
	if is_instance_valid(player) and is_instance_valid(player.flame_jet):
		player.flame_jet.process_mode = Node.PROCESS_MODE_DISABLED if on else Node.PROCESS_MODE_INHERIT
	if is_instance_valid(player) and is_instance_valid(player.flame_glow):
		player.flame_glow.visible = not on


'''
    h = h.replace(anchor2, helper2 + anchor2, 1)

pairs = (
    ('if state=="playing": state="paused"; _release_touches()',
     'if state=="playing":\n\t\t\tstate="paused"; _release_touches(); _freeze_world(true)'),
    ('if PAUSE_BUTTON.has_point(pos): state="paused"; _release_touches(); return true',
     'if PAUSE_BUTTON.has_point(pos):\n\t\t\tstate="paused"; _release_touches(); _freeze_world(true); return true'),
)
for old, new in pairs:
    if h.count(old) == 1:
        h = h.replace(old, new, 1)

io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("pause freezes the flame and the voices")
