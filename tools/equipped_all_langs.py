import io
import re

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_text.gd"

# "already equipped" in every language the store carries
TEXT = {
    "en": "ALREADY EQUIPPED",
    "zh_CN": "已装备",
    "zh_TW": "已裝備",
    "ja": "装備済み",
    "ko": "장착 완료",
    "es": "YA EQUIPADO",
    "fr": "DÉJÀ ÉQUIPÉ",
    "de": "BEREITS AUSGERÜSTET",
    "pt": "JÁ EQUIPADO",
    "ru": "УЖЕ НАДЕТО",
    "ar": "مُجهّز بالفعل",
    "hi": "पहले से सुसज्जित",
    "id": "SUDAH DIPAKAI",
    "it": "GIÀ EQUIPAGGIATO",
    "tr": "ZATEN KUŞANILDI",
    "nl": "AL UITGERUST",
    "pl": "JUŻ ZAŁOŻONE",
    "th": "ติดตั้งแล้ว",
    "vi": "ĐÃ TRANG BỊ",
    "uk": "УЖЕ ВДЯГНУТО",
}

src = io.open(P, encoding="utf-8").read()

added = 0
for lang, text in TEXT.items():
    marker = '"%s":{' % lang
    if marker not in src:
        print("missing language block:", lang)
        continue
    if src.split(marker, 1)[1][:30].find("char_equipped") != -1:
        continue
    src = src.replace(marker, '%s"char_equipped":"%s",' % (marker, text), 1)
    added += 1

io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("languages patched:", added)
