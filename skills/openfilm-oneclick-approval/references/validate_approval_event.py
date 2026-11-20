"""Read-only check of a user-initiated one-click decision against current packet state.
It does NOT execute actions, grant permissions, or verify that a chat click occurred.
An agent must establish that the event came from the latest actual user interaction.
"""
from __future__ import annotations
import json, argparse
from pathlib import Path

BUNDLE_ACTIONS = {'APPROVE_BUNDLE','ACCEPT_BUNDLE','ACCEPT_AND_APPROVE_NEXT_BUNDLE','RESUME_APPROVED_BUNDLE','APPROVE_BUNDLE_REPAIR'}
ACTIONS = {'APPROVE_EXECUTE','ACCEPT_AND_RUN_NEXT','ACCEPT_ONLY','APPROVE_REPAIR','RECHECK','PAUSE','DETAILS'}

def validate(index: dict, event: dict) -> list[str]:
    if index.get('productionMode')!='LEGACY_QC':
        import importlib.util
        root=Path(__file__).resolve().parents[2]/'openfilm-macro-bundles/references'
        spec=importlib.util.spec_from_file_location('production_flow',root/'production_flow.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        if not module.f.enabled(index):return module.f.migration_errors(index)
        if event.get('action') in ('VIEW_PROGRESS','VIEW_VIDEO','DETAILS','PAUSE'):
            errors=[k+' mismatch/stale' for k in ('deviceId','workspace','filmId','stateRevision') if event.get(k)!=index.get(k)]
            if event.get('action')=='VIEW_VIDEO':
                video=index.get('video',{})
                errors+=module.f.check_file(index.get('workspace'),video.get('path'),video.get('sha256'),require_audio=video.get('requiresAudio',True))
            return errors
        policy=json.loads((root/'MACRO_POLICY.json').read_text(encoding='utf-8'))
        return module.validate_event(index,event,policy)
    e=[]
    act=event.get('action')
    if act in BUNDLE_ACTIONS:
        import importlib.util
        validator=Path(__file__).resolve().parents[2]/'openfilm-batch-approval/references/validate_bundle_gate.py'
        spec=importlib.util.spec_from_file_location('vhh_bundle_gate',validator)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module.validate(index,event)
    if act not in ACTIONS:return [f'unknown action {act!r}']
    if event.get('stateRevision') != index.get('stateRevision'):
        e.append('stale stateRevision')
    for k in ('deviceId','workspace'):
        if not index.get(k) or event.get(k)!=index.get(k):e.append(f'{k} missing or mismatch')
    packets={p.get('packetId'):p for p in index.get('packets',[]) if isinstance(p,dict)}
    if act in ('PAUSE','DETAILS','RECHECK'):return e
    current=event.get('currentPacketId')
    packet=packets.get(current)
    if not packet:return e+['currentPacketId unknown']
    scope=event.get('scopeIds')
    if scope != packet.get('scopeIds'): e.append('scopeIds mismatch')
    if act=='APPROVE_EXECUTE':
        if packet.get('status') not in ('PLANNED','WAITING_APPROVAL'):e.append('packet not waiting for execution approval')
        if index.get('currentPacketId') not in (None,current):e.append('another packet active')
    elif act in ('ACCEPT_ONLY','ACCEPT_AND_RUN_NEXT'):
        if packet.get('status')!='READY_FOR_REVIEW' or packet.get('qcStatus')!='PASS':e.append('not QC PASS ready for review')
        if not packet.get('evidencePaths') or not packet.get('planApprovalId'):e.append('not enough evidence or plan approval')
        if packet.get('outputPaths') and not packet.get('outputHashes'):e.append('missing output hashes')
        if act=='ACCEPT_AND_RUN_NEXT':
            nxt=event.get('nextPacketId')
            if not nxt or nxt!=index.get('nextPacketId') or nxt not in packets:e.append('nextPacketId mismatch')
            else:
                p=packets[nxt]
                if p.get('status') not in ('PLANNED','WAITING_APPROVAL'):e.append('next packet not waiting approval')
                if event.get('nextScopeIds')!=p.get('scopeIds'):e.append('nextScopeIds mismatch')
                if p.get('presentedToUserRevision')!=index.get('stateRevision'):e.append('next packet not presented at current state revision')
                if p.get('specialApprovalRequired'):e.append('special approval cannot be combined into a normal next button')
    elif act=='APPROVE_REPAIR':
        if packet.get('status')!='FAIL' or packet.get('qcStatus')!='FAIL':e.append('not a failed packet')
        if not packet.get('issueId') or event.get('issueId')!=packet.get('issueId'):e.append('issueId mismatch')
        if not packet.get('repairPlanShown'):e.append('repair plan not shown')
    return e

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('index',type=Path);ap.add_argument('event',type=Path)
    a=ap.parse_args();i=json.loads(a.index.read_text(encoding='utf-8'));ev=json.loads(a.event.read_text(encoding='utf-8'))
    errors=validate(i,ev)
    print(json.dumps({'status':'ALLOW_FOR_AGENT_REVIEW' if not errors else 'REJECT','errors':errors},ensure_ascii=False,indent=2))
    raise SystemExit(0 if not errors else 2)
