shader_type spatial;
render_mode diffuse_burley, specular_disabled;

uniform vec4 base_color : source_color = vec4(1.0);
uniform sampler2D base_texture : source_color, filter_linear_mipmap, repeat_enable;
uniform bool use_texture = false;

void fragment() {
	vec3 ink = base_color.rgb;
	if (use_texture) ink *= texture(base_texture, UV).rgb;
	ALBEDO = ink;
	EMISSION = ink * 0.20;
	ROUGHNESS = 1.0;
}

void light() {
	float ndl = dot(NORMAL, LIGHT);
	float band = 0.36;
	if (ndl > 0.08) band = 0.64;
	if (ndl > 0.48) band = 0.88;
	if (ndl > 0.78) band = 1.0;
	DIFFUSE_LIGHT += ALBEDO * LIGHT_COLOR * ATTENUATION * band;
}
