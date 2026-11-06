import bpy
import math
import sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets'/'models'/'generated'
OUT=ROOT/'assets'/'models'/'actors'
OUT.mkdir(parents=True,exist_ok=True)
ACTORS={
    'male':('survivor_male_hd.glb','survivor_male.glb',1.92,True),
    'female':('survivor_female_hd.glb','survivor_female.glb',1.86,True),
    'walker':('zombie_walker_clean_hd.glb','zombie_walker.glb',1.90,False),
}
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(ACTORS)

def dist_segment(p,a,b):
    ab=b-a
    t=max(0.0,min(1.0,(p-a).dot(ab)/max(ab.length_squared,1e-8)))
    return (p-(a+ab*t)).length

def add_bone(arm,name,head,tail,parent=None):
    b=arm.data.edit_bones.new(name); b.head=head; b.tail=tail
    if parent: b.parent=arm.data.edit_bones[parent]

def aim_rotation(sign):
    return Vector((sign,0,-0.03)).normalized().rotation_difference(Vector((sign*0.12,-0.88,-0.32)).normalized())

def pose_survivor_mesh(mesh):
    for v in mesh.data.vertices:
        p=v.co.copy(); sign=-1 if p.x<0 else 1
        if abs(p.x)>0.25 and p.z>1.18:
            shoulder=Vector((sign*0.23,0,1.45))
            v.co=shoulder+aim_rotation(sign)@(p-shoulder)

def build_rig(mesh,is_survivor):
    arm_data=bpy.data.armatures.new('ActorRig')
    arm=bpy.data.objects.new('ActorRig',arm_data); bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm; arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    add_bone(arm,'Root',(0,0,0.05),(0,0,0.42))
    add_bone(arm,'Spine',(0,0,0.82),(0,0,1.40),'Root')
    add_bone(arm,'Neck',(0,0,1.40),(0,0,1.57),'Spine')
    add_bone(arm,'Head',(0,0,1.57),(0,0,1.86),'Neck')
    for side,sign in [('L',-1),('R',1)]:
        if is_survivor:
            shoulder=Vector((sign*0.23,0,1.45)); rotation=aim_rotation(sign)
            elbow=shoulder+rotation@(Vector((sign*0.59,0,1.42))-shoulder)
            wrist=shoulder+rotation@(Vector((sign*0.94,0,1.40))-shoulder)
            hand=shoulder+rotation@(Vector((sign*1.12,0,1.39))-shoulder)
        else:
            shoulder=(sign*0.25,0,1.44); elbow=(sign*0.34,-0.02,1.13); wrist=(sign*0.38,-0.08,0.86); hand=(sign*0.39,-0.10,0.73)
        add_bone(arm,'UpperArm.'+side,shoulder,elbow,'Spine')
        add_bone(arm,'Forearm.'+side,elbow,wrist,'UpperArm.'+side)
        add_bone(arm,'Hand.'+side,wrist,hand,'Forearm.'+side)
        hip=(sign*0.14,0,0.94); knee=(sign*0.15,0,0.52); ankle=(sign*0.15,0,0.12); toe=(sign*0.15,-0.20,0.07)
        add_bone(arm,'UpperLeg.'+side,hip,knee,'Root')
        add_bone(arm,'LowerLeg.'+side,knee,ankle,'UpperLeg.'+side)
        add_bone(arm,'Foot.'+side,ankle,toe,'LowerLeg.'+side)
    bpy.ops.object.mode_set(mode='OBJECT'); arm.select_set(False)
    segments={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in arm.data.bones}
    groups={name:mesh.vertex_groups.new(name=name) for name in segments}
    for v in mesh.data.vertices:
        p=v.co.copy(); ax=abs(p.x)
        if p.z>1.55 and p.y>-0.18:
            candidates=['Head','Neck']
        elif is_survivor and ((ax>0.25 and p.z>1.18) or (p.y<-0.18 and p.z>0.95)):
            side='L' if p.x<0 else 'R'; candidates=['UpperArm.'+side,'Forearm.'+side,'Hand.'+side]
        elif not is_survivor and ax>0.27 and 0.70<p.z<1.49:
            side='L' if p.x<0 else 'R'; candidates=['UpperArm.'+side,'Forearm.'+side,'Hand.'+side]
        elif p.z<0.96:
            side='L' if p.x<0 else 'R'; candidates=['UpperLeg.'+side,'LowerLeg.'+side,'Foot.'+side]
        else:
            candidates=['Spine','Root']
        distances=sorted((dist_segment(p,*segments[name]),name) for name in candidates)
        if len(distances)==1 or distances[0][0]<0.015:
            groups[distances[0][1]].add([v.index],1.0,'REPLACE')
        else:
            w1=math.exp(-distances[0][0]*16); w2=math.exp(-distances[1][0]*16)*0.55
            total=w1+w2
            groups[distances[0][1]].add([v.index],w1/total,'REPLACE')
            groups[distances[1][1]].add([v.index],w2/total,'REPLACE')
    mod=mesh.modifiers.new('Armature','ARMATURE'); mod.object=arm
    mesh.parent=arm
    return arm

def mat(name,color,metal=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=0.48; p.inputs['Metallic'].default_value=metal
    return m

def add_gun(mesh):
    dark=mat('Gun blued steel',(0.035,0.045,0.05),0.7)
    edge=mat('Gun worn edges',(0.19,0.22,0.22),0.6)
    parts=[]
    def box(name,loc,dims,material):
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
        o=bpy.context.object; o.name=name; o.dimensions=dims
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(material)
        b=o.modifiers.new('Bevel','BEVEL'); b.width=0.018; b.segments=2
        bpy.ops.object.modifier_apply(modifier=b.name); parts.append(o)
    box('RifleReceiver',(1.17,0,1.43),(0.46,0.14,0.18),dark)
    box('RifleStock',(0.88,0,1.43),(0.26,0.16,0.20),dark)
    box('RifleHandguard',(1.52,0,1.44),(0.30,0.13,0.14),edge)
    box('RifleMagazine',(1.17,0,1.28),(0.14,0.12,0.25),dark)
    box('RifleSight',(1.19,0,1.56),(0.16,0.08,0.08),edge)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.038,depth=0.34,location=(1.78,0,1.44),rotation=(0,math.pi/2,0))
    barrel=bpy.context.object; barrel.name='RifleBarrel'; barrel.data.materials.append(edge); parts.append(barrel)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
    gun=bpy.context.object
    gun.vertex_groups.new(name='Hand.R').add(list(range(len(gun.data.vertices))),1.0,'REPLACE')
    bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); gun.select_set(True); bpy.context.view_layer.objects.active=mesh
    bpy.ops.object.join()

def point_bone(arm,name,target):
    pb=arm.pose.bones[name]; rest=arm.data.bones[name]
    head=rest.head_local; direction=(rest.tail_local-rest.head_local).normalized()
    rotation=direction.rotation_difference(Vector(target).normalized())
    matrix=Matrix.Translation(head)@rotation.to_matrix().to_4x4()@Matrix.Translation(-head)@rest.matrix_local
    pb.matrix=matrix
    bpy.context.view_layer.update()

def animate(arm,is_survivor):
    arm.animation_data_create()
    for pb in arm.pose.bones: pb.rotation_mode='XYZ'
    scene=bpy.context.scene; scene.frame_start=1; scene.frame_end=33; scene.render.fps=30
    for frame in (1,9,17,25,33):
        scene.frame_set(frame)
        phase=(frame-1)/32*math.tau
        for side,offset in [('L',0),('R',math.pi)]:
            sign=-1 if side=='L' else 1
            swing=math.sin(phase+offset)
            arm.pose.bones['UpperLeg.'+side].rotation_euler.x=swing*0.42
            arm.pose.bones['LowerLeg.'+side].rotation_euler.x=max(0,-swing)*0.45
            arm.pose.bones['Foot.'+side].rotation_euler.x=-swing*0.16
            if not is_survivor:
                arm.pose.bones['UpperArm.'+side].rotation_euler.x=-swing*0.20
                arm.pose.bones['Forearm.'+side].rotation_euler.x=-0.18
        for pb in arm.pose.bones:
            pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name)
    action=arm.animation_data.action; action.name='Walk'
    scene.frame_set(1)

for key in selected:
    source,filename,height,is_survivor=ACTORS[key]
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(SRC/source))
    meshes=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1: bpy.ops.object.join()
    mesh=bpy.context.object; mesh.name=key+'_HD_Game'
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    coords=[mesh.matrix_world@Vector(c) for c in mesh.bound_box]
    mins=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    maxs=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    scale=height/(maxs.z-mins.z); mesh.scale=(scale,)*3; mesh.rotation_mode='XYZ'; mesh.rotation_euler[2]=-math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    coords=[mesh.matrix_world@Vector(c) for c in mesh.bound_box]
    mins=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    maxs=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    mesh.location+=Vector((-(mins.x+maxs.x)/2,-(mins.y+maxs.y)/2,-mins.z))
    bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
    dec=mesh.modifiers.new('Mobile detail LOD','DECIMATE'); dec.ratio=0.32
    bpy.ops.object.modifier_apply(modifier=dec.name)
    for polygon in mesh.data.polygons: polygon.use_smooth=True
    if is_survivor: pose_survivor_mesh(mesh)
    arm=build_rig(mesh,is_survivor)
    # Weapons use a separate stable mount in Godot, not an unverified hand weight.
    animate(arm,is_survivor)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(OUT/filename),export_format='GLB',export_animations=True,export_frame_range=True,export_force_sampling=True,export_apply=False)
    print('RIGGED_ACTOR_EXPORTED',key,len(mesh.data.vertices),'vertices',OUT/filename)
