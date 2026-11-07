"""Entry point: build assets/models/environment/cabin_interior.glb from scratch.

    "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background \
        --factory-startup --python tools/build_cabin.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import numpy as np

import cabin_prims as P
import cabin_set as S


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(4702)
    np.random.seed(4702)
    P.build_materials()
    gs = S.Groups()
    S.build_all(gs)
    S.export_scene(gs)


if __name__ == "__main__":
    main()
