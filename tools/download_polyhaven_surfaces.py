from pathlib import Path
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'textures' / 'polyhaven'
OUT.mkdir(parents=True, exist_ok=True)
ASSETS = ['asphalt_02', 'concrete_wall_003', 'red_brick_plaster_patch_02', 'concrete_pavement', 'plastered_wall']
MAPS = {'Diffuse': 'diff', 'nor_gl': 'nor_gl', 'Rough': 'rough', 'AO': 'ao'}
sources = {}

def download(url, path):
    if path.exists() and path.stat().st_size > 1024:
        print('REUSE', path.name, path.stat().st_size)
        return
    request = urllib.request.Request(url, headers={'User-Agent': 'DeadRun-Game-Prototype/1.0'})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
    path.write_bytes(data)
    print('DOWNLOADED', path.name, len(data))

for asset in ASSETS:
    with urllib.request.urlopen(f'https://api.polyhaven.com/files/{asset}', timeout=60) as response:
        manifest = json.load(response)
    sources[asset] = {'license': 'CC0-1.0', 'page': f'https://polyhaven.com/a/{asset}', 'files': {}}
    for key, suffix in MAPS.items():
        if key not in manifest:
            continue
        info = manifest[key]['2k']['jpg']
        filename = f'{asset}_{suffix}_2k.jpg'
        download(info['url'], OUT / filename)
        sources[asset]['files'][suffix] = {'file': filename, 'md5': info['md5'], 'url': info['url']}

sky = 'kloofendal_48d_partly_cloudy_puresky'
with urllib.request.urlopen(f'https://api.polyhaven.com/files/{sky}', timeout=60) as response:
    manifest = json.load(response)
info = manifest['hdri']['2k']['hdr']
sky_out = ROOT / 'assets' / 'sky' / 'day_partly_cloudy_2k.hdr'
download(info['url'], sky_out)
sources[sky] = {'license': 'CC0-1.0', 'page': f'https://polyhaven.com/a/{sky}', 'file': sky_out.name, 'url': info['url']}
(OUT / 'sources.json').write_text(json.dumps(sources, indent=2), encoding='utf-8')
print('POLYHAVEN_SURFACES_READY', len(sources))
