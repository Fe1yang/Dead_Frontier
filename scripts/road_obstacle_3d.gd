extends Node3D

var kind:="car"
var half_extents:=Vector2(1.02,2.08)
var damage:=22.0
var hit_cooldown:=0.0
var model: Node3D
var paint:=Color("71332f")
var rust_material: StandardMaterial3D
var dark_material: StandardMaterial3D
var metal_material: StandardMaterial3D
var rubber_material: StandardMaterial3D
var glass_material: StandardMaterial3D
var random:=RandomNumberGenerator.new()

func _ready() -> void:
	random.randomize()
	_make_materials()
	model=Node3D.new()
	add_child(model)
	if kind=="fence":
		half_extents=Vector2(1.15,0.34)
		damage=12.0
		_make_fence()
	else:
		half_extents=Vector2(1.02,2.08)
		damage=22.0
		paint=[Color("71332f"),Color("344b56"),Color("555b4b"),Color("6b6252")][random.randi_range(0,3)]
		_make_car()

func _make_materials() -> void:
	rust_material=_material(Color("633a28"),0.92,0.18)
	dark_material=_material(Color("171b1c"),0.72,0.38)
	metal_material=_material(Color("8b9290"),0.34,0.72)
	rubber_material=_material(Color("111313"),0.96,0.0)
	glass_material=_material(Color(0.12,0.23,0.26,0.64),0.16,0.30)
	glass_material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA

func _material(color: Color,roughness: float,metallic: float) -> StandardMaterial3D:
	var material:=StandardMaterial3D.new()
	material.albedo_color=color
	material.roughness=roughness
	material.metallic=metallic
	return material

func _rounded_box(size: Vector3,bevel: float=0.06,steps: int=4) -> ArrayMesh:
	var st:=SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var half:=size*0.5
	var inner:=Vector3(maxf(0.01,half.x-bevel),maxf(0.01,half.y-bevel),maxf(0.01,half.z-bevel))
	var faces:=[
		[Vector3(0,0,1),Vector3(1,0,0),Vector3(0,1,0)],
		[Vector3(0,0,-1),Vector3(-1,0,0),Vector3(0,1,0)],
		[Vector3(1,0,0),Vector3(0,0,-1),Vector3(0,1,0)],
		[Vector3(-1,0,0),Vector3(0,0,1),Vector3(0,1,0)],
		[Vector3(0,1,0),Vector3(1,0,0),Vector3(0,0,-1)],
		[Vector3(0,-1,0),Vector3(1,0,0),Vector3(0,0,1)]
	]
	for face in faces:
		var normal_axis: Vector3=face[0]
		var u_axis: Vector3=face[1]
		var v_axis: Vector3=face[2]
		var face_half:=Vector3(absf(normal_axis.x)*half.x,absf(normal_axis.y)*half.y,absf(normal_axis.z)*half.z)
		var u_half:=Vector3(absf(u_axis.x)*half.x,absf(u_axis.y)*half.y,absf(u_axis.z)*half.z)
		var v_half:=Vector3(absf(v_axis.x)*half.x,absf(v_axis.y)*half.y,absf(v_axis.z)*half.z)
		var first: int=faces.find(face)*(steps+1)*(steps+1)
		for y in range(steps+1):
			for x in range(steps+1):
				var point:=normal_axis*face_half+u_axis*u_half*(float(x)/steps*2.0-1.0)+v_axis*v_half*(float(y)/steps*2.0-1.0)
				var clamped:=Vector3(clampf(point.x,-inner.x,inner.x),clampf(point.y,-inner.y,inner.y),clampf(point.z,-inner.z,inner.z))
				var normal:=(point-clamped).normalized()
				st.set_normal(normal)
				st.set_uv(Vector2(float(x)/steps,float(y)/steps))
				st.add_vertex(clamped+normal*bevel)
		for y in range(steps):
			for x in range(steps):
				var a: int=first+y*(steps+1)+x
				var b: int=a+1
				var c: int=a+steps+2
				var d: int=a+steps+1
				for index in [a,b,c,a,c,d]: st.add_index(index)
	return st.commit()

func _box(parent: Node3D,size: Vector3,pos: Vector3,material: Material,bevel: float=0.05) -> MeshInstance3D:
	var node:=MeshInstance3D.new()
	node.mesh=_rounded_box(size,bevel)
	node.material_override=material
	node.position=pos
	parent.add_child(node)
	return node

func _cylinder(parent: Node3D,radius: float,height: float,pos: Vector3,material: Material,rotation_value: Vector3=Vector3.ZERO,segments: int=24) -> MeshInstance3D:
	var node:=MeshInstance3D.new()
	var mesh:=CylinderMesh.new()
	mesh.top_radius=radius
	mesh.bottom_radius=radius
	mesh.height=height
	mesh.radial_segments=segments
	mesh.rings=2
	node.mesh=mesh
	node.material_override=material
	node.position=pos
	node.rotation=rotation_value
	parent.add_child(node)
	return node

func _quad(parent: Node3D,size: Vector2,pos: Vector3,rotation_value: Vector3,material: Material) -> MeshInstance3D:
	var node:=MeshInstance3D.new()
	var mesh:=QuadMesh.new()
	mesh.size=size
	node.mesh=mesh
	node.material_override=material
	node.position=pos
	node.rotation=rotation_value
	parent.add_child(node)
	return node

func _make_car() -> void:
	var paint_material:=_material(paint,0.48,0.48)
	var faded_paint:=_material(paint.lightened(0.10),0.66,0.34)
	_box(model,Vector3(1.84,0.58,3.94),Vector3(0,0.66,0),paint_material,0.15)
	_box(model,Vector3(1.74,0.20,1.26),Vector3(0,0.98,1.20),faded_paint,0.07)
	_box(model,Vector3(1.52,0.15,1.72),Vector3(0,1.60,0.32),paint_material,0.07)
	# Exposed engine and a raised, bent hood make this a wreck rather than a clean prop.
	_box(model,Vector3(1.24,0.30,0.82),Vector3(0,0.99,-1.16),dark_material,0.04)
	for x in [-0.42,0.0,0.42]:
		_cylinder(model,0.11,0.64,Vector3(x,1.18,-1.12),metal_material,Vector3(PI/2,0,0),20)
	var hood:=_box(model,Vector3(1.68,0.12,1.12),Vector3(0,1.42,-1.13),faded_paint,0.055)
	hood.rotation.x=-0.83
	hood.rotation.z=0.055
	# Cabin frame and broken glass.
	for x in [-0.70,0.70]:
		for z in [-0.47,1.03]:
			var pillar:=_box(model,Vector3(0.11,0.72,0.12),Vector3(x,1.24,z),paint_material,0.025)
			pillar.rotation.x=0.12 if z<0 else -0.08
		_box(model,Vector3(0.09,0.11,1.55),Vector3(x,1.00,0.30),paint_material,0.025)
		_box(model,Vector3(0.035,0.045,1.44),Vector3(x*1.09,0.87,0.38),dark_material,0.01)
		var side_window:=_quad(model,Vector2(1.30,0.50),Vector3(x,1.30,0.32),Vector3(0,PI/2,0),glass_material)
		if x>0: side_window.visible=false
	var windshield:=_quad(model,Vector2(1.30,0.55),Vector3(0,1.29,-0.50),Vector3(-0.12,PI,0),glass_material)
	windshield.scale.x=0.73
	_quad(model,Vector2(1.26,0.49),Vector3(0,1.29,1.04),Vector3(0.08,0,0),glass_material)
	# Bumpers, grille, lamps and door handles.
	_box(model,Vector3(1.82,0.16,0.18),Vector3(0,0.54,-2.00),metal_material,0.04)
	_box(model,Vector3(1.82,0.15,0.16),Vector3(0,0.55,2.00),dark_material,0.035)
	_box(model,Vector3(0.70,0.25,0.06),Vector3(0,0.77,-2.00),dark_material,0.02)
	for x in [-0.26,-0.13,0.0,0.13,0.26]:
		_box(model,Vector3(0.035,0.22,0.065),Vector3(x,0.78,-2.035),metal_material,0.008)
	for x in [-0.65,0.65]:
		var lamp_material:=_material(Color("c8bb8d") if x<0 else Color("282c29"),0.24,0.25)
		_box(model,Vector3(0.36,0.19,0.08),Vector3(x,0.88,-1.99),lamp_material,0.04)
		_box(model,Vector3(0.30,0.14,0.07),Vector3(x,0.83,1.99),_material(Color("6e1917"),0.32,0.15),0.03)
	for x in [-0.945,0.945]:
		for z in [-0.10,0.73]:
			_box(model,Vector3(0.055,0.045,0.20),Vector3(x,1.01,z),metal_material,0.012)
	# Four detailed wheels; the front-right tire is damaged and flattened.
	for x in [-0.94,0.94]:
		for z in [-1.28,1.28]:
			var wheel:=MeshInstance3D.new()
			var tire:=TorusMesh.new()
			tire.inner_radius=0.21
			tire.outer_radius=0.39
			tire.rings=40
			tire.ring_segments=14
			wheel.mesh=tire
			wheel.material_override=rubber_material
			wheel.position=Vector3(x,0.43,z)
			wheel.rotation.z=PI/2
			if x>0 and z<0:
				wheel.scale=Vector3(1.0,0.72,1.0)
				wheel.position.y=0.33
				wheel.rotation.y=0.20
			model.add_child(wheel)
			_cylinder(model,0.20,0.13,Vector3(x,0.43,z),metal_material,Vector3(0,0,PI/2),32)
			_cylinder(model,0.075,0.15,Vector3(x,0.43,z),dark_material,Vector3(0,0,PI/2),24)
	# Rust blooms, dents and scattered metal around the wreck.
	for i in range(13):
		var side:float=1.0 if i%2==0 else -1.0
		var patch:=_box(model,Vector3(0.025,random.randf_range(0.07,0.18),random.randf_range(0.12,0.38)),Vector3(side*0.927,random.randf_range(0.54,0.86),random.randf_range(-1.72,1.72)),rust_material,0.008)
		patch.rotation.x=random.randf_range(-0.45,0.45)
	for i in range(5):
		var debris:=_box(model,Vector3(random.randf_range(0.12,0.30),0.035,random.randf_range(0.18,0.42)),Vector3(random.randf_range(-1.25,1.25),0.035,random.randf_range(-2.15,2.15)),rust_material,0.01)
		debris.rotation.y=random.randf_range(0,TAU)
	model.rotation.y=random.randf_range(-0.09,0.09)

func _make_fence() -> void:
	var orange:=_material(Color("c65b2c"),0.60,0.25)
	var white:=_material(Color("ddd7c5"),0.48,0.28)
	# Tubular barricade with a reflective upper board and splayed feet.
	for y in [0.30,1.10]:
		_cylinder(model,0.045,2.30,Vector3(0,y,0),metal_material,Vector3(0,0,PI/2),24)
	for x in [-1.10,1.10]:
		_cylinder(model,0.05,1.12,Vector3(x,0.61,0),metal_material,Vector3.ZERO,24)
		_cylinder(model,0.045,0.82,Vector3(x,0.09,0),dark_material,Vector3(PI/2,0,0),20)
	for i in range(9):
		_cylinder(model,0.023,0.77,Vector3(-0.88+i*0.22,0.69,0),metal_material,Vector3.ZERO,16)
	_box(model,Vector3(2.26,0.30,0.09),Vector3(0,1.04,-0.025),orange,0.025)
	for i in range(6):
		var stripe:=_box(model,Vector3(0.19,0.29,0.012),Vector3(-0.91+i*0.365,1.04,-0.078),white,0.006)
		stripe.rotation.z=-0.34
	for x in [-0.82,0.82]:
		var lamp:=_box(model,Vector3(0.16,0.12,0.10),Vector3(x,1.29,0),orange,0.035)
		lamp.material_override=_material(Color("ef7b35"),0.32,0.10)
	model.rotation.y=random.randf_range(-0.06,0.06)

func tick(delta: float) -> void:
	position.z+=3.5*delta
	hit_cooldown=maxf(0.0,hit_cooldown-delta)

func overlaps(point: Vector3,radius: float=0.40) -> bool:
	return absf(point.x-position.x)<half_extents.x+radius and absf(point.z-position.z)<half_extents.y+radius
