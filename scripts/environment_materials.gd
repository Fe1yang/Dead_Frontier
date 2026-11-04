extends RefCounted

const ROOT:="res://assets/textures/polyhaven/"
const ASSETS:={"asphalt":"asphalt_01","brick":"red_brick_plaster_patch_02","concrete":"concrete_wall_neutral","plaster":"plastered_wall","pavement":"concrete_pavement"}
static var cache: Dictionary={}

static func apply(root: Node) -> void:
	if root is MeshInstance3D and is_instance_valid(root.mesh):
		for surface in range(root.mesh.get_surface_count()):
			var source: Material=root.get_surface_override_material(surface)
			if source==null: source=root.mesh.surface_get_material(surface)
			if source==null: continue
			var key:=source.resource_name
			if not key.begins_with("PBR_"): continue
			var base_key:=key.split(".",true,1)[0]
			if not cache.has(base_key): cache[base_key]=_make_material(base_key)
			root.set_surface_override_material(surface,cache[base_key])
	for child in root.get_children(): apply(child)

static func _texture(asset: String,map: String) -> Texture2D:
	var path:=ROOT+asset+"/"+asset+"_"+map+"_2k.jpg"
	return load(path) if ResourceLoader.exists(path) else null

static func _make_material(key: String) -> StandardMaterial3D:
	var asset: String=ASSETS.get(key.trim_prefix("PBR_"),key.trim_prefix("PBR_"))
	var m:=StandardMaterial3D.new(); m.resource_name=key+"_LIVE"
	# Keep the modelled architecture, but use clean solid wall colours instead of
	# the heavily stained scans. Road and pavement retain their detailed PBR maps.
	var wall_colors:={"PBR_concrete":Color("b7b9b5"),"PBR_plaster":Color("c7c4ba"),"PBR_brick":Color("aa9183")}
	if wall_colors.has(key):
		m.albedo_color=wall_colors[key]; m.roughness=0.94; m.metallic_specular=0.08
		return m
	m.albedo_texture=_texture(asset,"diff"); m.roughness=0.96; m.metallic_specular=0.12
	m.normal_enabled=true; m.normal_texture=_texture(asset,"nor_gl"); m.normal_scale=0.60
	var rough:=_texture(asset,"rough")
	if rough!=null: m.roughness_texture=rough
	var ao:=_texture(asset,"ao")
	if ao!=null:
		m.ao_enabled=true; m.ao_texture=ao; m.ao_light_affect=0.35
	if asset=="concrete_pavement":
		var arm:=_texture(asset,"arm")
		m.roughness_texture=arm; m.roughness_texture_channel=1
		m.ao_enabled=true; m.ao_texture=arm; m.ao_texture_channel=0; m.ao_light_affect=0.3
	return m
