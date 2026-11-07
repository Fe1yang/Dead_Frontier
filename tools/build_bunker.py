"""Entry point: build assets/models/environment/safehouse_interior.glb from scratch.

    "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background \\
        --factory-startup --python tools/build_bunker.py
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import numpy as np

import cabin_prims as P
import bunker_prims
import bunker_set as S


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(4702)
    np.random.seed(4702)
    # safehouse output names (cabin_prims defaults point at the old cabin glb)
    P.OUT_GLB = os.path.join(P.ENV_DIR, "safehouse_interior.glb")
    P.OUT_BLEND = os.path.join(P.SRC_DIR, "safehouse_interior.blend")
    bunker_prims.build_materials()
    gs = S.Groups()
    S.build_all(gs)
    S.export_scene(gs)


if __name__ == "__main__":
    main()
