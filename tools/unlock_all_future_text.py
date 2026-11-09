import io
import re

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"

# the sentence to append to the existing "unlock all" description, per language
EXTRA = {
    "en": "Every item and resource added in future updates is yours free, forever.",
    "zh_CN": "今后更新新增的所有物品与资源同样免费永久拥有。",
    "zh_TW": "今後更新新增的所有物品與資源同樣免費永久擁有。",
    "ja": "今後のアップデートで追加されるアイテムとリソースもすべて無料で永久に手に入ります。",
    "ko": "앞으로 추가되는 모든 아이템과 자원도 무료로 영구 제공됩니다.",
    "es": "Todo lo que se añada en futuras actualizaciones es tuyo gratis para siempre.",
    "fr": "Tout ce qui sera ajouté dans les futures mises à jour vous appartient gratuitement, pour toujours.",
    "de": "Alles, was in künftigen Updates dazukommt, gehört dir dauerhaft kostenlos.",
    "pt": "Tudo o que for adicionado em atualizações futuras é seu de graça, para sempre.",
    "ru": "Всё, что появится в будущих обновлениях, бесплатно и навсегда ваше.",
    "ar": "كل ما يُضاف في التحديثات القادمة سيكون لك مجانًا إلى الأبد.",
    "hi": "आगे के अपडेट में जुड़ने वाली हर चीज़ हमेशा के लिए मुफ़्त रहेगी।",
    "id": "Semua item dan sumber daya pada pembaruan berikutnya gratis selamanya.",
    "it": "Tutto ciò che arriverà nei futuri aggiornamenti è tuo gratis, per sempre.",
    "tr": "Gelecek güncellemelerde eklenen her şey sonsuza dek ücretsiz senin.",
    "nl": "Alles wat in toekomstige updates verschijnt, is voor altijd gratis van jou.",
    "pl": "Wszystko, co pojawi się w przyszłych aktualizacjach, jest Twoje bezpłatnie na zawsze.",
    "th": "ทุกไอเทมและทรัพยากรที่เพิ่มในอัปเดตหน้าจะเป็นของคุณฟรีตลอดไป",
    "vi": "Mọi vật phẩm và tài nguyên trong các bản cập nhật sau đều miễn phí mãi mãi.",
    "uk": "Усе, що з'явиться в майбутніх оновленнях, безкоштовне й ваше назавжди.",
}

lines = io.open(P, encoding="utf-8").read().split("\n")
lang = None
patched = 0
lang_re = re.compile(r'^\t"([a-zA-Z_]{2,7})":\{')

for i, line in enumerate(lines):
    m = lang_re.match(line)
    if m:
        lang = m.group(1)
    if lang is None or '"unlock_all_desc":"' not in line:
        continue
    extra = EXTRA.get(lang)
    if extra is None:
        continue
    if extra in line:
        continue
    line = line.replace('"unlock_all_desc":"', '"unlock_all_desc":"' + extra + " ", 1)
    lines[i] = line
    patched += 1

io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("descriptions extended:", patched)
