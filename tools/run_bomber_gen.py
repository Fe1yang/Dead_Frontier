import os, subprocess, sys
os.environ.update({'KIMI_API_KEY': 'sk-kimi-Pc8vJBG4ud8TDurHodA6ltoFnVEe6NXLQdIl3C8yZ7b8j5PtAvZBzK2lgIwad2Pv', 'KIMI_BASE_URL': 'https://agent-gw.kimi.com/coding/', 'KIMI_WORK_NETWORK_PROXY': 'desktop', 'KIMI_WORK_CONTEXT_IPC': '\\\\.\\pipe\\kimi-work-12c596c8-3494-4f9f-8542-fa9acbf59e46', 'AGENT_GW_MCP_URL': 'https://agent-gw.kimi.com/coding/v1/mcp/', 'KIMI_AGENT_REGION': 'oversea', 'KIMI_AGENT_CLIENT_ID': 'kimiwork', 'KIMI_AGENT_GW_KEY': 'sk-kimi-Pc8vJBG4ud8TDurHodA6ltoFnVEe6NXLQdIl3C8yZ7b8j5PtAvZBzK2lgIwad2Pv'})
TOOL='C:\\Users\\user\\AppData\\Roaming\\kimi-desktop\\daimon-share\\daimon\\runtime\\kimi-code\\home\\plugins\\managed\\model3d_generation\\scripts\\model3d_generation_tool.py'
ROOT='C:\\Users\\user\\Documents\\kimi\\tasks\\2026-11-02\\20-32-30-26dbcd78'
which=sys.argv[1]
JOBS={
 "male":("Bloated fat male zombie, hugely swollen gas-filled belly about to burst, glowing yellow-green pustules and boils across the belly and chest, torn stained shirt stretched tight over the gut, gray-green rotting skin, sagging pants, strict T-pose with both arms fully extended straight out to the sides horizontally, arms and hands clearly visible and separated from the body, full body, apocalyptic survival horror game character, highly detailed texture","zombie_bomber_hd.glb"),
 "female":("Bloated fat female zombie, hugely swollen gas-filled belly about to burst, glowing yellow-green pustules and boils across the belly, torn stained tank top stretched tight over the gut, pale gray-green rotting skin, long messy dark hair, strict T-pose with both arms fully extended straight out to the sides horizontally, arms and hands clearly visible and separated from the body, full body, apocalyptic survival horror game character, highly detailed texture","zombie_bomber_female_hd.glb"),
}
desc,out=JOBS[which]
log=open(os.path.join(ROOT,"diagnostics","bomber-%s-gen.log"%which),"wb")
proc=subprocess.run([sys.executable,"-u",TOOL,"generate","--description",desc,"--model","v3.1","--face-limit","30000","--output",os.path.join(ROOT,"assets","models","actors",out)],stdout=log,stderr=subprocess.STDOUT)
log.close()
sys.exit(proc.returncode)
