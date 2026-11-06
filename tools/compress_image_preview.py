from pathlib import Path
from PIL import Image
import sys

source=Path(sys.argv[1])
target=Path(sys.argv[2])
image=Image.open(source).convert('RGB')
image.thumbnail((1088,1920),Image.Resampling.LANCZOS)
target.parent.mkdir(parents=True,exist_ok=True)
image.save(target,quality=86,optimize=True)
print(target,target.stat().st_size)
