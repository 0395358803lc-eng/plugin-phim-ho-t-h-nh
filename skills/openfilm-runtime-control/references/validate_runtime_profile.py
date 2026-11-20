"""Read-only validation of OpenFilm runtime capability evidence contract."""
import argparse
import json
import ntpath,re
from pathlib import Path

CAPS = ('openProject', 'inspectFrame', 'renderClip', 'openCanvas')
CAP_STATES = {'VERIFIED', 'UNVERIFIED', 'UNSUPPORTED'}

def is_inside_workspace(workspace,cwd):
    if not isinstance(workspace,str) or not isinstance(cwd,str):return False
    if not re.match(r'^[A-Za-z]:[\\/]',workspace) or not re.match(r'^[A-Za-z]:[\\/]',cwd):return False
    if '..' in cwd.replace('/','\\').split('\\'):return False
    try:return ntpath.commonpath([ntpath.normcase(ntpath.normpath(workspace)),ntpath.normcase(ntpath.normpath(cwd))])==ntpath.normcase(ntpath.normpath(workspace))
    except ValueError:return False

def relpath(x):
    return (isinstance(x, str) and bool(x) and not x.startswith(('/', '\\'))
            and ':' not in x and all(part not in ('', '..') for part in x.replace('\\', '/').split('/')))

def validate(x):
    e=[]
    if x.get('schemaVersion') != 1:e.append('schemaVersion must be 1')
    if x.get('mode') not in ('unverified', 'cli', 'desktop-ui'):e.append('invalid mode')
    if x.get('status') not in ('NOT_TESTED', 'BLOCKED', 'READY_FOR_PREVIEW', 'READY_FOR_RENDER'):e.append('invalid runtime status')
    caps=x.get('capabilities')
    if not isinstance(caps,dict):return e+['capabilities missing']
    for name in CAPS:
        c=caps.get(name)
        if not isinstance(c,dict):e.append(f'missing capability {name}');continue
        if c.get('status') not in CAP_STATES:e.append(f'invalid {name} status')
        ev=c.get('evidencePaths')
        if not isinstance(ev,list) or any(not relpath(a) for a in ev):e.append(f'invalid {name} evidence paths')
        if c.get('status')=='VERIFIED' and not ev:e.append(f'{name} VERIFIED without evidence')
    if x.get('status') in ('READY_FOR_PREVIEW', 'READY_FOR_RENDER'):
        if x.get('mode')!='cli':e.append('READY requires OpenFilm CLI mode; Desktop UI is not a fallback')
        if not x.get('approvalId'):e.append('READY without approvalId')
        if not x.get('deviceId') or not x.get('workspace'):e.append('READY without device/workspace')
        if not x.get('openFilmVersion') or not x.get('invocationMethod'):e.append('READY without version/invocationMethod')
        if x.get('mode')=='cli' and not x.get('executablePath'):e.append('CLI READY without executablePath')
        if not is_inside_workspace(x.get('workspace'),x.get('workingDirectory')):e.append('CLI READY workingDirectory must be inside workspace')
        for name in ('openProject','inspectFrame'):
            if caps.get(name,{}).get('status')!='VERIFIED':e.append('READY requires '+name+' VERIFIED')
        if x['status']=='READY_FOR_RENDER' and caps.get('renderClip',{}).get('status')!='VERIFIED':e.append('READY_FOR_RENDER requires renderClip VERIFIED')
    return e

def check_files(x, root):
    e=[];root=Path(root).resolve()
    for name in CAPS:
        for rel in x.get('capabilities',{}).get(name,{}).get('evidencePaths',[]):
            if not relpath(rel):continue
            path=(root/rel).resolve()
            if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size==0:e.append(f'{name} evidence missing/outside workspace: {rel}')
    return e

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('profile',type=Path);p.add_argument('--workspace',type=Path)
    a=p.parse_args();x=json.loads(a.profile.read_text(encoding='utf-8'))
    issues=validate(x)+(check_files(x,a.workspace) if a.workspace else [])
    print(json.dumps({'status':'PASS' if not issues else 'FAIL','errors':issues},ensure_ascii=False,indent=2))
    raise SystemExit(2 if issues else 0)
