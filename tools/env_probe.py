import os
from pathlib import Path
out = Path(__file__).resolve().parents[1] / "diagnostics" / "env-probe.log"
out.write_text("ENV_OK key=%s proxy=%s\n" % (bool(os.environ.get("KIMI_API_KEY")), os.environ.get("KIMI_WORK_NETWORK_PROXY")), encoding="utf-8")
