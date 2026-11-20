"""Preserve delivered versions and plan only user-requested changes."""
import copy
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('finish_first',Path(__file__).with_name('finish_first.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def plan_revision(state, event):
    if event.get('action')!='REQUEST_REVISION' or not f.user_event(event) or any(event.get(k)!=state.get(k) for k in ('stateRevision','deviceId','workspace','filmId')):
        raise ValueError('current explicit user feedback required')
    video=state.get('video',{})
    if not video.get('sha256'):raise ValueError('delivered video hash required')
    if video.get('status') not in ('DELIVERED_FOR_REVIEW','REVISION_REQUESTED'):
        raise ValueError('deliver video before revisions')
    errors=f.check_file(state.get('workspace'),video.get('path'),video.get('sha256'),require_audio=video.get('requiresAudio',True))
    if errors:raise ValueError('; '.join(errors))
    feedback=event.get('feedback')
    if not isinstance(feedback,list) or not feedback:raise ValueError('feedback list required')
    for item in feedback:
        if item.get('category') not in ('scene','audio','subtitle','effect') or not item.get('targetIds') or not item.get('request'):
            raise ValueError('feedback needs category, targetIds and request')
    result=copy.deepcopy(state)
    history=result.setdefault('videoHistory',[])
    if not any(v['path']==video['path'] for v in history):history.append(copy.deepcopy(video))
    version=max([v.get('version',1) for v in history]+[video.get('version',1)])+1
    parent=Path(video['path']).parent.as_posix()
    path=(Path(parent)/f'V{version:02d}.mp4').as_posix()
    if f.confined(state['workspace'],path).exists():raise ValueError('next version already exists; do not overwrite')
    result['revisionPlan']={'feedback':copy.deepcopy(feedback),'sourceVideo':video['path'],
        'outputPath':path,'version':version,'status':'PLANNED','approvalId':event['approvalId']}
    result['video']['status']='REVISION_REQUESTED'
    result['stateRevision']+=1
    return result

def register_revision(state):
    plan=state['revisionPlan'];root=state['workspace']
    history=state.get('videoHistory',[])
    if plan.get('status')!='PLANNED' or not plan.get('approvalId'):
        raise ValueError('approved revision plan required')
    if plan.get('outputPath') in {v['path'] for v in history} or plan.get('version',0)<=max([v.get('version',1) for v in history]+[state['video'].get('version',1)]):
        raise ValueError('revision must use a new video version and path')
    for previous in state.get('videoHistory',[]):
        if f.check_file(root,previous['path'],previous['sha256']):raise ValueError('previous version changed')
    errors=f.check_file(root,plan['outputPath'],require_audio=state['video'].get('requiresAudio',True))
    if errors:raise ValueError('; '.join(errors))
    result=copy.deepcopy(state)
    result['video']={'path':plan['outputPath'],'version':plan['version'],
        'sha256':f.digest(f.confined(root,plan['outputPath'])),'requiresAudio':state['video'].get('requiresAudio',True),
        'status':'OUTPUT_READY'}
    result['revisionPlan']['status']='OUTPUT_READY';result['stateRevision']+=1
    return result
