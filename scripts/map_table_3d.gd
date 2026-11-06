extends Node3D
## The war-room map table, fully modeled: a plank table, an aged paper map (procedural
## parchment, roads, fold creases), polaroid photos pinned along a red-string route, a
## kerosene lantern, a knife and a coffee mug. The table is wider than a portrait screen:
## the camera fills the frame and a horizontal swipe pans across the table. Only the city
## photo is a real destination; every other photo answers "coming soon".

const CAMERA_FOV := 48.0
const PAN_MIN := -2.6
const PAN_MAX := 2.6
const MAP_W := 6.0
const MAP_H := 2.3

var lantern_light: OmniLight3D
var city_frame_mat: StandardMaterial3D
var pan_x := -2.0   # opens on the city; swipe right for the rest of the table
var _t := 0.0
var photos: Array = []  # {id, node, open}

func _ready() -> void:
	var we:=WorldEnvironment.new(); var env:=Environment.new()
	env.background_mode=Environment.BG_COLOR; env.background_color=Color("050403")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color("4a3826"); env.ambient_light_energy=0.75
	env.tonemap_mode=Environment.TONE_MAPPER_ACES; env.tonemap_exposure=1.0
	we.environment=env; add_child(we)
	_build_table()
	_build_map()
	_build_route()
	_build_photos()
	_build_lantern()
	_build_knife()
	_build_mug()
	# Dark shell so neither the road nor the sky can leak in around the table.
	var shell:=MeshInstance3D.new(); var sb:=BoxMesh.new(); sb.size=Vector3(40,20,40)
	shell.mesh=sb
	var sm:=StandardMaterial3D.new(); sm.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.albedo_color=Color("050303"); sm.cull_mode=BaseMaterial3D.CULL_FRONT; sm.disable_fog=true
	shell.material_override=sm; shell.position=Vector3(0,4,0); add_child(shell)
	position=Vector3(600,-500,0)

## ---- building blocks -----------------------------------------------------------------------

func _mat(albedo: String,rough: float,metallic: float=0.0) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new(); m.albedo_color=Color(albedo); m.roughness=rough; m.metallic=metallic
	return m

func _box(parent: Node,size: Vector3,pos: Vector3,mat: Material,rot_y: float=0.0) -> MeshInstance3D:
	var n:=MeshInstance3D.new(); var b:=BoxMesh.new(); b.size=size; n.mesh=b
	n.position=pos; n.rotation.y=rot_y; n.material_override=mat; parent.add_child(n)
	return n

func _cylinder_between(a: Vector3,b: Vector3,radius: float,mat: Material) -> void:
	var d:=b-a; var mid:=(a+b)*0.5
	var n:=MeshInstance3D.new(); var c:=CylinderMesh.new()
	c.top_radius=radius; c.bottom_radius=radius; c.height=d.length(); n.mesh=c
	n.position=mid
	n.quaternion=Quaternion(Vector3(0,1,0),d.normalized())
	n.material_override=mat; add_child(n)

func _build_table() -> void:
	# Five planks with slight tone shifts and thin gaps, like a salvaged workbench.
	var tones:=["2a1a0e","241609","2d1d10","201307","281a0c"]
	for i in range(5):
		var z:=-1.44+0.72*i
		_box(self,Vector3(7.0,0.14,0.68),Vector3(0,-0.075,z),_mat(tones[i],0.93))

func _build_map() -> void:
	var map:=MeshInstance3D.new(); var pm:=PlaneMesh.new(); pm.size=Vector2(MAP_W,MAP_H)
	map.mesh=pm; map.position=Vector3(0,0.004,-0.1)
	var mm:=StandardMaterial3D.new(); mm.albedo_texture=_parchment_texture()
	mm.roughness=0.88; mm.texture_filter=BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	map.material_override=mm; add_child(map)
	# Faint typed place names scattered across the paper.
	for spot in [["GREENVALE",-1.7,-0.72],["PINEWOOD",1.05,-0.85],["RIVERSIDE",0.0,-0.2],["MILLERTON",-1.05,0.42],["ASHFORD",2.3,0.5],["BLACKWOOD",2.65,-0.75],["FORT DIXON",-2.4,0.3]]:
		var lab:=Label3D.new(); lab.text=spot[0]; lab.pixel_size=0.0016
		lab.modulate=Color(0.29,0.23,0.15,0.55); lab.outline_size=0
		lab.rotation_degrees=Vector3(-90,0,0); lab.position=Vector3(spot[1],0.009,-0.1+spot[2])
		add_child(lab)
	# A small compass "N" in the corner of the paper.
	var north:=Label3D.new(); north.text="N"; north.pixel_size=0.0028
	north.modulate=Color(0.29,0.23,0.15,0.7); north.outline_size=0
	north.rotation_degrees=Vector3(-90,0,0); north.position=Vector3(2.45,0.009,0.78)
	add_child(north)

func _parchment_texture() -> ImageTexture:
	var W:=512; var H:=224
	var img:=Image.create(W,H,false,Image.FORMAT_RGB8)
	var noise:=FastNoiseLite.new(); noise.seed=93; noise.frequency=1.0
	var grain:=FastNoiseLite.new(); grain.seed=41; grain.frequency=1.0
	# A few old stains.
	var stains:=[[0.22,0.30,0.10],[0.66,0.62,0.13],[0.82,0.22,0.07],[0.45,0.80,0.09],[0.10,0.72,0.06],[0.92,0.55,0.08]]
	for y in range(H):
		for x in range(W):
			var u:=float(x)/W; var v:=float(y)/H
			var blotch: float=noise.get_noise_2d(x*0.016,y*0.016)*0.5+0.5
			var g: float=grain.get_noise_2d(x*0.11,y*0.11)*0.5+0.5
			var c:=Color("c6b184").lerp(Color("8d7954"),blotch*0.55).lerp(Color("a08a60"),g*0.22)
			var edge:=minf(minf(u,1.0-u)*W/MAP_W,minf(v,1.0-v)*H/MAP_H)  # metres from the paper edge
			c=c.lerp(Color("6e5a3c"),clampf(1.0-edge/0.10,0.0,1.0)*0.65)
			for s in stains:
				var d: float=Vector2((u-s[0])*MAP_W,(v-s[1])*MAP_H).length()
				if d<s[2]: c=c.lerp(Color("7d6743"),(1.0-d/s[2])*0.5)
			for fx in [0.25,0.5,0.75]:
				var fd: float=absf(u-fx)*MAP_W
				if fd<0.012: c=c.darkened(0.22)
				elif fd<0.024: c=c.lightened(0.10)
			var hd: float=absf(v-0.52)*MAP_H
			if hd<0.014: c=c.darkened(0.20)
			img.set_pixel(x,y,c)
	# Meandering sepia roads.
	_road(img,[[0.05,0.62],[0.2,0.5],[0.36,0.56],[0.5,0.42],[0.66,0.47],[0.83,0.36],[0.97,0.4]],Color("6f5a3d"),1)
	_road(img,[[0.12,0.12],[0.25,0.24],[0.42,0.2],[0.55,0.3],[0.72,0.24],[0.9,0.3]],Color("6f5a3d"),1)
	_road(img,[[0.3,0.95],[0.4,0.78],[0.58,0.7],[0.7,0.78],[0.85,0.68]],Color("6f5a3d"),1)
	_road(img,[[0.06,0.30],[0.16,0.38],[0.24,0.34],[0.34,0.42]],Color("6f5a3d"),1)
	_road(img,[[0.62,0.06],[0.68,0.16],[0.8,0.14],[0.9,0.2]],Color("6f5a3d"),1)
	# A river winding down from the hills, wider and greener than the roads.
	_road(img,[[0.55,0.0],[0.6,0.14],[0.54,0.3],[0.62,0.46],[0.56,0.62],[0.64,0.8],[0.6,1.0]],Color("7d8a86"),2)
	# Contour rings around two rises.
	_contours(img,Vector2(0.80,0.78),4)
	_contours(img,Vector2(0.16,0.16),3)
	# X marks the spots.
	_xmark(img,Vector2(0.36,0.50))
	_xmark(img,Vector2(0.72,0.30))
	_xmark(img,Vector2(0.50,0.84))
	return ImageTexture.create_from_image(img)

func _contours(img: Image,center: Vector2,rings: int) -> void:
	for r in range(1,rings+1):
		var rad: int=r*9
		var col:=Color("8a744e")
		for deg in range(360):
			var a: float=deg*TAU/360.0
			var px: int=int(center.x*img.get_width()+cos(a)*rad)
			var py: int=int(center.y*img.get_height()+sin(a)*rad*0.5)
			if px>=0 and py>=0 and px<img.get_width() and py<img.get_height():
				img.set_pixel(px,py,img.get_pixel(px,py).lerp(col,0.35))

func _xmark(img: Image,center: Vector2) -> void:
	var col:=Color("7c2a1c")
	var cx: int=int(center.x*img.get_width()); var cy: int=int(center.y*img.get_height())
	for d in range(-4,5):
		for s in [[d,d],[d,-d]]:
			var px: int=cx+int(s[0]); var py: int=cy+int(s[1])
			if px>=0 and py>=0 and px<img.get_width() and py<img.get_height():
				img.set_pixel(px,py,col)

func _road(img: Image,pts: Array,col: Color,w: int) -> void:
	for i in range(pts.size()-1):
		var a:=Vector2(pts[i][0],pts[i][1]); var b:=Vector2(pts[i+1][0],pts[i+1][1])
		var steps:=int(a.distance_to(b)*300.0)
		for s in range(steps+1):
			var p: Vector2=a.lerp(b,float(s)/steps)
			var px: int=int(p.x*img.get_width()); var py: int=int(p.y*img.get_height())
			for dx in range(-w,w+1):
				for dy in range(-w,w+1):
					var xx:=px+dx; var yy:=py+dy
					if xx>=0 and yy>=0 and xx<img.get_width() and yy<img.get_height():
						img.set_pixel(xx,yy,img.get_pixel(xx,yy).lerp(col,0.55))

func _build_route() -> void:
	# Red string pinned from the city across the map toward the locked districts.
	var pts:=[Vector2(-2.0,-0.3),Vector2(-0.75,0.25),Vector2(0.45,-0.35),Vector2(1.5,0.2),Vector2(2.5,-0.3)]
	var string_mat:=_mat("7c1f16",0.7)
	var pin_mat:=_mat("3a3a3d",0.35,0.85)
	for i in range(pts.size()-1):
		var a:=Vector3(pts[i].x,0.007,-0.1+pts[i].y)
		var b:=Vector3(pts[i+1].x,0.007,-0.1+pts[i+1].y)
		# A slight sag: two segments per span with the middle dropped a hair.
		var mid:=(a+b)*0.5+Vector3(0,-0.0015,0)
		_cylinder_between(a,mid,0.004,string_mat)
		_cylinder_between(mid,b,0.004,string_mat)
	for p in pts:
		var pin:=MeshInstance3D.new(); var s:=SphereMesh.new(); s.radius=0.016; s.height=0.032
		pin.mesh=s; pin.position=Vector3(p.x,0.014,-0.1+p.y); pin.material_override=pin_mat
		add_child(pin)

## ---- photos --------------------------------------------------------------------------------

func _build_photos() -> void:
	# id, x, z (table space; the map's centre is z=-0.1), rotation, open
	var defs:=[
		["city",-2.15,-0.85,0.10,true],
		["farm",-0.6,0.6,-0.08,false],
		["coast",0.55,-0.8,0.10,false],
		["winter",1.6,0.55,-0.12,false],
		["graveyard",2.6,-0.7,0.08,false],
	]
	for d in defs:
		_photo(d[0],d[1],d[2],d[3],d[4])
	# The open destination gets a soft pulsing brass frame so players know photos are tappable.
	var city: Dictionary=photos[0]
	city_frame_mat=StandardMaterial3D.new(); city_frame_mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	city_frame_mat.albedo_color=Color(1.0,0.72,0.25,0.55); city_frame_mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	var frame:=Node3D.new(); frame.position=city.node.position+Vector3(0,0.008,0)
	var hw:=0.21; var hh:=0.25
	for seg in [[Vector3(0,0,-hh),Vector3(hw*2,0.008,0.02)],[Vector3(0,0,hh),Vector3(hw*2,0.008,0.02)],[Vector3(-hw,0,0),Vector3(0.02,0.008,hh*2)],[Vector3(hw,0,0),Vector3(0.02,0.008,hh*2)]]:
		_box(frame,seg[1],seg[0],city_frame_mat)
	add_child(frame)

func _photo(id: String,x: float,z: float,rot: float,open: bool) -> void:
	var card:=Node3D.new(); card.position=Vector3(x,0.008,z); card.rotation.y=rot
	add_child(card)
	_box(card,Vector3(0.36,0.008,0.44),Vector3(0,0,0),_mat("d8d0bc",0.82))   # polaroid border
	var pic:=MeshInstance3D.new(); var pq:=PlaneMesh.new(); pq.size=Vector2(0.30,0.30)
	pic.mesh=pq; pic.position=Vector3(0,0.006,-0.04)
	var pm:=StandardMaterial3D.new(); pm.albedo_texture=_photo_texture(id,open); pm.roughness=0.55
	pic.material_override=pm; card.add_child(pic)
	# Caption on the bottom band, like marker on the white border; small enough to stay inside it.
	var cap:=Label3D.new(); cap.text="THE BLOCKS" if open else id.to_upper()
	cap.pixel_size=0.0022; cap.modulate=Color(0.16,0.13,0.10,0.9); cap.outline_size=0
	cap.rotation_degrees=Vector3(-90,0,0); cap.position=Vector3(0,0.007,0.155)
	card.add_child(cap)
	# The pin holding it down.
	var pin:=MeshInstance3D.new(); var ps:=SphereMesh.new(); ps.radius=0.016; ps.height=0.032
	pin.mesh=ps; pin.position=Vector3(0,0.016,-0.19)
	pin.material_override=_mat("8e2a1e" if open else "3a3a3d",0.4,0.6); card.add_child(pin)
	if not open:
		# A small padlock: shackle ring plus the body.
		var body:=MeshInstance3D.new(); var bb:=BoxMesh.new(); bb.size=Vector3(0.062,0.012,0.07)
		body.mesh=bb; body.position=Vector3(0,0.012,-0.01); body.material_override=_mat("9aa0a4",0.35,0.9)
		card.add_child(body)
		var shackle:=MeshInstance3D.new(); var tm:=TorusMesh.new(); tm.inner_radius=0.02; tm.outer_radius=0.034
		shackle.mesh=tm; shackle.position=Vector3(0,0.014,-0.052)
		shackle.material_override=_mat("8a9094",0.3,0.9); card.add_child(shackle)
	photos.append({"id":id,"node":card,"open":open})

func _photo_texture(id: String,open: bool) -> ImageTexture:
	# A tiny murky snapshot per district: gradient sky plus a dark silhouette skyline.
	var W:=72; var H:=72
	var img:=Image.create(W,H,false,Image.FORMAT_RGB8)
	var pal:={
		"city":["5d6b78","1c232b"], "farm":["4d4433","1a150c"], "coast":["5c6a70","222a2e"],
		"winter":["7d8a99","2a3038"], "graveyard":["4a4c48","191a17"],
	}
	var p: Array=pal.get(id,pal["farm"])
	for y in range(H):
		var c:=Color(p[0]).lerp(Color(p[1]),float(y)/H)
		for x in range(W): img.set_pixel(x,y,c)
	var rng:=RandomNumberGenerator.new(); rng.seed=hash(id)
	match id:
		"city":
			for i in range(9):
				var bw:=rng.randi_range(6,12); var bh:=rng.randi_range(18,44); var bx:=i*8
				img.fill_rect(Rect2i(bx,H-bh,bw,bh),Color("232c34"))
				for wy in range(3):   # a few windows still lit
					if rng.randf()<0.6:
						img.fill_rect(Rect2i(bx+rng.randi_range(1,maxi(1,bw-3)),H-rng.randi_range(6,bh-2),2,2),Color("c9a45c"))
			img.fill_rect(Rect2i(0,H-6,W,6),Color("11161b"))
		"farm":
			img.fill_rect(Rect2i(14,H-30,26,22),Color("0d0a07"))
			img.fill_rect(Rect2i(12,H-34,30,5),Color("080604"))
			img.fill_rect(Rect2i(48,H-38,8,30),Color("0b0906"))
		"coast":
			img.fill_rect(Rect2i(0,H-24,W,24),Color("2b3a40"))   # the sea along the bottom
			img.fill_rect(Rect2i(0,H-26,W,2),Color("151d21"))
			for i in range(4):   # pier posts wading into the water
				var bx:=8+i*16
				img.fill_rect(Rect2i(bx,H-40,4,18),Color("0d1113"))
			img.fill_rect(Rect2i(6,H-42,60,4),Color("0d1113"))
		"winter":
			img.fill_rect(Rect2i(0,H-14,W,14),Color("6e7680"))   # snow field
			for i in range(6):   # dark pines against the white
				var bx:=5+i*12; var bh:=rng.randi_range(20,34)
				for k in range(bh):
					var wdt:=int(6.0*(1.0-float(k)/bh))+1
					img.fill_rect(Rect2i(bx-wdt/2,H-14-k,wdt,1),Color("10161a"))
		"graveyard":
			for i in range(5):   # headstones
				var bx:=8+i*12
				img.fill_rect(Rect2i(bx,H-24,7,14),Color("0d0e0c"))
				img.fill_rect(Rect2i(bx+1,H-26,5,2),Color("0d0e0c"))
			img.fill_rect(Rect2i(34,H-40,3,18),Color("0a0b09"))  # a crooked cross
			img.fill_rect(Rect2i(30,H-36,11,3),Color("0a0b09"))
		_:
			img.fill_rect(Rect2i(0,H-16,W,16),Color("0b0d0f"))
			img.fill_rect(Rect2i(20,H-38,6,38),Color("080a0c"))
			img.fill_rect(Rect2i(46,H-32,6,32),Color("080a0c"))
	if not open:
		for y in range(H):   # locked districts sit deeper in the dark
			for x in range(W): img.set_pixel(x,y,img.get_pixel(x,y).darkened(0.15))
	return ImageTexture.create_from_image(img)

## ---- props -----------------------------------------------------------------------------------

func _build_lantern() -> void:
	var root:=Node3D.new(); root.position=Vector3(-2.78,0.004,-0.72); add_child(root)
	var metal:=_mat("3d3226",0.5,0.75)
	var base:=MeshInstance3D.new(); var bc:=CylinderMesh.new(); bc.top_radius=0.15; bc.bottom_radius=0.17; bc.height=0.05
	base.mesh=bc; base.position=Vector3(0,0.025,0); base.material_override=metal; root.add_child(base)
	var tank:=MeshInstance3D.new(); var ts:=SphereMesh.new(); ts.radius=0.13; ts.height=0.2
	tank.mesh=ts; tank.position=Vector3(0,0.10,0); tank.scale=Vector3(1,0.72,1); tank.material_override=metal; root.add_child(tank)
	var glass:=MeshInstance3D.new(); var gc:=CylinderMesh.new(); gc.top_radius=0.085; gc.bottom_radius=0.10; gc.height=0.16
	glass.mesh=gc; glass.position=Vector3(0,0.22,0)
	var gm:=StandardMaterial3D.new(); gm.albedo_color=Color(1.0,0.8,0.5,0.22); gm.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	gm.roughness=0.1; gm.shading_mode=BaseMaterial3D.SHADING_MODE_PER_PIXEL
	glass.material_override=gm; root.add_child(glass)
	var flame:=MeshInstance3D.new(); var fs:=SphereMesh.new(); fs.radius=0.028; fs.height=0.056
	flame.mesh=fs; flame.position=Vector3(0,0.19,0)
	var fm:=StandardMaterial3D.new(); fm.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	fm.albedo_color=Color("ffd98a"); fm.emission_enabled=true; fm.emission=Color("ffb45c"); fm.emission_energy_multiplier=3.0
	flame.material_override=fm; root.add_child(flame)
	var cap:=MeshInstance3D.new(); var cc:=CylinderMesh.new(); cc.top_radius=0.05; cc.bottom_radius=0.11; cc.height=0.09
	cap.mesh=cc; cap.position=Vector3(0,0.345,0); cap.material_override=metal; root.add_child(cap)
	var chim:=MeshInstance3D.new(); var chc:=CylinderMesh.new(); chc.top_radius=0.028; chc.bottom_radius=0.045; chc.height=0.08
	chim.mesh=chc; chim.position=Vector3(0,0.42,0); chim.material_override=metal; root.add_child(chim)
	# Wire guards up the sides and the carry handle.
	for sx in [-1,1]:
		_cylinder_between(root.position+Vector3(0.11*sx,0.06,0),root.position+Vector3(0.07*sx,0.4,0),0.006,metal)
	var handle:=MeshInstance3D.new(); var ht:=TorusMesh.new(); ht.inner_radius=0.10; ht.outer_radius=0.115
	handle.mesh=ht; handle.position=Vector3(0,0.42,0); handle.rotation_degrees=Vector3(0,0,90)
	handle.scale=Vector3(1,1,1.35); handle.material_override=metal; root.add_child(handle)
	lantern_light=OmniLight3D.new()
	lantern_light.position=root.position+Vector3(0,0.30,0)
	lantern_light.light_color=Color("ffb45c"); lantern_light.light_energy=0.55
	lantern_light.omni_range=4.0; lantern_light.omni_attenuation=1.5; lantern_light.shadow_enabled=false
	add_child(lantern_light)

func _build_knife() -> void:
	var root:=Node3D.new(); root.position=Vector3(-3.45,0.002,0.55); root.rotation.y=0.5; add_child(root)
	var steel:=_mat("9ba1a6",0.28,0.95)
	_box(root,Vector3(0.46,0.008,0.075),Vector3(0,0,0),steel)                       # blade
	_box(root,Vector3(0.12,0.008,0.075),Vector3(0.28,0,0),steel,0.0).rotation.y=-0.5 # clipped point
	_box(root,Vector3(0.05,0.018,0.095),Vector3(-0.26,0,0),_mat("2a2018",0.8))       # guard
	_box(root,Vector3(0.22,0.024,0.06),Vector3(-0.42,0,0),_mat("1d1712",0.85))       # handle
	for rx in [-0.36,-0.46]:
		var rivet:=MeshInstance3D.new(); var rc:=CylinderMesh.new(); rc.top_radius=0.009; rc.bottom_radius=0.009; rc.height=0.028
		rivet.mesh=rc; rivet.position=Vector3(rx,0,0); rivet.material_override=steel; root.add_child(rivet)

func _build_mug() -> void:
	var root:=Node3D.new(); root.position=Vector3(3.5,0.0,-0.6); add_child(root)
	var ceramic:=_mat("2e3436",0.55)
	var cup:=MeshInstance3D.new(); var cc:=CylinderMesh.new(); cc.top_radius=0.10; cc.bottom_radius=0.085; cc.height=0.17
	cup.mesh=cc; cup.position=Vector3(0,0.085,0); cup.material_override=ceramic; root.add_child(cup)
	var coffee:=MeshInstance3D.new(); var cd:=CylinderMesh.new(); cd.top_radius=0.088; cd.bottom_radius=0.088; cd.height=0.006
	coffee.mesh=cd; coffee.position=Vector3(0,0.165,0); coffee.material_override=_mat("140c06",0.25); root.add_child(coffee)
	var ear:=MeshInstance3D.new(); var et:=TorusMesh.new(); et.inner_radius=0.045; et.outer_radius=0.062
	ear.mesh=et; ear.position=Vector3(0.11,0.09,0); ear.material_override=ceramic; root.add_child(ear)

## ---- runtime ---------------------------------------------------------------------------------

func _process(delta: float) -> void:
	_t+=delta
	# Kerosene flame: two slow wobbles plus a fast shiver.
	lantern_light.light_energy=0.55+0.10*sin(_t*7.3)+0.06*sin(_t*13.1)+0.035*sin(_t*29.0)
	if city_frame_mat:
		city_frame_mat.albedo_color.a=0.48+0.32*(0.5+0.5*sin(_t*2.4))

## A horizontal swipe pans the camera across the table (dx is screen pixels).
func pan(dx: float) -> void:
	pan_x=clampf(pan_x+dx*0.0030,PAN_MIN,PAN_MAX)

func camera_fov() -> float:
	return CAMERA_FOV

func camera_position() -> Vector3:
	# Dead overhead, the map lying square in front of the survivor; only a faint breathing sway.
	return to_global(Vector3(pan_x+0.04*sin(_t*0.31),4.6,0.05))

func camera_target() -> Vector3:
	return to_global(Vector3(pan_x,0,0.05))

## Returns the photo id under the tap, or "" when the tap missed every photo.
func pick_photo(cam: Camera3D,screen_pos: Vector2) -> String:
	for p in photos:
		var c:=cam.unproject_position(p.node.global_position+Vector3(0,0.01,0))
		var ex:=cam.unproject_position(p.node.global_position+Vector3(0.20,0,0))
		var ey:=cam.unproject_position(p.node.global_position+Vector3(0,0,0.24))
		var rx:=absf(ex.x-c.x)+18.0
		var ry:=absf(ey.y-c.y)+18.0
		if Rect2(c.x-rx,c.y-ry,rx*2,ry*2).has_point(screen_pos): return p.id
	return ""

func is_open(id: String) -> bool:
	for p in photos:
		if p.id==id: return p.open
	return false
