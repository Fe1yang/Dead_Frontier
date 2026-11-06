#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the embedded baseColor texture from pursuer_abomination.glb and compare its
brightness with the original 11-04 Color jpg on disk."""
import json, struct, io
from PIL import Image, ImageStat

PATH = r"assets\models\actors\pursuer_abomination.glb"
ORIG = r"assets\models\actors\pursuer_abomination_Color_b293d99e-e8a4-4a09-a567-10a05ccf4119.jpg"

data = open(PATH, "rb").read()
clen, _ = struct.unpack_from("<I4s", data, 12)
gltf = json.loads(data[20:20 + clen].decode("utf-8"))
off = 12 + 8 + clen
blen, btype = struct.unpack_from("<I4s", data, off)
binchunk = data[off + 8: off + 8 + blen]

mat = gltf["materials"][0]
tex_i = mat["pbrMetallicRoughness"]["baseColorTexture"]["index"]
img_i = gltf["textures"][tex_i]["source"]
img = gltf["images"][img_i]
bv = gltf["bufferViews"][img["bufferView"]]
raw = binchunk[bv.get("byteOffset", 0): bv.get("byteOffset", 0) + bv["byteLength"]]
print("embedded image:", img.get("mimeType"), len(raw), "bytes")
open(r"diagnostics\pursuer_embedded_color.bin", "wb").write(raw)

emb = Image.open(io.BytesIO(raw)).convert("RGB")
orig = Image.open(ORIG).convert("RGB").resize(emb.size)
emb.save(r"diagnostics\pursuer_embedded_color.png")
se = ImageStat.Stat(emb); so = ImageStat.Stat(orig)
print("embedded mean rgb:", [round(v, 1) for v in se.mean])
print("original mean rgb:", [round(v, 1) for v in so.mean])
ratio = [e / o if o else 0 for e, o in zip(se.mean, so.mean)]
print("embedded/original ratio:", [round(r, 3) for r in ratio])
