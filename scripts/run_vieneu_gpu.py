"""Local-only VieNeu preset synthesis. Requires an existing CUDA environment/model.

Run using that environment's Python. Never installs, downloads, clones a voice,
or falls back to CPU. Writes only new audio and evidence below --workspace.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import time

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def run(workspace,model,moss,manifest):
    root=Path(workspace).resolve(strict=True)
    model=Path(model).resolve(strict=True);moss=Path(moss).resolve(strict=True)
    manifest=Path(manifest).resolve(strict=True)
    if not manifest.is_relative_to(root):raise ValueError('manifest outside workspace')
    jobs=json.loads(manifest.read_text(encoding='utf-8'))
    paths=[]
    for job in jobs:
        relative=Path(job['output'])
        path=(root/relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root) or path.exists():
            raise ValueError('unsafe/existing output '+str(path))
        paths.append(path)
    cache=root/'runtime-cache';cache.mkdir(exist_ok=True)
    for key in ('HF_HOME','HF_MODULES_CACHE','TORCH_HOME','NUMBA_CACHE_DIR'):
        os.environ[key]=str(cache/key.lower())
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
    attempts=[]
    def blocked(*args,**kwargs):
        attempts.append('network denied');raise RuntimeError('offline production: network denied')
    socket.socket.connect=blocked;socket.socket.connect_ex=blocked;socket.create_connection=blocked
    import torch
    import soundfile as sf
    import numpy as np
    from vieneu import Vieneu
    if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable; CPU fallback is not authorized')
    torch.manual_seed(141)
    start=time.time();print('CUDA '+torch.cuda.get_device_name(0),flush=True)
    tts=Vieneu(mode='v3turbo',backend='pytorch',device='cuda',backbone_repo=str(model),moss_tokenizer=str(moss))
    def devices():
        return {'backbone':str(next(tts.engine.model.parameters()).device),
                'codec':str(next(tts.engine.audio_tokenizer.parameters()).device),'engine':str(tts.engine.device)}
    observed=devices()
    if tts.backend!='pytorch' or any(not d.startswith('cuda') for d in observed.values()):
        raise RuntimeError('GPU backend mismatch '+str(observed))
    report={'backend':'pytorch','device':observed,'gpu':torch.cuda.get_device_name(0),
        'torchVersion':torch.__version__,'cudaVersion':torch.version.cuda,'modelSource':'local-only',
        'modelFiles':{str(p.relative_to(model)):sha(p) for p in model.rglob('*') if p.is_file() and '.cache' not in p.parts},
        'mossFiles':{str(p.relative_to(moss)):sha(p) for p in moss.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.cache' not in p.parts},
        'networkBlocked':True,'downloads':False,'cpuFallback':False,'voiceCloning':False,'wav':[]}
    for job,path in zip(jobs,paths):
        print('SYNTHESIZE '+job['id'],flush=True)
        audio=tts.infer(job['text'],voice=job['voice'])
        torch.cuda.synchronize()
        if any(not d.startswith('cuda') for d in devices().values()):raise RuntimeError('device changed')
        samples=np.asarray(audio,dtype=np.float32)
        if not len(samples) or not np.isfinite(samples).all() or float(np.max(np.abs(samples)))<0.00001:
            raise ValueError('empty/nonfinite/silent speech output')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:sf.write(stream,samples,tts.sample_rate,format='WAV',subtype='PCM_16')
        info=sf.info(str(path))
        report['wav'].append({'id':job['id'],'text':job['text'],'voice':job['voice'],'path':job['output'],
            'sha256':sha(path),'frames':info.frames,'sampleRate':info.samplerate,'duration':info.duration,
            'rms':float(np.sqrt(np.mean(samples*samples))),'gpuDevicesAfterInference':devices()})
        evidence=root/'GPU_EXECUTION.json'
        report.update(elapsedSeconds=round(time.time()-start,2),networkAttemptsBlocked=len(attempts),
            peakCudaMemoryBytes=torch.cuda.max_memory_allocated())
        evidence.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print('WAV_READY '+job['id']+' '+str(info.duration)+'s',flush=True)
    print('GPU_SYNTHESIS_COMPLETE',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',required=True);ap.add_argument('--model',required=True)
    ap.add_argument('--moss',required=True);ap.add_argument('--manifest',required=True)
    a=ap.parse_args();run(a.workspace,a.model,a.moss,a.manifest)
