from PIL import Image
p = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\ken_hd_portrait.png"
im = Image.open(p).convert("L")
im.save(r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\ken_hud_gray.png")
print("saved gray")
