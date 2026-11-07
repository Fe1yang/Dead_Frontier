import bpy, sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
model = sys.argv[sys.argv.index('--')+1]
out = sys.argv[sys.argv.index('--')+2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets'/'models'/'actors'/model))
bpy.context.view_layer.update()
meshes=[o for o in bpy.data.objects if o.type=='MESH']
dg=bpy.context.evaluated_depsgraph_get()
lo=Vector((1e9,)*3); hi=Vector((-1e9,)*3)
for ob in meshes:
    ev=ob.evaluated_get(dg); me=ev.to_mesh()
    for v in me.vertices:
        w=ev.matrix_world@v.co; lo=Vector(map(min,lo,w)); hi=Vector(map(max,hi,w))
    ev.to_mesh_clear()
print('BOUNDS lo=',tuple(lo),'hi=',tuple(hi))
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'; scene.display.shading.color_type='TEXTURE'
scene.render.resolution_x=512; scene.render.resolution_y=512
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG'
cam_data=bpy.data.cameras.new('cam'); cam=bpy.data.objects.new('cam',cam_data)
scene.collection.objects.link(cam)
cx=(lo.x+hi.x)/2
cam.location=(cx,lo.y-8,(lo.z+hi.z)/2)
cam.rotation_euler=(Vector((cx,0,(lo.z+hi.z)/2))-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO'; cam_data.ortho_scale=(hi.z-lo.z)*1.05
scene.camera=cam
scene.render.filepath=out
bpy.ops.render.render(write_still=True)
print('FULL_RENDERED')
