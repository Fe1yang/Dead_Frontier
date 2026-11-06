#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brighten the pursuer's skin: add a warm >1 baseColorFactor to its material.
JSON-chunk-only patch; BIN chunk (mesh/skin/animation/texture bytes) untouched."""
import json, struct, shutil

PATH = r"assets\models\actors\pursuer_abomination.glb"
shutil.copy2(PATH, PATH + ".bak")  # keep a rollback copy next to the model

data = open(PATH, "rb").read()
magic, version, total = struct.unpack_from("<4sII", data, 0)
assert magic == b"glTF"
off = 12
chunks = []
while off < len(data):
    clen, ctype = struct.unpack_from("<I4s", data, off)
    chunks.append((ctype, data[off + 8: off + 8 + clen]))
    off += 8 + clen

gltf = json.loads(chunks[0][1].decode("utf-8"))
changed = 0
for mat in gltf.get("materials", []):
    pbr = mat.setdefault("pbrMetallicRoughness", {})
    if "baseColorTexture" in pbr and "baseColorFactor" not in pbr:
        # gentle warm lift: +25% red, +18% green, +12% blue keeps the fleshy tone
        pbr["baseColorFactor"] = [1.25, 1.18, 1.12, 1.0]
        print("material %r brightened x[1.25,1.18,1.12]" % mat.get("name"))
        changed += 1
assert changed >= 1, "no textured material found"

payload = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
payload += b" " * (-len(payload) % 4)
out = [struct.pack("<I4s", len(payload), b"JSON"), payload]
for ctype, cdata in chunks[1:]:
    out.append(struct.pack("<I4s", len(cdata), ctype))
    out.append(cdata)
body = b"".join(out)
open(PATH, "wb").write(struct.pack("<4sII", b"glTF", version, 12 + len(body)) + body)
print("PATCHED %s (%d material(s))" % (PATH, changed))
