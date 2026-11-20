"""Shared state validation for technical completion, independent of QC tables."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('finish_first',Path(__file__).with_name('finish_first.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def validate_packets(index,definitions=None):
    errors=[];root=index.get('workspace');packets=index.get('packets',[])
    if index.get('schemaVersion')!=1:errors.append('schemaVersion must be 1')
    if type(index.get('stateRevision')) is not int:errors.append('stateRevision invalid')
    if not isinstance(packets,list):return errors+['packets must be list']
    known={p['templateId'] for s in definitions['stages'] for p in s['packets']} if definitions else None
    ids=set();rows={p.get('packetId'):p for p in packets if isinstance(p,dict)}
    for p in packets:
        if not isinstance(p,dict):errors.append('packet not object');continue
        pid=p.get('packetId')
        if not isinstance(pid,str) or not __import__('re').fullmatch(r'P(?:0[6-9]|1[0-9]|2[01])\.\d{2}(?:\.[A-Za-z0-9_-]+)*',pid):
            errors.append('invalid packetId');continue
        if pid in ids:errors.append('duplicate packetId')
        ids.add(pid)
        if known and pid[:6] not in known:errors.append('unknown template')
        if p.get('stageId')!=pid[:3]:errors.append('stage mismatch')
        if p.get('status') not in f.STATES:errors.append('unknown status')
        for path in p.get('inputPaths',[])+p.get('outputPaths',[]):
            try:f.confined(root,path)
            except ValueError as exc:errors.append(str(exc))
        if p.get('status') in f.READY|f.LEGACY_READY|{'SKIPPED'}:
            errors.extend(f'{pid}: {e}' for e in f.completion_errors(p,root,legacy=True))
            if p.get('status')!='SKIPPED' and not p.get('planApprovalId'):errors.append(pid+' without plan approval')
            for dep in p.get('dependencies',[]):
                if dep not in rows or f.completion_errors(rows[dep],root,legacy=True):errors.append(pid+' dependency incomplete')
        if p.get('status')=='USER_ACCEPTED' and not f.user_event(p.get('userReviewEvent',{})):
            errors.append(pid+' without actual user acceptance')
    assigned=set();bids=set()
    for b in index.get('macroBundles',[]):
        bid=b.get('macroBundleId')
        mapping={'M0':{'P06'},'M1':{'P07','P08','P09'},'M2':{'P10','P11'},'M3':{'P12','P13'},'M4':{'P14','P15','P16'},'M5':{'P17','P18'},'M6':{'P19','P20'},'M7':{'P21'}}
        if b.get('macroId') not in mapping or any(s not in mapping.get(b.get('macroId'),set()) for s in b.get('stageIds',[])):
            errors.append('stage outside macro policy')
        if bid in bids:errors.append('duplicate macroBundleId')
        bids.add(bid)
        for pid in b.get('packetIds',[]):
            if pid in assigned:errors.append('packet assigned twice')
            assigned.add(pid)
            if pid not in rows:errors.append('unknown packet in macro');continue
            errors+=f.packet_scope_errors(rows[pid],b,{})
        if b.get('status') in {'APPROVED','IN_PROGRESS'}|f.READY and not f.authorized(b):
            errors.append('macro scope not approved or changed')
        if b.get('status') in f.READY:
            for pid in b.get('packetIds',[]):
                if pid in rows:errors+=f.completion_errors(rows[pid],root,legacy=True)
    for k in ('currentPacketId','nextPacketId'):
        if index.get(k) is not None and index[k] not in ids:errors.append(k+' unknown')
    return errors

def validate_stages(state):
    errors=[];root=state.get('workspace');stages=state.get('stages')
    if state.get('schemaVersion')!=1:errors.append('schemaVersion must equal 1')
    if not isinstance(stages,list):return errors+['stages must be list']
    if [s.get('id') for s in stages]!=[f'P{i:02d}' for i in range(6,22)]:errors.append('stages must exactly list P06..P21 in order')
    done=set()
    for s in stages:
        sid=s.get('id');status=s.get('status')
        if status not in f.STATES:errors.append(f'{sid} unknown status')
        if status=='SKIPPED':
            if sid not in {'P06','P12','P13','P14','P15','P18','P20'}:errors.append(f'{sid} cannot be skipped')
            if not s.get('skipReason'):errors.append(f'{sid} SKIPPED without reason')
            else:done.add(sid)
        elif status in f.READY|f.LEGACY_READY:
            dependencies=s.get('dependsOn',[f'P{int(sid[1:])-1:02d}'] if sid!='P06' else [])
            if sid=='P19':dependencies=['P17']
            if sid=='P21':dependencies=['P19']
            if not set(dependencies).issubset(done):errors.append(f'{sid} completed before previous stage complete')
            plan=s.get('planApproval',{})
            if plan.get('status')!='APPROVED' or not all(plan.get(k) for k in ('approvalId','source','at','scope')):
                errors.append(f'{sid} without execution approval')
            errors.extend(f'{sid}: {e}' for e in f.completion_errors(s,root,legacy=True))
            for unit in s.get('workUnits',[]):errors+=f.completion_errors(unit,root,legacy=True)
            done.add(sid)
        if status=='USER_ACCEPTED' and not f.user_event(s.get('userReviewEvent',{})):
            errors.append(f'{sid} without actual user acceptance')
        if sid=='P21' and status in f.READY|f.LEGACY_READY:
            video=state.get('video',{})
            if not video.get('sha256'):errors.append('P21 video checksum missing')
            errors+=f.check_file(root,video.get('path'),video.get('sha256'),require_audio=video.get('requiresAudio',True))
    return errors
