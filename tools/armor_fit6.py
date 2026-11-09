import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

t = t.replace("\t\tarmor_model.rotation.y = PI          # the GLB faces backwards",
              "\t\tarmor_model.rotation.y = 0.0          # the GLB already faces +Z like the body", 1)
t = t.replace("\t\tholder.position = Vector3(0.0, 1.16, 0.0)",
              "\t\tholder.position = Vector3(0.0, 1.18, 0.0)", 1)
t = t.replace("\t\t\t\tvar sc: float = 0.46 / widest",
              "\t\t\t\tvar sc: float = 0.44 / widest", 1)

# helmet: smaller shell that sits on the crown instead of swallowing the face
t = t.replace("\t\tvar hs: float = 0.34 / maxf(widest, 0.001)",
              "\t\tvar hs: float = 0.27 / maxf(widest, 0.001)", 1)
t = t.replace("helmet_model.position = -box.get_center() * hs + Vector3(0.0, 0.02, 0.0)",
              "helmet_model.position = -box.get_center() * hs + Vector3(0.0, 0.055, 0.0)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("vest faces forward again; helmet scaled to 0.27 m and lifted")
