"""Create self-contained OpenFilm 7-second animation+48kHz WAV tone+VTT.

No network/no models/no render; explicit --create required for any write.
No overwrite of any existing media. Workspace path must be an existing directory.
"""
from pathlib import Path
import argparse,io,json,math,struct,wave

REL='qc/openfilm-e2e/fixture'

def wav_bytes():
    b=io.BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000)
        # 2.5 s original low-level, non-speech audible signal
        frames=bytearray()
        for n in range(120000):
            ramp=min(1,n/1000,(120000-n)/1000)
            y=int(4500*max(0,ramp)*math.sin(2*math.pi*440*n/48000))
            frames.extend(struct.pack('<h',y))
        w.writeframes(frames)
    return b.getvalue()

FILM='''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=1280, height=720"></head><body>
<section><iframe id="probe" src="scenes/probe.html#t=0,7" at="0" style="width:1280px;height:720px"></iframe></section>
<section><audio id="tone" src="audio/probe-tone.wav#t=0,2.5" at="1" volume="0.35"></audio></section>
<section><track kind="captions" srclang="vi" label="Kiểm thử âm thanh" src="captions/probe.vtt"></track></section>
</body></html>\n'''
SCENE='''<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>body{margin:0;background:#12253b;color:white;font:46px sans-serif;overflow:hidden}#ball{position:absolute;top:260px;left:0;width:100px;height:100px;border-radius:50%;background:#ffc85a;box-shadow:0 0 30px #ffc85a}#lab{position:absolute;top:60px;left:60px}</style></head><body><div id="lab">OPENFILM · E2E 7s</div><div id="ball"></div>
<script>const ball=document.getElementById('ball');window.film={duration:7,frame(t){const x=Math.max(0,Math.min(1,t/7));ball.style.transform=`translateX(${80+980*x}px)`;}};</script>
</body></html>\n'''
VTT='''WEBVTT\n\n00:00:01.000 --> 00:00:03.500\nKiểm tra hình ảnh và âm thanh OpenFilm\n'''

def plan(workspace):
    workspace=Path(workspace).resolve()
    if not workspace.is_dir():raise ValueError('workspace must already exist')
    root=workspace/REL
    if not root.resolve().is_relative_to(workspace):raise ValueError('fixture destination outside workspace')
    paths=[root/'film.html',root/'scenes/probe.html',root/'audio/probe-tone.wav',root/'captions/probe.vtt']
    if any(not p.resolve().is_relative_to(workspace) for p in paths):
        raise ValueError('fixture path resolves outside workspace')
    return root,paths

def build(workspace,create=False):
    root,paths=plan(workspace)
    exists=[str(p) for p in paths if p.exists()]
    if create:
        if exists:raise FileExistsError('would overwrite: '+', '.join(exists))
        for p in paths:p.parent.mkdir(parents=True,exist_ok=True)
        bytes_=[FILM.encode(),SCENE.encode(),wav_bytes(),VTT.encode()]
        for p,b in zip(paths,bytes_):
            with p.open('xb') as f:f.write(b)
    return {'status':'CREATED' if create else 'PLAN','files':[str(p) for p in paths],'existing':exists,'durationS':7,'wavHz':48000,'speechTtsValidated':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True,type=Path);p.add_argument('--create',action='store_true')
    a=p.parse_args()
    try:print(json.dumps(build(a.workspace,a.create),ensure_ascii=False,indent=2))
    except Exception as e:print(json.dumps({'status':'BLOCKED','reason':str(e)},ensure_ascii=False));raise SystemExit(2)
