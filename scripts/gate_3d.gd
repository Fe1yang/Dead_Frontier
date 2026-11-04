extends Node3D
## Upgrade gate: two glowing barrier panels side by side across the road, like the
## "pick a side" gates in runner games. Each half shows one buff in big lettering; the survivor
## runs through one half and gets that buff. The chosen half flares and the other fades out.

const GameText=preload("res://scripts/game_text.gd")
const ROAD_HALF:=3.15
const PANEL_BOTTOM:=0.22
const PANEL_TOP:=1.95
const POST_HEIGHT:=2.15
# Left half always blue, right half always red, like the runner-game gates.
const SIDE_COLORS:=[Color("2f7bff"),Color("ff3b3b")]

static var gate_font: Font

var language:="en"
var left: Dictionary={}
var right: Dictionary={}
var resolved:=false
var selected:=-1
var fade:=1.0
var pulse:=0.0
var labels: Array[Label3D]=[]
var panels: Array[MeshInstance3D]=[]   # [left, right]
var panel_mats: Array[StandardMaterial3D]=[]
var trim_mats: Array[StandardMaterial3D]=[]
var halves: Array[Node3D]=[]
var flare:=0.0

static func _font() -> Font:
	if gate_font==null:
		var base:=(load("res://assets/fonts/hud_condensed_bold.otf") as FontFile).duplicate() as FontFile
		var fallbacks: Array[Font]=[]
		if ResourceLoader.exists("res://assets/fonts/hud_cjk_black.otf"): fallbacks.append(load("res://assets/fonts/hud_cjk_black.otf"))
		var system:=SystemFont.new(); system.font_names=PackedStringArray(["Microsoft YaHei","PingFang SC","Noto Sans CJK SC","Segoe UI","Arial"])
		fallbacks.append(system); base.fallbacks=fallbacks
		var heavy:=FontVariation.new(); heavy.base_font=base; heavy.variation_embolden=0.6
		gate_font=heavy
	return gate_font

func setup(first: Dictionary,second: Dictionary,language_code:="en") -> void:
	language=language_code
	left=first; right=second
	_make_option(left,-ROAD_HALF*0.5,0)
	_make_option(right,ROAD_HALF*0.5,1)
	# Posts: outer edges plus a shared one in the middle.
	for x in [-ROAD_HALF,0.0,ROAD_HALF]: _post(x)

func _unshaded(color: Color,add:=false) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new(); m.albedo_color=color
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode=BaseMaterial3D.CULL_DISABLED
	if add: m.blend_mode=BaseMaterial3D.BLEND_MODE_ADD
	return m

func _box(parent: Node3D,pos:Vector3,size:Vector3,mat: Material) -> MeshInstance3D:
	var n:=MeshInstance3D.new(); var mesh:=BoxMesh.new(); mesh.size=size; n.mesh=mesh
	n.position=pos; n.material_override=mat; parent.add_child(n); return n

func _post(x: float) -> void:
	var post_mat:=StandardMaterial3D.new(); post_mat.albedo_color=Color("2f3436"); post_mat.roughness=0.5; post_mat.metallic=0.5
	var n:=MeshInstance3D.new(); var c:=CylinderMesh.new(); c.top_radius=0.09; c.bottom_radius=0.11; c.height=POST_HEIGHT
	n.mesh=c; n.position=Vector3(x,POST_HEIGHT*0.5,0); n.material_override=post_mat; add_child(n)
	var cap:=MeshInstance3D.new(); var s:=SphereMesh.new(); s.radius=0.13; s.height=0.26; cap.mesh=s
	cap.position=Vector3(x,POST_HEIGHT,0); cap.material_override=post_mat; add_child(cap)
	var foot:=MeshInstance3D.new(); var f:=CylinderMesh.new(); f.top_radius=0.16; f.bottom_radius=0.2; f.height=0.1
	foot.mesh=f; foot.position=Vector3(x,0.05,0); foot.material_override=post_mat; add_child(foot)

func _make_option(option: Dictionary,x: float,index: int) -> void:
	var color: Color=SIDE_COLORS[index]
	var half:=Node3D.new(); half.position=Vector3(x,0,0); add_child(half); halves.append(half)
	var width:=ROAD_HALF-0.12
	var height:=PANEL_TOP-PANEL_BOTTOM
	var mid_y:=(PANEL_TOP+PANEL_BOTTOM)*0.5
	# Translucent glowing barrier sheet.
	var deep:=color.darkened(0.15); deep.s=minf(1.0,deep.s*1.35)
	var sheet_mat:=_unshaded(Color(deep.r,deep.g,deep.b,0.28))
	var sheet:=_box(half,Vector3(0,mid_y,0),Vector3(width,height,0.03),sheet_mat)
	panels.append(sheet); panel_mats.append(sheet_mat)
	# Bright frame bars top and bottom, and a soft additive glow behind.
	var trim:=_unshaded(color.lightened(0.25)); trim_mats.append(trim)
	_box(half,Vector3(0,PANEL_TOP,0.0),Vector3(width,0.09,0.07),trim)
	_box(half,Vector3(0,PANEL_BOTTOM,0.0),Vector3(width,0.07,0.07),trim)
	_box(half,Vector3(0,mid_y,-0.02),Vector3(width+0.3,height+0.3,0.01),_unshaded(Color(color.r,color.g,color.b,0.10),true))
	# Lettering: the effect huge, the name smaller above it.
	var parts:=GameText.gate(language,option.id,option.title+"|"+option.detail).split("|")
	var title: String=parts[0]
	var detail: String=parts[1] if parts.size()>1 else ""
	var big:=Label3D.new(); big.text=detail; big.font=_font()
	big.font_size=_fit(detail,150,2.75,0.0092); big.pixel_size=0.0092; big.outline_size=28
	big.modulate=Color("ffffff"); big.outline_modulate=color.darkened(0.65)
	big.position=Vector3(0,mid_y-0.22,0.05); big.double_sided=false
	big.render_priority=5; big.outline_render_priority=4
	half.add_child(big); labels.append(big)
	var small:=Label3D.new(); small.text=title; small.font=_font()
	small.font_size=_fit(title,110,2.6,0.0072); small.pixel_size=0.0072; small.outline_size=28
	small.modulate=Color("ffffff"); small.outline_modulate=color.darkened(0.65)
	small.position=Vector3(0,mid_y+0.50,0.05); small.double_sided=false
	small.render_priority=5; small.outline_render_priority=4
	half.add_child(small); labels.append(small)

## Shrinks the font so long words (German, Russian...) still fit inside the panel width.
func _fit(text: String,size: int,max_width_m: float,pixel: float) -> int:
	var f:=_font()
	while size>40 and f.get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,size).x*pixel>max_width_m: size-=6
	return size

func tick(delta: float) -> void:
	pulse+=delta
	if not resolved:
		position.z+=3.5*delta
		# Gentle shimmer so the gates read as energy barriers.
		for i in range(panel_mats.size()):
			panel_mats[i].albedo_color.a=0.26+0.05*sin(pulse*3.0+i*1.7)
		return
	position.z+=3.5*delta
	fade=maxf(0.0,fade-delta*1.6)
	flare=maxf(0.0,flare-delta*2.5)
	for i in range(halves.size()):
		var chosen: bool=i==selected
		var a: float=fade if chosen else fade*fade*0.6
		panel_mats[i].albedo_color.a=(0.28+0.5*flare)*a if chosen else 0.28*a
		trim_mats[i].albedo_color.a=a
		if chosen: halves[i].scale=Vector3.ONE*(1.0+0.12*flare)
	for label in labels: label.modulate.a=fade; label.outline_modulate.a=fade

func choose(player_x: float) -> Dictionary:
	if resolved: return {}
	resolved=true; selected=0 if player_x<0 else 1; flare=1.0
	return left if selected==0 else right
