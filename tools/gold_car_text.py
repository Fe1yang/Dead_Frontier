import io
import re

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"

NAME = {
    "en": "Golden Supercar", "zh_CN": "金色跑车", "zh_TW": "金色跑車",
    "ja": "ゴールドスーパーカー", "ko": "골드 슈퍼카", "es": "Superdeportivo dorado",
    "fr": "Supercar dorée", "de": "Goldener Supersportwagen", "pt": "Supercarro dourado",
    "ru": "Золотой суперкар", "ar": "سيارة خارقة ذهبية", "hi": "गोल्डन सुपरकार",
    "id": "Supercar Emas", "it": "Supercar dorata", "tr": "Altın Süper Araba",
    "nl": "Gouden supercar", "pl": "Złoty supersamochód", "th": "ซูเปอร์คาร์สีทอง",
    "vi": "Siêu xe vàng", "uk": "Золотий суперкар",
}
DESC = {
    "en": "Gold plated supercar · no guns, ploughs through wrecks and rams the horde · first 1000m every run, until it breaks",
    "zh_CN": "纯金涂装超跑 · 不开枪，直接冲过路障、撞飞僵尸 · 每局前1000米自动行驶，直到损坏",
    "zh_TW": "純金塗裝超跑 · 不開槍，直接衝過路障、撞飛殭屍 · 每局前1000公尺自動行駛，直到損壞",
    "ja": "純金のスーパーカー · 銃は使わず障害物を突き破りゾンビを跳ね飛ばす · 毎回最初の1000mを自動走行、壊れるまで",
    "ko": "순금 슈퍼카 · 총 없이 장애물을 뚫고 좀비를 치어버림 · 매 판 첫 1000m 자동 주행, 파손될 때까지",
    "es": "Superdeportivo bañado en oro · sin armas, arrasa obstáculos y embiste a la horda · primeros 1000m de cada partida, hasta romperse",
    "fr": "Supercar plaquée or · sans armes, traverse les épaves et percute la horde · 1000 premiers mètres de chaque partie, jusqu'à la casse",
    "de": "Vergoldeter Supersportwagen · keine Waffen, durchbricht Wracks und rammt die Horde · erste 1000 m jeder Runde, bis er kaputtgeht",
    "pt": "Supercarro banhado a ouro · sem armas, atravessa destroços e atropela a horda · primeiros 1000m de cada partida, até quebrar",
    "ru": "Позолоченный суперкар · без оружия, пробивает завалы и давит орду · первые 1000 м каждого забега, пока не сломается",
    "ar": "سيارة خارقة مطلية بالذهب · بلا أسلحة، تخترق الحطام وتدهس الحشد · أول 1000 متر من كل جولة حتى تتحطم",
    "hi": "सोने की परत वाली सुपरकार · बिना बंदूक, मलबे को तोड़ती और भीड़ को कुचलती है · हर रन के पहले 1000 मीटर, टूटने तक",
    "id": "Supercar berlapis emas · tanpa senjata, menerobos reruntuhan dan menabrak gerombolan · 1000m pertama tiap permainan, sampai rusak",
    "it": "Supercar placcata oro · senza armi, sfonda i rottami e travolge l'orda · primi 1000m di ogni partita, finché non si rompe",
    "tr": "Altın kaplama süper araba · silahsız, enkazı deler ve sürüyü ezer · her oyunda ilk 1000m, kırılana kadar",
    "nl": "Vergulde supercar · geen wapens, ramt wrakken en de horde · eerste 1000m van elke run, tot hij stukgaat",
    "pl": "Złoty supersamochód · bez broni, przebija wraki i tratuje hordę · pierwsze 1000 m każdego biegu, aż się zepsuje",
    "th": "ซูเปอร์คาร์ชุบทอง · ไม่มีปืน ทะลุซากและชนฝูงซอมบี้ · วิ่งอัตโนมัติ 1000 เมตรแรกของทุกตา จนพัง",
    "vi": "Siêu xe mạ vàng · không súng, xuyên qua xác xe và húc văng bầy zombie · 1000m đầu mỗi ván, cho đến khi hỏng",
    "uk": "Позолочений суперкар · без зброї, пробиває завали й тисне орду · перші 1000 м кожного забігу, доки не зламається",
}

lines = io.open(P, encoding="utf-8").read().split("\n")
lang_re = re.compile(r'^\t"([a-zA-Z_]{2,7})":\{')
patched = 0

for i, line in enumerate(lines):
    m = lang_re.match(line)
    if not m:
        continue
    lang = m.group(1)
    if lang not in NAME:
        continue
    if '"gold_car":"' in line:
        continue
    ins = '"gold_car":"%s","gold_car_desc":"%s",' % (NAME[lang], DESC[lang])
    lines[i] = line.replace(m.group(0), m.group(0) + ins, 1)
    patched += 1

io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("languages given the gold car text:", patched)
