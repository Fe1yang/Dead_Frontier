import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

targets = []

# weight-fix backups and the abandoned boss variant
for name in (
    r"assets\models\actors\pursuer_abomination_pre_weightfix.glb",
    r"assets\models\actors\pursuer_abomination_before_weights.glb",
    r"assets\models\actors\boss_chaser.glb",
    r"assets\models\pets\boss_chaser.glb",
    r"assets\models\actors\zombie_walker.glb",
    r"assets\models\pets\zombie_walker.glb",
):
    targets.append(name)

# loose Blender textures: every GLB embeds its own maps, none reference these
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "assets", "models")):
    for fn in filenames:
        low = fn.lower()
        if low.endswith((".bak", ".blend1")):
            targets.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))
            continue
        if not low.endswith(".png"):
            continue
        if any(k in fn for k in ("_NormalGL", "_ORM", "_Color", "_AlbedoTransparency", "_Roughness", "_Metallic", "_BaseColor")):
            targets.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))

# orphaned import metadata for files that no longer exist
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "assets")):
    for fn in filenames:
        if not fn.endswith(".import"):
            continue
        source = os.path.join(dirpath, fn[:-7])
        if not os.path.exists(source):
            targets.append(os.path.relpath(os.path.join(dirpath, fn), ROOT))

freed = 0
removed = 0
for rel in targets:
    full = os.path.join(ROOT, rel)
    if not os.path.exists(full):
        continue
    size = os.path.getsize(full)
    os.remove(full)
    freed += size
    removed += 1

print("removed %d files, freed %.1f MB" % (removed, freed / 1048576.0))
