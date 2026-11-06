import bpy, sys, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--')+1:]
actors = argv or ['survivor_male_universal.glb', 'survivor_riley_universal.glb']

def load_glb(path):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.context.scene.objects if o not in before]

for actor_name in actors:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    new = load_glb(ROOT/'assets'/'models'/'actors'/actor_name)
    rig = next(o for o in new if o.type=='ARMATURE')
    mesh = next(o for o in new if o.type=='MESH')
    # Freeze the rig in rest pose and drop animations so the check is about fit only.
    if rig.animation_data: rig.animation_data.action = None

    # Helmet: BoneAttachment3D on 'Head', model offset (0,0.065,0.015), scale 1.12.
    head_bone = rig.data.bones.get('Head')
    head_world = rig.matrix_world @ head_bone.matrix_local
    helmet = load_glb(ROOT/'assets'/'models'/'helmet.glb')
    for o in helmet:
        if o.parent is None:
            o.scale = Vector((1.12,)*3)
            # BoneAttachment: bone tail space; use head bone origin plus game offset.
            o.matrix_world = head_world
            o.location += Vector((0.0, 0.065, 0.015))

    # Armor: child of model root, scale (0.72,0.78,0.64), y = 1.315*(1-0.78).
    armor = load_glb(ROOT/'assets'/'models'/'armor.glb')
    for o in armor:
        if o.parent is None:
            o.scale = Vector((0.72, 0.78, 0.64))
            o.location = Vector((0.0, 0.0, 1.315*(1.0-0.78)))

    # Frame everything.
    low = Vector((1e9,)*3); high = Vector((-1e9,)*3)
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH': continue
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            low = Vector(map(min, low, w)); high = Vector(map(max, high, w))
    center = (low+high)/2

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'TEXTURE'
    scene.render.resolution_x = 640; scene.render.resolution_y = 640
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'

    cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
    scene.collection.objects.link(cam); scene.camera = cam
    span = (high.z-low.z)
    for label, direction in (('front', Vector((0,-1,0.12))), ('side', Vector((1,0,0.12)))):
        dist = span*1.9
        cam.location = center + direction.normalized()*dist + Vector((0,0,span*0.06))
        cam.rotation_euler = (center - cam.location).to_track_quat('-Z','Y').to_euler()
        cam_data.clip_start = 0.01; cam_data.clip_end = 100
        out = ROOT/'diagnostics'/('gear-%s-%s.png' % (actor_name.replace('_universal.glb',''), label))
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        print('GEAR_RENDER', out)
    for o in armor + helmet:
        bpy.data.objects.remove(o, do_unlink=True)
