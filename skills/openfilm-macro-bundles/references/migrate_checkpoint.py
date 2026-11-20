"""Explicit, non-destructive migration. Originals and old approval records survive."""
import copy
import json
import os
import uuid
from pathlib import Path
import importlib.util

spec=importlib.util.spec_from_file_location('finish_first',Path(__file__).with_name('finish_first.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def migrate(path, workspace, *, copy_to=None):
    path=Path(path).resolve();root=Path(workspace).resolve()
    if not path.is_relative_to(root):raise ValueError('checkpoint outside workspace')
    original=path.read_bytes();state=json.loads(original)
    if f.enabled(state):return state, None
    if f.checkpoint_kind(state) in ('UNSUPPORTED_MODE','UNSUPPORTED_VERSION'):
        raise ValueError('unsupported checkpoint format; no migration performed')
    if state.get('schemaVersion')!=1 or type(state.get('stateRevision',0)) is not int:
        raise ValueError('unsupported schema/revision; no migration performed')
    if state.get('workspace') and Path(state['workspace']).resolve()!=root:raise ValueError('workspace mismatch')
    target=Path(copy_to).resolve() if copy_to is not None else path
    if copy_to is not None and (target.exists() or not target.parent.is_dir()):
        raise ValueError('migration copy needs a new file in an existing destination directory')
    backup=target.with_name(target.name+'.pre-1.14.'+uuid.uuid4().hex+'.bak')
    with backup.open('xb') as stream:
        stream.write(original);stream.flush();os.fsync(stream.fileno())
    result=copy.deepcopy(state)
    if not result.get('workspace'):result['workspace']=str(root)
    def walk(value):
        if isinstance(value,dict):
            status=value.get('status')
            if status in f.LEGACY_READY|f.READY|{'BLOCKED','VISUAL_BLOCKED'}:
                value.setdefault('legacyStatus',status)
                if status in f.LEGACY_READY|f.READY:
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
        if bundle.get('planApprovalId') or bundle.get('approvedScopeSha256'):
            # Preserve the historical permission and state, but do not make it executable.
            bundle['scopeRevalidationRequired']=True
    result.update(productionMode=f.MODE,pluginVersion='1.14.1',stateRevision=state.get('stateRevision',0)+1)
    result['migration']={'backup':str(backup),'sourceSha256':f.digest(backup),'sourceVersion':state.get('pluginVersion'),
                         'sourceKind':f.checkpoint_kind(state),'requiresScopeRevalidation':True}
    temp=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp')
    with temp.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);stream.flush();os.fsync(stream.fileno())
    if path.read_bytes()!=original:raise ValueError('checkpoint changed concurrently; backup retained')
    if copy_to is None:os.replace(temp,target)
    else:
        # Same-directory hard link publishes the complete file atomically and
        # fails if another writer created target; never overwrites the source.
        os.link(temp,target);temp.unlink()
    return result,backup

def restore_existing_approval(state,bundle_id,approval_id):
    """Reuse a retained real user receipt; migration alone cannot grant execution.

No caller-supplied new event: the exact original scope must already be present
in retained history. An absent receipt needs host/user clarification once, not
fabricated permission or per-packet reapproval.
"""
    if not f.enabled(state) or not state.get('migration'):raise ValueError('migrated checkpoint required')
    result=copy.deepcopy(state)
    b=next((b for b in result.get('macroBundles',[]) if b.get('macroBundleId')==bundle_id),None)
    if not b or b.get('planApprovalId')!=approval_id:raise ValueError('existing plan approval mismatch')
    history=state.get('eventHistory',[])+state.get('approvalHistory',[])
    matches=[e for e in history if e.get('approvalId')==approval_id and f.user_event(e) and
             e.get('action') in ('APPROVE_MACRO','APPROVE_PRODUCTION')]
    if len(matches)!=1:raise ValueError('unambiguous original user approval receipt required')
    event=matches[0]
    if any(event.get(k)!=state.get(k) for k in ('deviceId','workspace','filmId')):
        raise ValueError('original approval identity mismatch')
    shown=event.get('bundles',{}).get(bundle_id,{}) if event['action']=='APPROVE_PRODUCTION' else event
    if event['action']=='APPROVE_MACRO' and event.get('macroBundleId')!=bundle_id:raise ValueError('wrong bundle receipt')
    fields=('macroId','macroIds','stageIds','packetIds','scopeIds','allowedPaths','allowedCommands','riskClass','inputHashes','specialApprovalRequired')
    if any(shown.get(k)!=b.get(k) for k in fields):raise ValueError('original approved scope differs')
    if b.get('status') not in ('APPROVED','IN_PROGRESS'):
        raise ValueError('original scope is not resumable')
    for path,expected in b.get('inputHashes',{}).items():
        errors=f.check_file(state['workspace'],path,expected)
        if errors:raise ValueError('; '.join(errors))
    b['approvedScopeSha256']=f.scope_digest(b);b['scopeRevalidationRequired']=False
    result.setdefault('migrationRevalidations',[]).append({'macroBundleId':bundle_id,'originalApprovalId':approval_id})
    result['stateRevision']+=1
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('checkpoint');ap.add_argument('--workspace',required=True)
    ap.add_argument('--copy-to',help='New output file in an explicitly chosen existing directory; preserve source checkpoint and workspace identity')
    args=ap.parse_args();state,backup=migrate(args.checkpoint,args.workspace,copy_to=args.copy_to)
    print(json.dumps({'backup':str(backup),'stateRevision':state['stateRevision']}))
