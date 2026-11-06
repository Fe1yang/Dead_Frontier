import bpy, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTORS = ROOT / 'assets' / 'models' / 'actors'

def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

def fatten(src: str, dst: str, belly: float = 1.0) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ACTORS / src))
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        verts = ob.data.vertices
        zvals = [v.co.z for v in verts]
        if not zvals:
            continue
        z_top = max(zvals)
        # 只在接近人体比例的网格上做（跳过眼睛等小附件：它们的 z 范围也在腹部就一起胖，无碍）
        for v in verts:
            co = v.co
            z = co.z
            # 肚皮鼓包：峰值在身高 55% 附近，向上下平滑衰减
            peak = z_top * (0.56 if z_top > 1.2 else 0.5)
            span = z_top * 0.26
            t = smooth(1.0 - abs(z - peak) / span)
            if t <= 0.0:
                continue
            # 腰围 X 方向撑开，前后 Y 方向更夸张（啤酒肚）
            co.x *= 1.0 + 0.62 * belly * t
            co.y *= 1.0 + 0.95 * belly * t
            # 肚子略微下垂
            co.z -= 0.02 * belly * t
        ob.data.update()
    bpy.ops.export_scene.gltf(
        filepath=str(ACTORS / dst),
        export_format='GLB',
        export_animations=True,
        export_skins=True,
        export_apply=False,
    )
    print('fattened', src, '->', dst)

fatten('zombie_walker_universal.glb', 'zombie_bomber_universal.glb', 1.0)
fatten('zombie_female_universal.glb', 'zombie_bomber_female_universal.glb', 0.9)
