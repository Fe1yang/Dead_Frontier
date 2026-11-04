extends Node3D

const MODELS := {
	"medkit": preload("res://assets/models/medkit.glb"),
	"armor": preload("res://assets/models/armor.glb"),
	"helmet": preload("res://assets/models/helmet.glb"),
	"ammo": preload("res://assets/models/ammo_pickup.glb"),
	"grenade": preload("res://assets/models/frag_grenade.glb"),
	"flashbang": preload("res://assets/models/flashbang.glb"),
	"launcher": preload("res://assets/models/weapons/launcher.glb"),
	"fire_round": preload("res://assets/models/fire_round.glb")
}
const DISPLAY_SCALES := {"medkit": 1.35, "armor": 0.55, "helmet": 1.60, "ammo": 1.25, "grenade": 2.0, "flashbang": 2.0, "launcher": 0.9, "fire_round": 2.4}
const GROUND_OFFSETS := {"medkit": 0.0, "armor": -0.535, "helmet": 0.0, "ammo": 0.0, "grenade": 0.02, "flashbang": 0.02, "launcher": 0.12, "fire_round": 0.03}
const LABELS := {"medkit": "MED", "armor": "ARMOR", "helmet": "HELMET", "ammo": "AMMO", "grenade": "FRAG", "flashbang": "FLASH", "launcher": "LAUNCHER", "fire_round": "INCENDIARY"}
const COLORS := {"medkit": Color("ff7668"), "armor": Color("72d9e5"), "helmet": Color("b6d38a"), "ammo": Color("ffd275"), "grenade": Color("b6d38a"), "flashbang": Color("bdefff"), "launcher": Color("ff9b55"), "fire_round": Color("ff6547")}

var kind := "ammo"
var visual: Node3D
var model_instance: Node3D
var time := 0.0
var base_yaw := 0.0

func _ready() -> void:
	visual = Node3D.new()
	add_child(visual)
	model_instance = MODELS[kind].instantiate() as Node3D
	model_instance.scale = Vector3.ONE * float(DISPLAY_SCALES[kind])
	model_instance.position.y = float(GROUND_OFFSETS[kind])
	visual.add_child(model_instance)
	base_yaw = -0.35 if kind=="armor" else 0.12
	visual.rotation.y = base_yaw
	var light:=OmniLight3D.new(); light.position=Vector3(0,0.58,0)
	light.light_color=COLORS[kind]; light.light_energy=0.38; light.omni_range=1.55; add_child(light)
	_label(LABELS[kind],COLORS[kind])

func _label(text: String,color: Color) -> void:
	var label:=Label3D.new(); label.text=text; label.font_size=42; label.pixel_size=0.004
	label.modulate=color; label.outline_modulate=Color("101513"); label.outline_size=7
	label.billboard=BaseMaterial3D.BILLBOARD_ENABLED; label.position=Vector3(0,0.82,0); add_child(label)

func tick(delta: float) -> void:
	time+=delta
	position.z+=3.5*delta
	visual.position.y=0.045+sin(time*3.0)*0.035
	visual.rotation.y=base_yaw+sin(time*1.2)*0.18
