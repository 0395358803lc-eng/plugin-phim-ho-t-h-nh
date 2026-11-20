"""Read-only contract validation for recorded OpenFilm CLI invocations. Never executes commands."""
import argparse,json,ntpath,re
from pathlib import Path

ALLOWED={'open','look','render','doctor','canvas','help'}
STATES={'NOT_TESTED','BLOCKED','FAIL','PASS'}
def absolute_win(v):
 return isinstance(v,str) and bool(re.match(r'^[A-Za-z]:[\\/]',v)) and not any(p in ('..','.') for p in v.replace('/', '\\').split('\\'))
def within(w,p):
 if not absolute_win(w) or not absolute_win(p):return False
 try:
  w=ntpath.normcase(ntpath.normpath(w));p=ntpath.normcase(ntpath.normpath(p))
  return ntpath.commonpath((w,p))==w and p!=w
 except ValueError:return False
def valid_arg(a):
 return isinstance(a,str) and bool(a) and len(a)<1024 and not any(t in a for t in ('\n','\r',';','|','&','>','<','`','$(')) and not re.search(r'(^|[/\\])\.\.($|[/\\])',a)
def relative(x):
 return isinstance(x,str) and bool(x) and not x.startswith(('/', '\\')) and ':' not in x and '..' not in x.replace('\\','/').split('/')
def validate(x):
 e=[]
 if x.get('schemaVersion')!=1:e.append('bad schemaVersion')
 if x.get('status') not in STATES:e.append('bad status')
 if x.get('command') is not None and x['command'] not in ALLOWED:e.append('bad command')
 if not isinstance(x.get('args'),list) or any(not valid_arg(a) for a in x['args']):e.append('unsafe command args')
 if x.get('status')=='PASS':
  for k in ('deviceId','workspace','cwd','executablePath','openFilmVersion','stageId','packetId','approvalId','logPath'):
   if not x.get(k):e.append('PASS missing '+k)
  if not absolute_win(x.get('executablePath')):e.append('CLI executable must be absolute Windows path')
  if not within(x.get('workspace'),x.get('cwd')):e.append('cwd must be under workspace')
  if not x.get('command') in ALLOWED:e.append('PASS invalid command')
  if x.get('exitCode')!=0:e.append('PASS requires exitCode=0')
  if not relative(x.get('logPath')):e.append('invalid logPath')
  if not isinstance(x.get('evidencePaths'),list) or not x['evidencePaths'] or any(not relative(v) for v in x['evidencePaths']):e.append('PASS needs relative evidencePaths')
  if x.get('command')=='open' and any(a.startswith(('http://','https://')) for a in x.get('args',[])):e.append('open URL not allowed in CLI automation')
  for j,a in enumerate(x.get('args',[])):
   if a=='--out':
    if j==len(x['args'])-1 or not (relative(x['args'][j+1]) or within(x['workspace'],x['args'][j+1])):e.append('--out must stay in workspace')
 return e
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('file',type=Path);args=p.parse_args();record=json.loads(args.file.read_text(encoding='utf-8'));errs=validate(record);print(json.dumps({'status':'PASS' if not errs else 'FAIL','errors':errs},ensure_ascii=False,indent=2));raise SystemExit(0 if not errs else 2)
