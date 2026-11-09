import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# do not leave the loading screen until the warm-up queue has drained: the bar simply stays up a
# moment longer, which is invisible to the player and removes the leftover preview nodes
old = "\tif loading_time>=loading_duration and districts_ready:"
new = "\tif loading_time>=loading_duration and districts_ready and (loading_target!=\"run\" or warmup_done or warmup_queue.is_empty()):"

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("loading waits for the warm-up queue to drain")
