from PIL import Image
p = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\male_hd_portrait.png"
im = Image.open(p).convert("RGB")
w, h = im.size
print("src", w, h)
im.crop((int(w * 0.35), 0, int(w * 0.65), int(h * 0.55))).save(
    r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\ken_hd_portrait.png")
print("saved")
