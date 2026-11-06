extends SceneTree

const OUT := "res://diagnostics/godot_actor_axes"
const ACTORS := {
    "male": "res://assets/models/actors/survivor_male_universal.glb",
    "female": "res://assets/models/actors/survivor_female.glb",
    "walker": "res://assets/models/actors/zombie_walker.glb"
}
const VIEWS := {
    "pos_z": Vector3(0, 1.55, 5),
    "pos_x": Vector3(5, 1.55, 0),
    "neg_z": Vector3(0, 1.55, -5),
    "neg_x": Vector3(-5, 1.55, 0)
}

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
    root.size = Vector2i(384, 512)
    var world := Node3D.new()
    root.add_child(world)
    var environment := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("283039")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("c7d4df")
    env.ambient_light_energy = 0.65
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    environment.environment = env
    world.add_child(environment)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-48, -32, 0)
    sun.light_energy = 1.5
    sun.shadow_enabled = true
    world.add_child(sun)
    var fill := OmniLight3D.new()
    fill.position = Vector3(-2, 3, 2)
    fill.light_energy = 1.2
    fill.omni_range = 8
    world.add_child(fill)
    var camera := Camera3D.new()
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.size = 2.35
    camera.near = 0.05
    camera.far = 50
    world.add_child(camera)
    camera.current = true
    for key in ACTORS:
        var model := load(ACTORS[key]).instantiate() as Node3D
        world.add_child(model)
        for view in VIEWS:
            camera.position = VIEWS[view]
            camera.look_at(Vector3(0, 0.98, 0), Vector3.UP)
            await process_frame
            await RenderingServer.frame_post_draw
            var image := root.get_texture().get_image()
            var path := "%s/%s_%s.png" % [OUT, key, view]
            image.save_png(path)
            print("GODOT_AXIS_VIEW ", key, " ", view)
        model.free()
    quit()
