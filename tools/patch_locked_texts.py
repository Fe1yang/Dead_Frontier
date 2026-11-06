# -*- coding: utf-8 -*-
## Insert char_locked/skin_locked toasts (extra_text.gd) and store section labels
## (store_catalog.gd) for all 20 languages. Pure str.replace, one hit per language, asserted.
import io, sys

def patch(path, pairs):
    with io.open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    for old, new in pairs:
        n = text.count(old)
        assert n == 1, '%s: anchor occurs %d times: %r' % (path, n, old[:60])
        text = text.replace(old, new)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    print('PATCHED', path, len(pairs), 'anchors')

# --- extra_text.gd: pet_locked -> pet_locked + char_locked + skin_locked ---
extra = [
    ('"pet_locked":"Win it from a case to own it","mail"', '"pet_locked":"Win it from a case to own it","char_locked":"Unlock in the store","skin_locked":"Unlock this outfit in the store","mail"'),
    ('"pet_locked":"开箱子获得后永久解锁","mail"', '"pet_locked":"开箱子获得后永久解锁","char_locked":"前往商城解锁该角色","skin_locked":"前往商城解锁该皮肤","mail"'),
    ('"pet_locked":"開箱子獲得後永久解鎖","mail"', '"pet_locked":"開箱子獲得後永久解鎖","char_locked":"前往商城解鎖該角色","skin_locked":"前往商城解鎖該造型","mail"'),
    ('"pet_locked":"ケースで手に入れると永久解放","mail"', '"pet_locked":"ケースで手に入れると永久解放","char_locked":"ストアで解放できます","skin_locked":"ストアでスキンを解放できます","mail"'),
    ('"pet_locked":"상자에서 얻으면 영구 해금","mail"', '"pet_locked":"상자에서 얻으면 영구 해금","char_locked":"상점에서 해금하세요","skin_locked":"상점에서 스킨을 해금하세요","mail"'),
    ('"pet_locked":"Gánalo en una caja para tenerlo","mail"', '"pet_locked":"Gánalo en una caja para tenerlo","char_locked":"Desbloquéalo en la tienda","skin_locked":"Desbloquea el aspecto en la tienda","mail"'),
    ('"pet_locked":"Gagne-le dans une caisse pour l\'avoir","mail"', '"pet_locked":"Gagne-le dans une caisse pour l\'avoir","char_locked":"Débloque-le dans la boutique","skin_locked":"Débloque cette tenue dans la boutique","mail"'),
    ('"pet_locked":"Aus einer Kiste gewinnen, um ihn zu besitzen","mail"', '"pet_locked":"Aus einer Kiste gewinnen, um ihn zu besitzen","char_locked":"Im Shop freischalten","skin_locked":"Skin im Shop freischalten","mail"'),
    ('"pet_locked":"Ganhe numa caixa para tê-lo","mail"', '"pet_locked":"Ganhe numa caixa para tê-lo","char_locked":"Desbloqueie na loja","skin_locked":"Desbloqueie o visual na loja","mail"'),
    ('"pet_locked":"Выиграйте в ящике, чтобы получить навсегда","mail"', '"pet_locked":"Выиграйте в ящике, чтобы получить навсегда","char_locked":"Откройте в магазине","skin_locked":"Откройте скин в магазине","mail"'),
    ('"pet_locked":"اربحه من صندوق لتمتلكه","mail"', '"pet_locked":"اربحه من صندوق لتمتلكه","char_locked":"افتحه في المتجر","skin_locked":"افتح المظهر في المتجر","mail"'),
    ('"pet_locked":"बक्से से जीतें और हमेशा के लिए पाएँ","mail"', '"pet_locked":"बक्से से जीतें और हमेशा के लिए पाएँ","char_locked":"स्टोर में अनलॉक करें","skin_locked":"स्किन स्टोर में अनलॉक करें","mail"'),
    ('"pet_locked":"Dapatkan dari peti untuk memilikinya","mail"', '"pet_locked":"Dapatkan dari peti untuk memilikinya","char_locked":"Buka di toko","skin_locked":"Buka skin di toko","mail"'),
    ('"pet_locked":"Vincilo in una cassa per averlo","mail"', '"pet_locked":"Vincilo in una cassa per averlo","char_locked":"Sblocca nel negozio","skin_locked":"Sblocca il costume nel negozio","mail"'),
    ('"pet_locked":"Sandıktan kazanınca kalıcı açılır","mail"', '"pet_locked":"Sandıktan kazanınca kalıcı açılır","char_locked":"Mağazadan aç","skin_locked":"Kostümü mağazadan aç","mail"'),
    ('"pet_locked":"Win hem uit een kist om hem te houden","mail"', '"pet_locked":"Win hem uit een kist om hem te houden","char_locked":"Ontgrendel in de winkel","skin_locked":"Ontgrendel de skin in de winkel","mail"'),
    ('"pet_locked":"Wygraj go ze skrzyni, by go mieć","mail"', '"pet_locked":"Wygraj go ze skrzyni, by go mieć","char_locked":"Odblokuj w sklepie","skin_locked":"Odblokuj skórkę w sklepie","mail"'),
    ('"pet_locked":"เปิดกล่องได้มาแล้วปลดล็อกถาวร","mail"', '"pet_locked":"เปิดกล่องได้มาแล้วปลดล็อกถาวร","char_locked":"ปลดล็อกในร้านค้า","skin_locked":"ปลดล็อกสกินในร้านค้า","mail"'),
    ('"pet_locked":"Mở rương nhận được để sở hữu vĩnh viễn","mail"', '"pet_locked":"Mở rương nhận được để sở hữu vĩnh viễn","char_locked":"Mở khóa trong cửa hàng","skin_locked":"Mở khóa trang phục trong cửa hàng","mail"'),
    ('"pet_locked":"Виграйте в ящику, щоб отримати назавжди","mail"', '"pet_locked":"Виграйте в ящику, щоб отримати назавжди","char_locked":"Відкрийте в крамниці","skin_locked":"Відкрийте скін у крамниці","mail"'),
]
patch('scripts/extra_text.gd', extra)

# --- store_catalog.gd: section labels "characters"/"skins" right after "buy" ---
store = [
    ('"buy":"Buy","store"', '"buy":"Buy","characters":"Survivors","skins":"Skins","store"'),
    ('"buy":"购买","store"', '"buy":"购买","characters":"角色","skins":"皮肤","store"'),
    ('"buy":"購買","store"', '"buy":"購買","characters":"角色","skins":"造型","store"'),
    ('"buy":"購入","store"', '"buy":"購入","characters":"キャラクター","skins":"スキン","store"'),
    ('"buy":"구매","store"', '"buy":"구매","characters":"캐릭터","skins":"스킨","store"'),
    ('"buy":"Comprar","store":"Tienda"', '"buy":"Comprar","characters":"Personajes","skins":"Aspectos","store":"Tienda"'),
    ('"buy":"Acheter","store"', '"buy":"Acheter","characters":"Personnages","skins":"Skins","store"'),
    ('"buy":"Kaufen","store"', '"buy":"Kaufen","characters":"Charaktere","skins":"Skins","store"'),
    ('"buy":"Comprar","store":"Loja"', '"buy":"Comprar","characters":"Personagens","skins":"Visuais","store":"Loja"'),
    ('"buy":"Купить","store"', '"buy":"Купить","characters":"Персонажи","skins":"Скины","store"'),
    ('"buy":"شراء","store"', '"buy":"شراء","characters":"الشخصيات","skins":"المظاهر","store"'),
    ('"buy":"खरीदें","store"', '"buy":"खरीदें","characters":"चरित्र","skins":"स्किन","store"'),
    ('"buy":"Beli","store"', '"buy":"Beli","characters":"Karakter","skins":"Skin","store"'),
    ('"buy":"Compra","store"', '"buy":"Compra","characters":"Personaggi","skins":"Costumi","store"'),
    ('"buy":"Satın al","store"', '"buy":"Satın al","characters":"Karakterler","skins":"Kostümler","store"'),
    ('"buy":"Kopen","store"', '"buy":"Kopen","characters":"Personages","skins":"Skins","store"'),
    ('"buy":"Kup","store"', '"buy":"Kup","characters":"Postacie","skins":"Skiny","store"'),
    ('"buy":"ซื้อ","store"', '"buy":"ซื้อ","characters":"ตัวละคร","skins":"สกิน","store"'),
    ('"buy":"Mua","store"', '"buy":"Mua","characters":"Nhân vật","skins":"Trang phục","store"'),
    ('"buy":"Купити","store"', '"buy":"Купити","characters":"Персонажі","skins":"Скіни","store"'),
]
patch('scripts/store_catalog.gd', store)
print('ALL_DONE')
