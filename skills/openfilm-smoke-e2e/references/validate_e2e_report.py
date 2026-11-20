"""Read-only evidence guard for a 7s OpenFilm render smoke; no video engine execution."""
import argparse,json
from pathlib import Path

def relpath(x):
 return isinstance(x,str) and bool(x) and not x.startswith(('/','\\')) and ':' not in x and '..' not in x.replace('\\','/').split('/')

def validate(x):
 e=[]
 if x.get('schemaVersion')!=1:e.append('schemaVersion must be 1')
 if x.get('engine')!='openfilm':e.append('engine must be openfilm; Remotion cannot substitute')
 if x.get('status') not in ('NOT_TESTED','BLOCKED','FAIL','PASS'):e.append('invalid status')
 for k in ['runtimeProfilePath','mp4Path','ffprobePath','renderLogPath']:
  if not relpath(x.get(k)):e.append(f'bad {k}')
 if not isinstance(x.get('reviewEvidencePaths'),list) or any(not relpath(p) for p in x['reviewEvidencePaths']):e.append('invalid reviewEvidencePaths')
 if x.get('status')=='PASS':
  if x.get('executionMode')!='cli':e.append('E2E PASS requires OpenFilm CLI mode')
  if not relpath(x.get('cliRunEvidencePath')):e.append('E2E PASS requires CLI run evidence')
  for k in ['visualReview','audioReview','captionReview']:
   if x.get(k)!='PASS':e.append(f'PASS needs {k} PASS')
  if not x.get('planApprovalId') or not x.get('acceptanceApprovalId'):e.append('PASS needs separate plan and acceptance approvals')
  if not x.get('reviewEvidencePaths'):e.append('PASS needs actual reviewEvidencePaths')
 return e

def check_files(x,workspace):
 e=[];root=Path(workspace).resolve()
 if x.get('status')!='PASS':return e
 for field in ['runtimeProfilePath','mp4Path','ffprobePath','renderLogPath','cliRunEvidencePath']:
  path=x.get(field)
  if not relpath(path):continue
  target=(root/path).resolve()
  if not target.is_relative_to(root) or not target.is_file() or target.stat().st_size<16:e.append(f'file missing/outside workspace: {field}: {path}')
 for p in x.get('reviewEvidencePaths',[]):
  if not relpath(p):continue
  target=(root/p).resolve()
  if not target.is_relative_to(root) or not target.is_file() or not target.stat().st_size:e.append('review evidence missing: '+p)
 ff=x.get('ffprobePath')
 if relpath(ff):
  path=(root/ff).resolve()
  if path.is_file():
   try:
    probe=json.loads(path.read_text(encoding='utf-8'))
    streams=probe.get('streams',[])
    cats={s.get('codec_type') for s in streams}
    if not {'video','audio'}.issubset(cats):e.append('ffprobe does not show video + audio')
    # Don't invent codec, inspect actual values stored by ffprobe
    vs=[s for s in streams if s.get('codec_type')=='video']
    if vs and (not vs[0].get('width') or not vs[0].get('height')):e.append('ffprobe video dimensions missing')
    dur=float(probe.get('format',{}).get('duration',0))
    if not 6.5<=dur<=7.5:e.append('ffprobe duration not near 7s')
   except (ValueError,TypeError,KeyError,json.JSONDecodeError):e.append('invalid ffprobe JSON')
 return e

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workspace',required=True,type=Path);p.add_argument('--report',required=True,type=Path)
 a=p.parse_args();x=json.loads(a.report.read_text(encoding='utf8'))
 e=validate(x)+check_files(x,a.workspace)
 print(json.dumps({'status':'PASS' if not e else 'FAIL','errors':e},ensure_ascii=False,indent=2));raise SystemExit(2 if e else 0)
