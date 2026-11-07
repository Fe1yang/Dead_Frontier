from PIL import Image
p = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\ken_hd_portrait.png"
im = Image.open(p)
im.save(r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\store\char_ken.png")
print("saved char_ken")
