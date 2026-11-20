"""Extract deterministic screenshot evidence ONLY from a real rendered MP4.

This does not mark visual QC PASS. The agent MUST receive generated images
as multimodal content and inspect them before writing any review receipt.
Execution on Windows requires a prior approved macro scope covering the
FFmpeg/FFprobe binaries and output directory; no install/network/shell.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
from fractions import Fraction
from pathlib import Path

ROLES = {'M5': ('START','Q1','MID','Q3','END'),
         'M6': ('START','MID','END'),
         'M7': ('START','MID','END')}


def sample_frames(film: dict | None, macro_id: str, observed_frames: int):
    """Return (target_id, role, absolute video frame index) in stable order."""
    if macro_id not in ROLES or type(observed_frames) is not int or observed_frames < 1:
        raise ValueError('invalid macro or observed frame count')
    if macro_id == 'M5':
        shot_spans=[('SMOKE',0,observed_frames)]
    else:
        if not isinstance(film,dict) or not isinstance(film.get('shots'),list) or not film['shots']:
            raise ValueError('FilmData shots required for draft/master sampling')
        shot_spans=[];seen=set()
        for sh in film['shots']:
            name=sh.get('id');start=sh.get('startFrame');length=sh.get('durationInFrames')
            if not isinstance(name,str) or not name or name in seen or type(start) is not int or type(length) is not int or start<0 or length<1:
                raise ValueError('invalid FilmData shot ID/frame span')
            if start+length>observed_frames:raise ValueError('film shot exceeds rendered video frames')
            seen.add(name);shot_spans.append((name,start,length))
    offsets={'START':Fraction(0),'Q1':Fraction(1,4),'MID':Fraction(1,2),'Q3':Fraction(3,4),'END':Fraction(1)}
    out=[]
    for name,start,length in shot_spans:
        for role in ROLES[macro_id]:
            frame=start+int((length-1)*offsets[role])
            if frame>=observed_frames:raise ValueError('frame exceeds render')
            out.append((name,role,frame))
    return out


def sha256(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()


def within_workspace(workspace:Path, relative:str)->Path:
    if not isinstance(relative,str) or not relative or relative.startswith(('/', '\\')) or ':' in relative or '\0' in relative:
        raise ValueError('unsafe path')
    parts=relative.replace('\\','/').split('/')
    if any(p in ('','..') for p in parts):raise ValueError('unsafe path traversal')
    root=workspace.resolve();path=(root/Path(*parts)).resolve()
    if not path.is_relative_to(root):raise ValueError('outside workspace')
    return path


def _exe(value:str)->Path:
    path=Path(value)
    if not path.is_absolute() or not path.is_file():raise ValueError('explicit verified absolute executable path required')
    return path.resolve()


def _probe(ffprobe:Path,video:Path):
    cmd=[str(ffprobe),'-v','error','-show_entries','stream=codec_type,avg_frame_rate','-show_entries','format=duration','-of','json',str(video)]
    done=subprocess.run(cmd,capture_output=True,text=True,timeout=120,check=False,shell=False)
    if done.returncode!=0:raise RuntimeError('ffprobe failed: '+done.stderr[-1000:])
    meta=json.loads(done.stdout)
    stream=next((s for s in meta.get('streams',[]) if s.get('codec_type')=='video'),None)
    if stream is None:raise ValueError('video stream missing')
    fps=Fraction(stream.get('avg_frame_rate','0/1'))
    duration=float(meta.get('format',{}).get('duration',0))
    if fps<=0 or duration<=0:raise ValueError('invalid actual FPS or video duration')
    return float(fps),duration,cmd


def run(workspace:Path, macro:str, video_relative:str, film_data_relative:str|None, ffmpeg_path:str, ffprobe_path:str)->dict:
    if macro not in ROLES:raise ValueError('only rendered MP4 macros M5/M6/M7 are supported')
    root=workspace.resolve();video=within_workspace(root,video_relative)
    if not video.is_file() or video.suffix.lower()!='.mp4':raise ValueError('render source must be existing MP4')
    if video.stat().st_size<12 or video.read_bytes()[:12][4:8]!=b'ftyp':raise ValueError('invalid MP4 container signature')
    ffmpeg=_exe(ffmpeg_path);ffprobe=_exe(ffprobe_path)
    fps,duration,probe_cmd=_probe(ffprobe,video)
    total=max(1,int(round(fps*duration)))
    film=None
    if macro!='M5':
        if not film_data_relative:raise ValueError('FilmData required for draft/master')
        film_path=within_workspace(root,film_data_relative)
        film=json.loads(film_path.read_text(encoding='utf-8'))
        if abs(int(film['fps'])-fps)>0.01:raise ValueError('FilmData FPS differs from rendered FPS')
    samples=sample_frames(film,macro,total)
    source_hash=sha256(video)
    outputs=[];commands=[];outdir=within_workspace(root,f'qc/visual/{macro}/frames');outdir.mkdir(parents=True,exist_ok=True)
    for target,role,frame in samples:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',target):raise ValueError('unsafe shot ID for output name')
        path=within_workspace(root,f'qc/visual/{macro}/frames/{target}-{role}-{source_hash[:10]}.png')
        if not path.is_file():
            cmd=[str(ffmpeg),'-nostdin','-v','error','-ss',f'{frame/fps:.7f}','-i',str(video),'-frames:v','1','-f','image2','-n',str(path)]
            done=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=False,shell=False,cwd=str(root))
            commands.append({'args':cmd,'exitCode':done.returncode,'stderrTail':done.stderr[-1000:]})
            if done.returncode!=0 or not path.is_file():raise RuntimeError(f'frame extract failed for {target}/{role}')
        rel=path.relative_to(root).as_posix()
        outputs.append({'targetId':target,'frameRole':role,'frameIndex':frame,'imagePath':rel,'imageSha256':sha256(path)})
    extract={'sourcePath':video_relative,'sourceSha256':source_hash,'engine':'FFMPEG_FROM_RENDERED_MP4',
             'exitCode':0,'fps':fps,'duration':duration,'imagePaths':[o['imagePath'] for o in outputs],
             'frameSamples':outputs,'commands':commands,'ffprobeCommand':probe_cmd,
             'warning':'Extraction log is NOT evidence that ChatGPT has actually received or viewed these images.'}
    out=within_workspace(root,f'qc/visual/{macro}/extract.json');out.parent.mkdir(parents=True,exist_ok=True)
    temp=out.with_name(out.name+'.tmp')
    temp.write_text(json.dumps(extract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(out)
    return {'extractLog':out.relative_to(root).as_posix(),'extractSha256':sha256(out),'frames':len(outputs),
            'targets':sorted({x['targetId'] for x in outputs}), 'status':'IMAGES_EXTRACTED_NOT_VISUALLY_REVIEWED'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Approved-workspace MP4 frame extraction, no visual PASS')
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--macro',choices=tuple(ROLES),required=True)
    parser.add_argument('--render',required=True,help='Workspace-relative MP4')
    parser.add_argument('--filmdata',help='Workspace-relative FilmData JSON, required for M6/M7')
    parser.add_argument('--ffmpeg',required=True,help='Absolute path of already-approved FFmpeg executable')
    parser.add_argument('--ffprobe',required=True,help='Absolute path of already-approved FFprobe executable')
    a=parser.parse_args()
    print(json.dumps(run(a.workspace,a.macro,a.render,a.filmdata,a.ffmpeg,a.ffprobe),ensure_ascii=False,indent=2))
