import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_text.gd"

EQUIP = {
    "en": "EQUIP", "zh_CN": "装备", "zh_TW": "裝備", "ja": "装備", "ko": "장착",
    "es": "EQUIPAR", "fr": "ÉQUIPER", "de": "AUSRÜSTEN", "pt": "EQUIPAR", "ru": "НАДЕТЬ",
    "ar": "تجهيز", "hi": "सुसज्जित करें", "id": "PAKAI", "it": "EQUIPAGGIA",
    "tr": "KUŞAN", "nl": "UITRUSTEN", "pl": "ZAŁÓŻ", "th": "ติดตั้ง",
    "vi": "TRANG BỊ", "uk": "ВДЯГНУТИ",
}

src = io.open(P, encoding="utf-8").read()
added = 0
for lang, text in EQUIP.items():
    marker = '"%s":{' % lang
    if marker not in src:
        print("missing block:", lang)
        continue
    head = src.split(marker, 1)[1][:40]
    if "btn_equip" in head:
        continue
    src = src.replace(marker, '%s"btn_equip":"%s",' % (marker, text), 1)
    added += 1

io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("btn_equip added to", added, "languages")
