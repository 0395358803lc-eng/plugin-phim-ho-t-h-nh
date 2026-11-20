"""Read-only VieNeu source-lock contract, no provider calls or model loading."""
import argparse,json
from pathlib import Path

def relpath(x):
 return isinstance(x,str) and bool(x) and not x.startswith(('/','\\')) and ':' not in x and '..' not in x.replace('\\','/').split('/')

def validate(x,gpu=None):
 e=[]
 if x.get('schemaVersion')!=1:e.append('schemaVersion must be 1')
 source=x.get('source'); backend=x.get('backend')
 if source not in ('none','vieneu-local','alternate-approved'):e.append('invalid source')
 if source=='none' and backend!='none':e.append('none source requires none backend')
 if source=='vieneu-local':
  if backend not in ('cuda-pytorch','onnx-cpu'):e.append('VieNeu backend must be cuda-pytorch or onnx-cpu')
  if x.get('openFilmTtsAllowed') is not False:e.append('VieNeu lock forbids OpenFilm TTS')
  if x.get('origin')!='WAV_LOCAL':e.append('VieNeu lock must import WAV_LOCAL')
  if not relpath(x.get('gpuDecisionPath')):e.append('missing/unsafe gpuDecisionPath')
  if backend=='onnx-cpu':
   if gpu is None:e.append('CPU fallback needs GPU decision evidence')
   elif not gpu.get('cpuFallbackApprovalId') or gpu.get('selectedBackend')!='onnx-cpu' or gpu.get('gpuAssessment') not in ('GPU_UNSUPPORTED','GPU_INSUFFICIENT','GPU_FAILED'):
    e.append('CPU fallback without approved GPU failure')
  if gpu is not None and backend=='cuda-pytorch' and gpu.get('selectedBackend') != 'cuda-pytorch':e.append('CUDA lock mismatch GPU decision')
 if source=='alternate-approved' and not x.get('alternateProviderApprovalId'):e.append('alternate provider requires approval')
 if source!='alternate-approved' and x.get('openFilmTtsAllowed') is True:e.append('OpenFilm provider not allowed without alternate approval')
 if x.get('status') not in ('PLANNED','LOCKED','BLOCKED'):e.append('invalid lock status')
 if x.get('status')=='LOCKED':
  if not x.get('approvalId') or not x.get('evidencePaths'):e.append('LOCKED requires approval and evidence')
  if source=='vieneu-local':
   if not x.get('modelRevision') or not x.get('voicePresetIds'):e.append('LOCKED VieNeu requires model revision and preset voices')
   if gpu is None:e.append('LOCKED VieNeu requires GPU decision file')
   elif backend=='cuda-pytorch' and (gpu.get('gpuAssessment')!='GPU_RUNTIME_PASS' or not gpu.get('runtimeGpuWavEvidence')):
    e.append('LOCKED VieNeu GPU requires GPU_RUNTIME_PASS + WAV evidence')
 if not isinstance(x.get('evidencePaths'),list) or any(not relpath(a) for a in x['evidencePaths']):e.append('invalid evidencePaths')
 return e

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('lock',type=Path);p.add_argument('--gpu-decision',type=Path)
 a=p.parse_args();x=json.loads(a.lock.read_text(encoding='utf8'))
 gpu=json.loads(a.gpu_decision.read_text(encoding='utf8')) if a.gpu_decision else None
 issues=validate(x,gpu)
 print(json.dumps({'status':'PASS' if not issues else 'FAIL','errors':issues},ensure_ascii=False,indent=2));raise SystemExit(bool(issues)*2)
