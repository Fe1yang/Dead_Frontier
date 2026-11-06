import os, subprocess, sys
os.environ.update({'KIMI_API_KEY': 'sk-kimi-Pc8vJBG4ud8TDurHodA6ltoFnVEe6NXLQdIl3C8yZ7b8j5PtAvZBzK2lgIwad2Pv', 'KIMI_BASE_URL': 'https://agent-gw.kimi.com/coding/', 'KIMI_WORK_NETWORK_PROXY': 'desktop', 'KIMI_WORK_CONTEXT_IPC': '\\\\.\\pipe\\kimi-work-12c596c8-3494-4f9f-8542-fa9acbf59e46', 'AGENT_GW_MCP_URL': 'https://agent-gw.kimi.com/coding/v1/mcp/', 'KIMI_AGENT_REGION': 'oversea', 'KIMI_AGENT_CLIENT_ID': 'kimiwork', 'KIMI_AGENT_GW_KEY': 'sk-kimi-Pc8vJBG4ud8TDurHodA6ltoFnVEe6NXLQdIl3C8yZ7b8j5PtAvZBzK2lgIwad2Pv'})
TOOL='C:\\Users\\user\\AppData\\Roaming\\kimi-desktop\\daimon-share\\daimon\\runtime\\kimi-code\\home\\plugins\\managed\\model3d_generation\\scripts\\model3d_generation_tool.py'
ROOT='C:\\Users\\user\\Documents\\kimi\\tasks\\2026-11-02\\20-32-30-26dbcd78'
which=sys.argv[1]
JOBS={
 "riley":("Hand-painted comic-book style female survivor, graphic novel look, matte painterly textures with visible brush strokes, muted desaturated colors, soft cel shading, absolutely no glossy plastic look, slightly oversized head, about 5.5 heads tall stylized proportions, fair skin, dark brown hair tied back in a low ponytail with a few loose strands, wearing an open dark burgundy leather jacket with popped collar and snap chest pockets over a light gray henley shirt, dark charcoal cargo pants with large thigh pockets, black belt, black lace-up combat boots, strict T-pose with both arms fully extended straight out to the sides horizontally, arms and hands clearly visible and separated from the body, full body, stylized face matching a gritty comic illustration, apocalyptic survival game character","survivor_riley_hd.glb"),
 "maya":("Hand-painted comic-book style Black female survivor, graphic novel look, matte painterly textures with visible brush strokes, muted desaturated colors, soft cel shading, absolutely no glossy plastic look, dark brown skin, slightly oversized head, about 5.5 heads tall stylized proportions, natural black hair in neat shoulder-length twists pulled back from the face, wearing a fitted olive-green field jacket over a dark gray t-shirt, dark blue slim jeans, brown hiking boots, strict T-pose with both arms fully extended straight out to the sides horizontally, arms and hands clearly visible and separated from the body, full body, stylized face matching a gritty comic illustration, apocalyptic survival game character","survivor_maya_hd.glb"),
}
desc,out=JOBS[which]
log=open(os.path.join(ROOT,"diagnostics","female-%s-gen.log"%which),"wb")
proc=subprocess.run([sys.executable,"-u",TOOL,"generate","--description",desc,"--model","v3.1","--face-limit","30000","--output",os.path.join(ROOT,"assets","models","generated",out)],stdout=log,stderr=subprocess.STDOUT)
log.close()
sys.exit(proc.returncode)
