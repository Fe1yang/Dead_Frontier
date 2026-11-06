import os, subprocess, sys
os.environ.update({'KIMI_API_KEY': 'sk-kimi-Pc8vJBG4ud8TDurHodA6ltoFnVEe6NXLQdIl3C8yZ7b8j5PtAvZBzK2lgIwad2Pv', 'KIMI_BASE_URL': 'https://agent-gw.kimi.com/coding/', 'KIMI_WORK_NETWORK_PROXY': 'desktop', 'KIMI_WORK_CONTEXT_IPC': '\\\\.\\pipe\\kimi-work-12c596c8-3494-4f9f-8542-fa9acbf59e46', 'AGENT_GW_MCP_URL': 'https://agent-gw.kimi.com/coding/v1/mcp/', 'KIMI_AGENT_REGION': 'oversea', 'KIMI_AGENT_CLIENT_ID': 'kimiwork', 'KIMI_AGENT_GW_KEY': 'sk-kimi-Pc8vJBG4ud8TDurHodA6ltoFnVEe6NXLQdIl3C8yZ7b8j5PtAvZBzK2lgIwad2Pv'})
TOOL='C:\\Users\\user\\AppData\\Roaming\\kimi-desktop\\daimon-share\\daimon\\runtime\\kimi-code\\home\\plugins\\managed\\model3d_generation\\scripts\\model3d_generation_tool.py'
ROOT='C:\\Users\\user\\Documents\\kimi\\tasks\\2026-11-02\\20-32-30-26dbcd78'
desc=("Photorealistic adult Black woman survivor, realistic anatomy, natural proportions 7.5 heads tall, "
"normal size head, realistic adult face with normal-sized eyes and natural eye spacing, defined cheekbones, "
"no cartoon or doll-like face, deep brown skin, long black box braids with dark red thread wraps in a high ponytail, "
"cropped rust-red tactical bomber jacket with rolled sleeves and patches over a charcoal compression top, "
"dark leather chest rig with brass buckles and pouches, black tactical cargo pants with knee pads, "
"fingerless gloves, tan combat boots, canvas utility belt, distinctive layered post-apocalyptic outfit, "
"strict T-pose with arms fully extended horizontally, full body, hand-painted matte textures, "
"muted desaturated colors, gritty graphic novel style")
out=os.path.join(ROOT,"assets","models","generated","survivor_maya_hd.glb")
log=open(os.path.join(ROOT,"diagnostics","maya-v4-gen.log"),"wb")
proc=subprocess.Popen([sys.executable,"-u",TOOL,"generate","--description",desc,"--model","v3.1","--face-limit","30000","--output",out],stdout=log,stderr=subprocess.STDOUT)
print("PID",proc.pid)
