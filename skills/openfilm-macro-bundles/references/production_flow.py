"""Finish First scheduler and approval validation. Read-only except apply_event copy."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path

def load(name):
    spec=importlib.util.spec_from_file_location(name, Path(__file__).with_name(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

f=load('finish_first')

def next_packet(index, bundle_id, policy, ordered):
    if not f.enabled(index):return None
    bundle=next((b for b in index.get('macroBundles',[]) if b.get('macroBundleId')==bundle_id),None)
    if not bundle or bundle.get('status') not in ('APPROVED','IN_PROGRESS') or not f.authorized(bundle):
        return None
    root=index.get('workspace'); rows={p['packetId']:p for p in ordered}
    if len(rows)!=len(ordered):return None
    owns=bundle.get('packetIds',[])
    if not owns or any(pid not in rows for pid in owns):return None
    for pre in policy['macros'][0]['preflightStages']:
        gate=index.get('preflightGates',{}).get(pre,{})
        if gate.get('status') not in ('PASS','OUTPUT_READY') or not gate.get('evidencePaths'):return None
        if any(f.check_file(root,p) for p in gate['evidencePaths']):return None
    for packet in ordered:
        pid=packet['packetId']
        if pid not in owns:continue
        if packet.get('status') not in ('PLANNED','WAITING_APPROVAL'):continue
        if packet.get('stageId') not in bundle.get('stageIds',[]):return None
        if f.packet_scope_errors(packet,bundle,policy):return None
        stage_order=[s for m in policy['macros'] for s in m['stages']]
        for sid in stage_order[:stage_order.index(packet['stageId'])]:
            if sid in ('P18','P20'):continue  # diagnostics and post-delivery feedback never gate V01
            stage_packets=[p for p in ordered if p.get('stageId')==sid]
            if not stage_packets and f.completion_errors(index.get('stageStates',{}).get(sid,{}),root,legacy=True):
                return None
        # All materialized preceding work must have actual usable output or a reasoned skip.
        for prior in ordered[:ordered.index(packet)]:
            if prior.get('stageId') in ('P18','P20') and not prior.get('requiredForOutput',False):continue
            if f.completion_errors(prior,root,legacy=True):return None
        for dep in packet.get('dependencies',[]):
            if dep not in rows or f.completion_errors(rows[dep],root,legacy=True):return None
        # Check every input immediately before scheduling, including products made since approval.
        for path in packet.get('inputPaths',[]):
            producers=[p for p in ordered[:ordered.index(packet)] if path in p.get('outputPaths',[])]
            expected=(producers[-1].get('outputHashes',{}).get(path) if producers else bundle.get('inputHashes',{}).get(path))
            if not expected or f.check_file(root,path,expected):return None
        try:
            for path in packet.get('outputPaths',[]):f.confined(root,path)
        except ValueError:return None
        return pid
    return None

SCOPE_FIELDS=('macroId','macroIds','stageIds','packetIds','scopeIds','allowedPaths','allowedCommands','riskClass','inputHashes','specialApprovalRequired')

def validate_event(index,event,policy):
    if not f.enabled(index):return f.migration_errors(index) or ['MIGRATION_REQUIRED: legacy checkpoint cannot execute Finish First events']
    errors=[]
    action=event.get('action')
    if action not in ('APPROVE_PRODUCTION','APPROVE_MACRO','RESUME_APPROVED_MACRO','COMPLETE_MACRO',
                      'ACCEPT_MACRO','DELIVER_VIDEO','ACCEPT_VIDEO','REQUEST_REVISION'):
        return ['unknown Finish First action']
    for key in ('stateRevision','deviceId','workspace','filmId'):
        if index.get(key) is None or event.get(key)!=index.get(key):errors.append(key+' mismatch/stale')
    if type(index.get('stateRevision')) is not int:errors.append('invalid stateRevision')
    bundles=index.get('macroBundles',[])
    if len({b.get('macroBundleId') for b in bundles})!=len(bundles):errors.append('duplicate macroBundleId')
    ids=event.get('macroBundleIds',[]) if action=='APPROVE_PRODUCTION' else [event.get('macroBundleId')]
    if not ids or len(set(ids))!=len(ids):return errors+['invalid macro bundle IDs']
    rows={p.get('packetId'):p for p in index.get('packets',[])}
    if len(rows)!=len(index.get('packets',[])):errors.append('duplicate packetId')
    selected=[b for b in bundles if b.get('macroBundleId') in ids]
    if len(selected)!=len(ids):return errors+['unknown macroBundleId']
    all_ids=[pid for b in selected for pid in b.get('packetIds',[])]
    if len(set(all_ids))!=len(all_ids):errors.append('packet assigned twice')
    root=index.get('workspace')
    mapping={s:m['id'] for m in policy['macros'] for s in m['stages']}
    if action in ('APPROVE_PRODUCTION','APPROVE_MACRO','ACCEPT_VIDEO','REQUEST_REVISION') and not f.user_event(event):
        errors.append('explicit user event with approvalId/source/at required')
    for b in selected:
        bid=b['macroBundleId']
        shown=event.get('bundles',{}).get(bid,{}) if action=='APPROVE_PRODUCTION' else event
        for key in SCOPE_FIELDS:
            if shown.get(key)!=b.get(key):errors.append(key+' mismatch')
        if b.get('riskClass') not in f.SPECIAL|{'NORMAL'}:errors.append('invalid riskClass')
        if any(mapping.get(s)!=b.get('macroId') for s in b.get('stageIds',[])):errors.append('stage outside macro policy')
        packet_ids=b.get('packetIds',[])
        if not packet_ids or any(pid not in rows for pid in packet_ids):
            errors.append('missing packet');continue
        if action in ('APPROVE_PRODUCTION','APPROVE_MACRO'):
            if b.get('status') not in ('PLANNED','WAITING_APPROVAL') or b.get('presentedToUserRevision')!=index.get('stateRevision'):
                errors.append('scope not presented/waiting')
            if action=='APPROVE_PRODUCTION' and b.get('specialApprovalRequired'):
                errors.append('special approval must be separate')
        elif not f.authorized(b):errors.append('scope changed or not approved')
        if action=='RESUME_APPROVED_MACRO' and b.get('status') not in ('APPROVED','IN_PROGRESS'):
            errors.append('macro not resumable')
        for path in b.get('allowedPaths',[]):
            try:f.confined(root,path)
            except ValueError as exc:errors.append(str(exc))
        for pid in packet_ids:
            p=rows[pid]
            if p.get('stageId') not in b.get('stageIds',[]):errors.append('packet outside stages')
            errors+=f.packet_scope_errors(p,b,policy)
            for path in p.get('inputPaths',[]):
                earlier=all_ids[:all_ids.index(pid)]
                producers=[x for x in earlier if x in rows and path in rows[x].get('outputPaths',[])]
                producer=producers[-1] if producers else None
                if producer:
                    if action in ('APPROVE_PRODUCTION','APPROVE_MACRO'):continue
                    source=rows[producer]
                    if source.get('status') not in f.READY|f.LEGACY_READY:continue
                    expected=source.get('outputHashes',{}).get(path)
                else:
                    expected=b.get('inputHashes',{}).get(path)
                    if not expected and action not in ('APPROVE_PRODUCTION','APPROVE_MACRO'):
                        prior_rows=list(rows.values())[:list(rows).index(pid)]
                        external=[x for x in prior_rows if path in x.get('outputPaths',[]) and x.get('status') in f.READY|f.LEGACY_READY]
                        if external:expected=external[-1].get('outputHashes',{}).get(path)
                if not expected:errors.append(path+': external input hash missing')
                else:errors+=f.check_file(root,path,expected)
            if action in ('COMPLETE_MACRO','ACCEPT_MACRO','DELIVER_VIDEO','ACCEPT_VIDEO','REQUEST_REVISION'):
                errors+=f.completion_errors(p,root,legacy=True)
        if action in ('DELIVER_VIDEO','ACCEPT_VIDEO','REQUEST_REVISION'):
            if b.get('macroId')!='M7':errors.append('delivery/review is only for M7')
            video=index.get('video',{})
            errors+=f.check_file(root,video.get('path'),video.get('sha256'),require_audio=video.get('requiresAudio',True))
            if not video.get('sha256'):errors.append('video checksum missing')
            if action in ('ACCEPT_VIDEO','REQUEST_REVISION') and video.get('status')!='DELIVERED_FOR_REVIEW':
                errors.append('video must be delivered before user review')
            if action=='REQUEST_REVISION' and (not event.get('feedback') or not isinstance(event.get('feedback'),list)):
                errors.append('revision feedback required')
    return errors

def apply_event(index,event,policy):
    """Return a copy; caller persists it atomically. Never manufactures a user event."""
    errors=validate_event(index,event,policy)
    if errors:raise ValueError('; '.join(errors))
    result=copy.deepcopy(index);action=event['action']
    ids=event.get('macroBundleIds',[event.get('macroBundleId')])
    for b in result['macroBundles']:
        if b['macroBundleId'] not in ids:continue
        if action in ('APPROVE_PRODUCTION','APPROVE_MACRO'):
            b.update(status='APPROVED',planApprovalId=event['approvalId'],approvedScopeSha256=f.scope_digest(b))
            b.pop('scopeRevalidationRequired',None)
            for p in result['packets']:
                if p['packetId'] in b['packetIds']:p['planApprovalId']=event['approvalId']
        elif action in ('COMPLETE_MACRO','ACCEPT_MACRO'):b['status']='OUTPUT_READY'
        elif action=='DELIVER_VIDEO':
            b['status']='DELIVERED_FOR_REVIEW';result['video']['status']='DELIVERED_FOR_REVIEW'
        elif action in ('ACCEPT_VIDEO','REQUEST_REVISION'):
            status='USER_ACCEPTED' if action=='ACCEPT_VIDEO' else 'REVISION_REQUESTED'
            result['video']['status']=status;b['status']=status
            result['video']['userReviewEvent']=copy.deepcopy(event)
    result.setdefault('eventHistory',[]).append(copy.deepcopy(event))
    result['stateRevision']+=1
    return result
