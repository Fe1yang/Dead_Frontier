extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _rms(path: String) -> Dictionary:
	var s = load(path)
	if s == null:
		return {"path": path, "err": "load failed"}
	var bytes: PackedByteArray = s.get_data()
	var n := bytes.size() / 2
	var sum := 0.0
	var peak := 0.0
	var step := maxi(1, n / 400000)
	var i := 0
	while i < n:
		var v := bytes.decode_s16(i * 2) / 32768.0
		sum += v * v
		peak = maxf(peak, absf(v))
		i += step
	var count := float(maxi(1, i / step))
	var rms := sqrt(sum / count)
	return {"path": path, "rms": rms, "peak": peak, "seconds": s.get_length()}
func _run() -> void:
	for p in ("res://assets/audio/storm_rain.mp3", "res://assets/audio/storm_rain_2.mp3"):
		var r := _rms(p)
		if r.has("rms"):
			print("LOUD ", p.get_file(), " rms=", snappedf(r.rms, 0.0001), " peak=", snappedf(r.peak, 0.001), " len=", snappedf(r.seconds, 0.1))
		else:
			print("LOUD ", p, " ", r)
	print("LOUD_DONE")
	quit()
