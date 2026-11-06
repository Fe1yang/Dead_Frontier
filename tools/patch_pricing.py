#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pricing pass: characters $10.00 flat (new tier 7), dogs+skins $4.99 (tier 2),
adds 4 dog packs to the store and the "pets" section title in all 20 languages.
Pure str.replace with count assertions — no regex."""
import sys

PATH = "scripts/store_catalog.gd"
src = open(PATH, encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, "anchor %r found %d times, expected %d" % (old[:60], n, count)
    src = src.replace(old, new)
    print("OK  %-50s x%d" % (old[:48], n))

# 1) New price tier 7 = US$10.00 flat. TIERS is index-addressed; appending is safe.
rep("const TIERS:=[0.99,1.99,4.99,9.99,19.99,49.99,99.99]",
    "const TIERS:=[0.99,1.99,4.99,9.99,19.99,49.99,99.99,10.0]")

# 2) Eighth price in every currency (approximate local equivalent of US$10.00).
#    Anchors that share an identical tier array (USD/EUR/GBP, SAR/AED) include the code prefix.
rep('"USD":["$",false,2,".",",",[0.99,1.99,4.99,9.99,19.99,49.99,99.99]],',
    '"USD":["$",false,2,".",",",[0.99,1.99,4.99,9.99,19.99,49.99,99.99,10.0]],')
rep('"EUR":["€",true,2,",",".",[0.99,1.99,4.99,9.99,19.99,49.99,99.99]],',
    '"EUR":["€",true,2,",",".",[0.99,1.99,4.99,9.99,19.99,49.99,99.99,10.99]],')
rep('"GBP":["£",false,2,".",",",[0.99,1.99,4.99,9.99,19.99,49.99,99.99]],',
    '"GBP":["£",false,2,".",",",[0.99,1.99,4.99,9.99,19.99,49.99,99.99,10.49]],')
rep('"SAR":["ر.س",true,2,".",",",[3.99,7.99,19.99,39.99,79.99,199.99,399.99]],',
    '"SAR":["ر.س",true,2,".",",",[3.99,7.99,19.99,39.99,79.99,199.99,399.99,44.99]],')
rep('"AED":["د.إ",true,2,".",",",[3.99,7.99,19.99,39.99,79.99,199.99,399.99]],',
    '"AED":["د.إ",true,2,".",",",[3.99,7.99,19.99,39.99,79.99,199.99,399.99,44.99]],')
for arr, val in [
    ("[6,12,30,68,128,328,648]", "70"),
    ("[160,300,800,1500,3000,7800,15800]", "1550"),
    ("[1400,2900,7500,14000,29000,73000,149000]", "14500"),
    ("[30,60,150,300,590,1490,2990]", "310"),
    ("[8,15,38,78,158,388,778]", "80"),
    ("[1.48,2.98,6.98,13.98,27.98,68.98,138.98]", "14.0"),
    ("[99,199,499,999,1990,4990,9990]", "1050"),
    ("[39,79,199,399,799,1999,3999]", "419"),
    ("[4.99,9.99,24.99,49.99,99.99,249.99,499.99]", "52.99"),
    ("[39.99,79.99,199.99,399.99,799.99,1999.99,3999.99]", "449.99"),
    ("[89,179,449,899,1799,4499,8999]", "999"),
    ("[16000,32000,79000,159000,319000,799000,1599000]", "169000"),
    ("[35,69,179,349,699,1790,3590]", "369"),
    ("[25000,49000,129000,249000,499000,1290000,2490000]", "259000"),
    ("[5.90,11.90,29.90,59.90,119.90,299.90,599.90]", "64.90"),
    ("[19,39,99,199,399,999,1999]", "219"),
    ("[1.39,2.79,6.99,13.99,27.99,69.99,139.99]", "14.49"),
    ("[1.49,2.99,7.99,15.99,29.99,79.99,159.99]", "16.99"),
]:
    rep(arr + "]", arr + "," + val + "]")

# 3) Pack tiers: survivors $10.00 (tier 7), Maya's tactical outfit $4.99 (tier 2),
#    and the four dogs join the store at $4.99 each.
rep('"char":2,"perk":"perk_darius","coins":0,"vouchers":0,"tier":1',
    '"char":2,"perk":"perk_darius","coins":0,"vouchers":0,"tier":7')
rep('"char":3,"perk":"perk_maya","coins":0,"vouchers":0,"tier":1',
    '"char":3,"perk":"perk_maya","coins":0,"vouchers":0,"tier":7')
rep('\t{"id":"skin_maya_tactical","kind":"skin","name":"skin_maya_tactical","skin":1,"coins":0,"vouchers":0,"tier":0,"bonus":0,"once":true,"glow":"amber","rays":8},',
    '\t{"id":"skin_maya_tactical","kind":"skin","name":"skin_maya_tactical","skin":1,"coins":0,"vouchers":0,"tier":2,"bonus":0,"once":true,"glow":"amber","rays":8},\n'
    '\t{"id":"pet_0","kind":"pet","name":"pets","pet":0,"coins":0,"vouchers":0,"tier":2,"bonus":0,"once":true,"glow":"gold","rays":8},\n'
    '\t{"id":"pet_1","kind":"pet","name":"pets","pet":1,"coins":0,"vouchers":0,"tier":2,"bonus":0,"once":true,"glow":"amber","rays":8},\n'
    '\t{"id":"pet_2","kind":"pet","name":"pets","pet":2,"coins":0,"vouchers":0,"tier":2,"bonus":0,"once":true,"glow":"violet","rays":10},\n'
    '\t{"id":"pet_3","kind":"pet","name":"pets","pet":3,"coins":0,"vouchers":0,"tier":2,"bonus":0,"once":true,"glow":"red","rays":10},')

# 4) "pets" section title in all 20 languages (anchor includes the skins+store pair).
for old, new in [
    ('"skins":"Skins","store":"Store"', '"skins":"Skins","pets":"Pets","store":"Store"'),
    ('"skins":"皮肤","store":"商店"', '"skins":"皮肤","pets":"宠物","store":"商店"'),
    ('"skins":"造型","store":"商店"', '"skins":"造型","pets":"寵物","store":"商店"'),
    ('"skins":"スキン","store":"ショップ"', '"skins":"スキン","pets":"ペット","store":"ショップ"'),
    ('"skins":"스킨","store":"상점"', '"skins":"스킨","pets":"반려견","store":"상점"'),
    ('"skins":"Aspectos","store":"Tienda"', '"skins":"Aspectos","pets":"Mascotas","store":"Tienda"'),
    ('"skins":"Skins","store":"Boutique"', '"skins":"Skins","pets":"Compagnons","store":"Boutique"'),
    ('"skins":"Skins","store":"Shop"', '"skins":"Skins","pets":"Haustiere","store":"Shop"'),
    ('"skins":"Visuais","store":"Loja"', '"skins":"Visuais","pets":"Bichos","store":"Loja"'),
    ('"skins":"Скины","store":"Магазин"', '"skins":"Скины","pets":"Питомцы","store":"Магазин"'),
    ('"skins":"المظاهر","store":"المتجر"', '"skins":"المظاهر","pets":"الرفاق","store":"المتجر"'),
    ('"skins":"स्किन","store":"स्टोर"', '"skins":"स्किन","pets":"पालतू","store":"स्टोर"'),
    ('"skins":"Skin","store":"Toko"', '"skins":"Skin","pets":"Peliharaan","store":"Toko"'),
    ('"skins":"Costumi","store":"Negozio"', '"skins":"Costumi","pets":"Animali","store":"Negozio"'),
    ('"skins":"Kostümler","store":"Mağaza"', '"skins":"Kostümler","pets":"Dostlar","store":"Mağaza"'),
    ('"skins":"Skins","store":"Winkel"', '"skins":"Skins","pets":"Huisdieren","store":"Winkel"'),
    ('"skins":"Skiny","store":"Sklep"', '"skins":"Skiny","pets":"Zwierzaki","store":"Sklep"'),
    ('"skins":"สกิน","store":"ร้านค้า"', '"skins":"สกิน","pets":"สัตว์เลี้ยง","store":"ร้านค้า"'),
    ('"skins":"Trang phục","store":"Cửa hàng"', '"skins":"Trang phục","pets":"Thú cưng","store":"Cửa hàng"'),
    ('"skins":"Скіни","store":"Крамниця"', '"skins":"Скіни","pets":"Улюбленці","store":"Крамниця"'),
]:
    rep(old, new)

open(PATH, "w", encoding="utf-8", newline="\n").write(src)
print("PATCHED store_catalog.gd: tier7=$10 flat, dogs+skin=$4.99, 4 dog packs, pets x20")
