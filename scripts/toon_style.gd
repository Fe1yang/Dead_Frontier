extends RefCounted

const TOON_SHADER=preload("res://shaders/comic_toon.gdshader")
const OUTLINE_SHADER=preload("res://shaders/comic_outline.gdshader")
static var material_cache: Dictionary={}
static var outline_cache: Dictionary={}

static func apply(root: Node,thickness: float=0.012) -> void:
	if root is MeshInstance3D and is_instance_valid(root.mesh):
		for surface in range(root.mesh.get_surface_count()):
			var source: Material=root.get_surface_override_material(surface)
			if source==null: source=root.mesh.surface_get_material(surface)
			if source is ShaderMaterial: continue
			var color:=Color(0.65,0.68,0.64)
			var texture: Texture2D=null
			if source is StandardMaterial3D:
				color=source.albedo_color
				texture=source.albedo_texture
			var key:=color.to_html()+str(texture.get_rid() if texture!=null else "")+str(thickness)
			if not material_cache.has(key):
				var toon:=ShaderMaterial.new(); toon.shader=TOON_SHADER
				toon.set_shader_parameter("base_color",color)
				toon.set_shader_parameter("use_texture",texture!=null)
				if texture!=null: toon.set_shader_parameter("base_texture",texture)
				if not outline_cache.has(thickness):
					var outline:=ShaderMaterial.new(); outline.shader=OUTLINE_SHADER
					outline.set_shader_parameter("thickness",thickness); outline_cache[thickness]=outline
				toon.next_pass=outline_cache[thickness]; material_cache[key]=toon
			root.set_surface_override_material(surface,material_cache[key])
	for child in root.get_children(): apply(child,thickness)
