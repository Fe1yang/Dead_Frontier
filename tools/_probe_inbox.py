
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=r"C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/assets/models/environment/safehouse_interior.glb")
LO=(0.2,2.6,0.0); HI=(1.35,3.4,1.2)
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    mw=obj.matrix_world
    n=0; zmin=9; zmax=-9; xmin=9; xmax=-9; ymin=9; ymax=-9
    for v in obj.data.vertices:
        p=mw@v.co
        if LO[0]<=p.x<=HI[0] and LO[1]<=p.y<=HI[1] and LO[2]<=p.z<=HI[2]:
            n+=1; zmin=min(zmin,p.z); zmax=max(zmax,p.z)
            xmin=min(xmin,p.x); xmax=max(xmax,p.x); ymin=min(ymin,p.y); ymax=max(ymax,p.y)
    if n>0:
        print("INBOX %s n=%d x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (obj.name,n,xmin,xmax,ymin,ymax,zmin,zmax))
