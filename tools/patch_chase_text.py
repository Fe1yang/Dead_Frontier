# Patch the mid-run chase banner: make it clear the giant must be SURVIVED, not killed.
# zh source: 坚持下去！巨人来了。
import io, re, sys

PATH = "scripts/run_text.gd"
src = io.open(PATH, encoding="utf-8").read()

NEW = {
    "en": "HOLD ON! THE GIANT IS HERE!",
    "zh_CN": "坚持下去！巨人来了。",
    "zh_TW": "堅持下去！巨人來了。",
    "ja": "耐えろ！巨人が来た！",
    "ko": "버텨라! 거인이 왔다!",
    "es": "¡AGUANTA! ¡LLEGA EL GIGANTE!",
    "fr": "TIENS BON ! LE GÉANT ARRIVE !",
    "de": "DURCHHALTEN! DER RIESE KOMMT!",
    "pt": "AGUENTA! O GIGANTE CHEGOU!",
    "ru": "ДЕРЖИСЬ! ГИГАНТ ЗДЕСЬ!",
    "ar": "اصمد! العملاق قادم!",
    "hi": "टिके रहो! दैत्य आ गया!",
    "id": "BERTAHAN! RAKSASA DATANG!",
    "it": "RESISTI! IL GIGANTE È ARRIVATO!",
    "tr": "DAYAN! DEV GELDİ!",
    "nl": "VOLHOUDEN! DE REUS IS ER!",
    "pl": "WYTRZYMAJ! OLBRZYM NADCHODZI!",
    "th": "อดทนไว้! ยักษ์มาแล้ว!",
    "vi": "CỐ LÊN! NGƯỜI KHỔNG LỒ TỚI!",
    "uk": "ТРИМАЙСЯ! ГІГАНТ ТУТ!",
}

# Each language block has exactly one "chase":"..." entry; replace them in file order.
order = ["en","zh_CN","zh_TW","ja","ko","es","fr","de","pt","ru","ar","hi","id","it","tr","nl","pl","th","vi","uk"]
hits = list(re.finditer(r'"chase":"[^"]*"', src))
assert len(hits) == 20, "expected 20 chase entries, found %d" % len(hits)

out = src
for lang, m in zip(order, reversed(hits)):
    pass
# rebuild from the end so offsets stay valid
out = src
for lang, m in zip(reversed(order), reversed(hits)):
    out = out[:m.start()] + '"chase":"' + NEW[lang] + '"' + out[m.end():]

# sanity: every language's new text is present, no old banner left
for lang in order:
    assert '"chase":"' + NEW[lang] + '"' in out, lang
for old in ["CHASE!","巨兽追击！","巨獸追擊！","追跡！","추격!","¡PERSECUCIÓN!","POURSUIVE !","VERFOLGUNG!","PERSEGUIÇÃO!","ПОГОНЯ!","مطاردة!","पीछा!","KEJARAN!","INSEGUIMENTO!","KOVALAMACA!","ACHTERVOLGING!","POŚCIG!","ไล่ล่า!","TRUY ĐUỔI!","ПЕРЕСЛІДУВАННЯ!"]:
    assert ('"chase":"' + old + '"') not in out, old

io.open(PATH, "w", encoding="utf-8", newline="\n").write(out)
print("OK patched 20 chase banners")
