import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"
t = io.open(p, encoding="utf-8").read()

BLURB = {
    "en": "Unlocks every survivor, pet, vehicle and weapon, and gives endless coins, silver, vouchers and cans. Every item and resource added in future updates is yours free, forever.",
    "zh_CN": "解锁全部角色、宠物、载具与武器，金币、银币、兑换券、能量罐无限。今后更新新增的所有物品与资源同样免费永久拥有。",
    "zh_TW": "解鎖全部角色、寵物、載具與武器，金幣、銀幣、兌換券、能量罐無限。今後更新新增的所有物品與資源同樣免費永久擁有。",
    "ja": "すべてのサバイバー・ペット・車両・武器を解放し、コイン・銀貨・引換券・缶が無限になります。今後のアップデートで追加されるアイテムとリソースもすべて無料で永久に手に入ります。",
    "ko": "모든 생존자, 펫, 차량, 무기를 해금하고 코인, 은화, 교환권, 캔을 무한으로 제공합니다. 앞으로 추가되는 모든 아이템과 자원도 무료로 영구 제공됩니다.",
    "es": "Desbloquea todos los supervivientes, mascotas, vehículos y armas, y da monedas, plata, cupones y latas infinitas. Todo lo que se añada en futuras actualizaciones es tuyo gratis para siempre.",
    "fr": "Débloque tous les survivants, animaux, véhicules et armes, et donne pièces, argent, bons et canettes à l'infini. Tout ce qui sera ajouté dans les futures mises à jour vous appartient gratuitement, pour toujours.",
    "de": "Schaltet alle Überlebenden, Tiere, Fahrzeuge und Waffen frei und gibt unendlich Münzen, Silber, Gutscheine und Dosen. Alles, was in künftigen Updates dazukommt, gehört dir dauerhaft kostenlos.",
    "pt": "Desbloqueia todos os sobreviventes, pets, veículos e armas, e dá moedas, prata, cupons e latas infinitos. Tudo o que for adicionado em atualizações futuras é seu de graça, para sempre.",
    "ru": "Открывает всех выживших, питомцев, транспорт и оружие, а монеты, серебро, купоны и банки становятся бесконечными. Всё, что появится в будущих обновлениях, бесплатно и навсегда ваше.",
    "ar": "يفتح كل الناجين والحيوانات والمركبات والأسلحة، ويمنحك عملات وفضة وقسائم وعلبًا بلا حدود. كل ما يُضاف في التحديثات القادمة سيكون لك مجانًا إلى الأبد.",
    "hi": "सभी सर्वाइवर, पालतू, वाहन और हथियार खोलता है, और सिक्के, चांदी, कूपन व कैन असीमित करता है। आगे के अपडेट में जुड़ने वाली हर चीज़ हमेशा के लिए मुफ़्त रहेगी।",
    "id": "Membuka semua penyintas, hewan, kendaraan, dan senjata, serta koin, perak, kuota, dan kaleng tanpa batas. Semua item dan sumber daya pada pembaruan berikutnya gratis selamanya.",
    "it": "Sblocca tutti i sopravvissuti, gli animali, i veicoli e le armi, e rende infinite monete, argento, buoni e lattine. Tutto ciò che arriverà nei futuri aggiornamenti è tuo gratis, per sempre.",
    "tr": "Tüm hayatta kalanları, evcil hayvanları, araçları ve silahları açar; jeton, gümüş, kupon ve kutuları sonsuz yapar. Gelecek güncellemelerde eklenen her şey sonsuza dek ücretsiz senin.",
    "nl": "Ontgrendelt alle overlevenden, huisdieren, voertuigen en wapens en geeft oneindig munten, zilver, tegoeden en blikjes. Alles wat in toekomstige updates verschijnt, is voor altijd gratis van jou.",
    "pl": "Odblokowuje wszystkich ocalałych, zwierzęta, pojazdy i broń oraz daje nieskończone monety, srebro, kupony i puszki. Wszystko, co pojawi się w przyszłych aktualizacjach, jest Twoje bezpłatnie na zawsze.",
    "th": "ปลดล็อกผู้รอดชีวิต สัตว์เลี้ยง ยานพาหนะ และอาวุธทั้งหมด พร้อมเหรียญ เงิน คูปอง และกระป๋องแบบไม่จำกัด ทุกไอเทมและทรัพยากรที่เพิ่มในอัปเดตหน้าจะเป็นของคุณฟรีตลอดไป",
    "vi": "Mở khóa mọi người sống sót, thú nuôi, phương tiện và vũ khí, đồng thời cho xu, bạc, phiếu và lon không giới hạn. Mọi vật phẩm và tài nguyên trong các bản cập nhật sau đều miễn phí mãi mãi.",
    "uk": "Відкриває всіх уцілілих, улюбленців, транспорт і зброю, а монети, срібло, купони й бляшанки стають безмежними. Усе, що з'явиться в майбутніх оновленнях, безкоштовне й ваше назавжди.",
}

added = 0
for lang, text in BLURB.items():
    marker = '"%s":{' % lang
    if marker not in t:
        continue
    if t.split(marker, 1)[1][:80].find("unlock_all_desc") != -1:
        continue
    t = t.replace(marker, '%s"unlock_all":"OWN EVERYTHING","unlock_all_desc":"%s",' % (marker, text), 1)
    added += 1

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("languages patched:", added)
