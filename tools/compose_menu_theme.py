from pathlib import Path
import numpy as np
import wave

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'audio'/'dead_run_theme.wav'
SR=32000
BPM=80
BEAT=60.0/BPM
BARS=8
DURATION=BARS*4*BEAT
N=int(SR*DURATION)
mix=np.zeros((N,2),dtype=np.float64)
rng=np.random.default_rng(7319)

def add(signal,start,volume=1.0,pan=0.0):
    index=int(start*SR)
    if index>=N: return
    length=min(len(signal),N-index)
    if length<=0: return
    left=np.sqrt((1-pan)*0.5); right=np.sqrt((1+pan)*0.5)
    mix[index:index+length,0]+=signal[:length]*volume*left
    mix[index:index+length,1]+=signal[:length]*volume*right

def tone(freq,duration,kind='pad'):
    t=np.arange(int(duration*SR))/SR
    if kind=='pad':
        s=(np.sin(2*np.pi*freq*t)+0.32*np.sin(2*np.pi*freq*2*t)+0.15*np.sin(2*np.pi*freq*0.5*t))
        attack=np.minimum(1,t/0.45); release=np.minimum(1,(duration-t)/0.65)
        return s*attack*release
    if kind=='bass':
        s=np.sin(2*np.pi*freq*t)+0.28*np.sin(2*np.pi*freq*2*t)
        env=(1-np.exp(-t*45))*np.exp(-t*2.5)
        return s*env
    if kind=='bell':
        s=np.sin(2*np.pi*freq*t)+0.42*np.sin(2*np.pi*freq*2.01*t)+0.16*np.sin(2*np.pi*freq*3.98*t)
        return s*(1-np.exp(-t*70))*np.exp(-t*2.2)
    return np.zeros_like(t)

def kick():
    t=np.arange(int(0.38*SR))/SR
    phase=2*np.pi*(52*t+48*(1-np.exp(-t*24))/24)
    return np.sin(phase)*np.exp(-t*11)

def snare():
    t=np.arange(int(0.28*SR))/SR
    noise=rng.uniform(-1,1,len(t))
    return (noise*0.7+np.sin(2*np.pi*170*t)*0.25)*np.exp(-t*18)

def hat():
    t=np.arange(int(0.09*SR))/SR
    noise=rng.uniform(-1,1,len(t))
    return np.concatenate(([0.0],np.diff(noise)))*np.exp(-t*55)

# D minor progression, one chord per bar. The arrangement remains sparse so
# menu text and sound effects retain space.
chords=[(146.83,174.61,220.0),(116.54,146.83,174.61),(174.61,220.0,261.63),(130.81,164.81,196.0),
        (146.83,174.61,220.0),(116.54,146.83,174.61),(130.81,164.81,196.0),(130.81,164.81,196.0)]
roots=[73.42,58.27,87.31,65.41,73.42,58.27,65.41,65.41]
for bar,chord in enumerate(chords):
    start=bar*4*BEAT
    for j,freq in enumerate(chord):
        add(tone(freq,4*BEAT,'pad'),start,0.075,(-0.45+j*0.45))
        add(tone(freq*0.5,4*BEAT,'pad'),start,0.028,(0.3-j*0.3))
    for beat in range(4):
        add(tone(roots[bar],0.65*BEAT,'bass'),start+beat*BEAT,0.16,-0.08)
    add(kick(),start,0.28); add(kick(),start+2*BEAT,0.23)
    add(snare(),start+BEAT,0.055,0.1); add(snare(),start+3*BEAT,0.06,0.1)
    for eighth in range(8): add(hat(),start+eighth*BEAT/2,0.018,0.42)
    if bar>=4:
        melody=[chord[2]*2,chord[1]*2,chord[0]*2,chord[1]*2]
        for beat,freq in enumerate(melody):
            if beat in (0,2): add(tone(freq,1.8,'bell'),start+beat*BEAT,0.045,0.18)

# Short, low-level stereo echoes; no noise bed and no abrupt loop boundary.
dry=mix.copy()
for delay,gain in ((0.27,0.13),(0.53,0.07)):
    d=int(delay*SR)
    mix[d:]+=dry[:-d,::-1]*gain
fade=int(0.04*SR)
mix[:fade]*=np.linspace(0,1,fade)[:,None]
mix[-fade:]*=np.linspace(1,0,fade)[:,None]
mix*=0.78/max(0.78,np.max(np.abs(mix)))
pcm=(mix*32767).astype('<i2')
OUT.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(OUT),'wb') as wav:
    wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(SR); wav.writeframes(pcm.tobytes())
print('MENU_THEME_WRITTEN',OUT,'seconds',DURATION,'peak',float(np.max(np.abs(mix))))
