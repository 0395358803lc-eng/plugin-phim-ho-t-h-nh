"""Pure, read-only planner/selector. No network, remote execution, file writes or approvals."""
from __future__ import annotations
from collections import defaultdict

SPECIAL={'PACKAGE_INSTALL','MODEL_DOWNLOAD','BROWSER_DOWNLOAD','SYSTEM_CHANGE',
         'GPU_TO_CPU_FALLBACK','VOICE_CLONING','EXTERNAL_PROVIDER','PAID_ACTION',
         'DELETE','PUBLISH','OUT_OF_SCOPE'}


def _valid_paths(paths:list[str])->bool:
    return isinstance(paths,list) and all(isinstance(p,str) and p and not p.startswith(('/', '\\'))
      and ':' not in p and '..' not in p.replace('\\','/').split('/') and '<' not in p and '>' not in p for p in paths)


def propose(index:dict,policy:dict)->list[dict]:
    """Suggest bounded groups from materialized packets; NEVER grants permission.
    Only verifiable concrete IDs/paths, no inferred extra work. Order follows index.
    Special packet/risk always one independent bundle.
    """
    stages={x['stageId']:x for x in policy['stages']}
    groups=[];current=None
    for p in index.get('packets',[]):
        if p.get('status') not in ('PLANNED','WAITING_APPROVAL'):
            continue
        sid=p.get('stageId');pid=p.get('packetId')
        if sid not in stages or not isinstance(pid,str) or not pid.startswith(sid+'.'):
            raise ValueError('packet missing verified stage/id')
        scope=p.get('scopeIds');paths=p.get('outputPaths',[]);inputs=p.get('inputPaths',[])
        if not isinstance(scope,list) or not scope or not _valid_paths(paths) or not _valid_paths(inputs):
            raise ValueError(f'{pid}: no concrete scope or safe paths')
        if any('<' in str(x) or '>' in str(x) or not x for x in scope):raise ValueError(f'{pid}: unresolved scope')
        risk=p.get('riskClass','NORMAL')
        if risk not in SPECIAL | {'NORMAL'}:raise ValueError(f'{pid}: unknown riskClass')
        special=risk in SPECIAL or bool(p.get('specialApprovalRequired'))
        commands=p.get('allowedCommands',[])
        if not isinstance(commands,list):raise ValueError(f'{pid}: commands are not listed')
        # Do not infer safety for actions the plan did not classify.
        if not special and any(any(k in c.lower() for k in (' install',' download','winget','npx ','publish','delete','remove-item','rmdir','cuda fallback')) for c in commands):
            raise ValueError(f'{pid}: elevated command without special approval')
        cap=stages[sid]['maxInternalPacketsPerTurn']
        cat=p.get('bundleCategory','ordinary')
        need_new=(current is None or current['stageId']!=sid or current['_category']!=cat or
                  current['_riskClass']!=risk or current['specialApprovalRequired'] or special or
                  len(current['packetIds'])>=cap)
        if need_new:
            current={'stageId':sid,'packetIds':[],'scopeIds':[],'allowedPaths':[],
                     'allowedCommands':[],'riskClass':risk,'specialApprovalRequired':special,
                     '_category':cat,'_riskClass':risk}
            groups.append(current)
        current['packetIds'].append(pid)
        current['scopeIds'].extend(x for x in scope if x not in current['scopeIds'])
        current['allowedPaths'].extend(x for x in paths if x not in current['allowedPaths'])
        current['allowedCommands'].extend(x for x in commands if x not in current['allowedCommands'])
    count=defaultdict(int)
    for g in groups:
        count[g['stageId']]+=1;g['bundleId']=f"{g['stageId']}.B{count[g['stageId']]:03d}"
        del g['_category'],g['_riskClass']
        g['status']='PLANNED'
        g['presentedToUserRevision']=None
        g['planApprovalId']=None
        g['evidencePaths']=[]
        g['inputHashes']={}  # must be populated from actual files before showing or allowing approval
    return groups


def next_eligible_packet(index:dict,bundle_id:str)->str|None:
    """Return only next task inside an already-approved bundle with satisfied deps.
    Intra-bundle READY_FOR_REVIEW+QC PASS is sufficient for dependent internal work;
    cross-bundle requires PASS and user acceptance. Does not execute or accept.
    """
    b=next((b for b in index.get('approvalBundles',[]) if b.get('bundleId')==bundle_id),None)
    if not b or b.get('status') not in ('APPROVED','IN_PROGRESS') or not b.get('planApprovalId'):
        return None
    packets={p.get('packetId'):p for p in index.get('packets',[])}
    own=set(b.get('packetIds',[]))
    if not own or any(pid not in packets for pid in own):return None
    if b.get('specialApprovalRequired') and (len(own)!=1 or not b.get('specialApprovalId')):return None
    if any(packets[pid].get('status') in ('FAIL','BLOCKED','INVALIDATED') for pid in own):return None
    paths=set(b.get('allowedPaths',[])); cmds=set(b.get('allowedCommands',[]))
    for pid in b['packetIds']:
        p=packets[pid]
        if p.get('stageId')!=b.get('stageId'):return None
        if p.get('status') not in ('PLANNED','WAITING_APPROVAL'):continue
        if not set(p.get('outputPaths',[])).issubset(paths) or not set(p.get('allowedCommands',[])).issubset(cmds):return None
        if p.get('specialApprovalRequired') and not b.get('specialApprovalId'):return None
        ready=True
        for dep in p.get('dependencies',[]):
            prior=packets.get(dep)
            if not prior:ready=False;break
            if dep in own:
                if prior.get('status') not in ('PASS','SKIPPED') and not (prior.get('status')=='READY_FOR_REVIEW' and prior.get('qcStatus')=='PASS'):
                    ready=False;break
            elif prior.get('status') not in ('PASS','SKIPPED') or (prior.get('status')=='PASS' and not prior.get('acceptanceApprovalId')):
                ready=False;break
        if ready:return pid
    return None
