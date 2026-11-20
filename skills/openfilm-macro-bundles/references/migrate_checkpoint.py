"""Explicit, non-destructive migration. Originals and old approval records survive."""
import copy
import json
import os
import uuid
from pathlib import Path
import importlib.util

spec=importlib.util.spec_from_file_location('finish_first',Path(__file__).with_name('finish_first.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def migrate(path, workspace):
    path=Path(path).resolve();root=Path(workspace).resolve()
    if not path.is_relative_to(root):raise ValueError('checkpoint outside workspace')
    original=path.read_bytes();state=json.loads(original)
    if state.get('productionMode')==f.MODE:return state, None
    if state.get('workspace') and Path(state['workspace']).resolve()!=root:raise ValueError('workspace mismatch')
    backup=path.with_name(path.name+'.pre-1.14.'+uuid.uuid4().hex+'.bak')
    with backup.open('xb') as stream:stream.write(original)
    result=copy.deepcopy(state);result['workspace']=str(root)
    def walk(value):
        if isinstance(value,dict):
            status=value.get('status')
            if status in f.LEGACY_READY|{'BLOCKED','VISUAL_BLOCKED'}:
                value['legacyStatus']=status
                if status in f.LEGACY_READY:
                    errors=f.completion_errors(value,root,legacy=True)
                    value['status']='FAILED_TECHNICAL' if errors else 'OUTPUT_READY'
                    if errors:value['migrationIssues']=errors
                elif status=='VISUAL_BLOCKED':value['status']='PLANNED'
                # BLOCKED remains blocked; technical cause is not guessed away.
            # Task rows only: approval records, runtime reports, logs and user data
            # can also contain status=PASS and must remain byte-for-byte meaningful.
            for child in value.get('workUnits',[]):walk(child)
        elif isinstance(value,list):
            for v in value:walk(v)
    for collection in ('packets','stages'):
        walk(result.get(collection,[]))
    for stage in result.get('stageStates',{}).values():walk(stage)
    for bundle in result.get('macroBundles',[]):
        old_status=bundle.get('status')
        if old_status in f.LEGACY_READY|{'APPROVED','IN_PROGRESS','VISUAL_BLOCKED'}:
            bundle['legacyStatus']=old_status
            bundle['status']='WAITING_APPROVAL'
            bundle['scopeRevalidationRequired']=True
    result.update(productionMode=f.MODE,pluginVersion='1.14.0',stateRevision=state.get('stateRevision',0)+1)
    result['migration']={'backup':str(backup),'sourceSha256':f.digest(backup),'requiresScopeRevalidation':True}
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with temp.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);stream.flush();os.fsync(stream.fileno())
    if path.read_bytes()!=original:raise ValueError('checkpoint changed concurrently; backup retained')
    os.replace(temp,path)
    return result,backup

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('checkpoint');ap.add_argument('--workspace',required=True)
    args=ap.parse_args();state,backup=migrate(args.checkpoint,args.workspace)
    print(json.dumps({'backup':str(backup),'stateRevision':state['stateRevision']}))
