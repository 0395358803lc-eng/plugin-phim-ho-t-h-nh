"""Read-only macro planner and packet selector. Never executes CLI or grants approvals.

New projects: eight macro groups M0..M7, with special-action sub-bundles isolated.
Legacy v1.10 `approvalBundles` are left untouched. Caller must persist approved
states using its own atomic checkpoint/write implementation after user events.
"""
from __future__ import annotations
import re
import json
from pathlib import Path
from collections import defaultdict

ELEVATED = (' install',' download','winget','npx ','publish','delete','remove-item','rmdir',
            'curl ','wget ','pip install','npm install','playwright install','set-executionpolicy',
            'reg add','cuda fallback','model download','get voice','openfilm get')


def safe_path(path):
    if not isinstance(path,str) or not path or any(c in path for c in ('\0','<','>')):
        return False
    unified=path.replace('\\','/')
    return not unified.startswith('/') and ':' not in unified and all(s not in ('..','') for s in unified.split('/'))


def _template_rank():
    """Get authoritative ordering of 99 templates; old work indexes can be unsorted."""
    path=Path(__file__).resolve().parents[2]/'openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json'
    spec=json.loads(path.read_text(encoding='utf-8'))
    return {packet['templateId']:position for stage in spec['stages'] for position,packet in enumerate(stage['packets'])}


def _ordered_packets(index, policy):
    stage_order={st:i for i,st in enumerate([s for m in policy['macros'] for s in m['stages']])}
    template_order=_template_rank()
    raw=index.get('packets',[])
    def sort_key(item):
        original,pkt=item
        sid=pkt.get('stageId');tid=str(pkt.get('packetId',''))[:6]
        if sid not in stage_order or tid not in template_order:
            raise ValueError('unknown stage or template')
        return stage_order[sid],template_order[tid],original
    return [p for _,p in sorted(enumerate(raw),key=sort_key)]


def _macro_of(stage, policy):
    for group in policy['macros']:
        if stage in group['stages']:
            return group['id']
    return None


def propose(index:dict,policy:dict)->list[dict]:
    """Group concrete planned packet rows across stages; split explicit special actions.

    Returns plans, never status approval. Only materialized known IDs/paths are accepted.
    Does NOT impose per-turn packet limits on approval scope; High resumes same macro.
    """
    macros={x['id']:x for x in policy['macros']}
    groups=[];current=None;seen=set()
    order={st:i for i,st in enumerate([s for m in policy['macros'] for s in m['stages']])}
    last_ord=-1
    for pkt in _ordered_packets(index, policy):
        if pkt.get('status') not in ('PLANNED','WAITING_APPROVAL'):
            continue
        pid=pkt.get('packetId');stage=pkt.get('stageId');mid=_macro_of(stage,policy)
        if not isinstance(pid,str) or not pid.startswith(f'{stage}.') or mid is None:
            raise ValueError('unknown packet ID or stage')
        if pid in seen:raise ValueError('duplicate packetId')
        seen.add(pid)
        if order[stage]<last_ord:raise ValueError('stage order reversed')
        last_ord=order[stage]
        scopes=pkt.get('scopeIds');paths=pkt.get('inputPaths',[])+pkt.get('outputPaths',[])
        commands=pkt.get('allowedCommands',[])
        if not isinstance(scopes,list) or not scopes or any(not isinstance(x,str) or not x or '<' in x or '>' in x for x in scopes):
            raise ValueError(f'{pid}: unresolved scope')
        if not all(isinstance(q,list) for q in [pkt.get('inputPaths',[]),pkt.get('outputPaths',[]),commands]) or not all(map(safe_path,paths)):
            raise ValueError(f'{pid}: invalid relative paths/commands')
        if any(not isinstance(c,str) or not c for c in commands):raise ValueError(f'{pid}: invalid command')
        risk=pkt.get('riskClass','NORMAL')
        if risk not in set(policy['specialRiskClasses']) | {'NORMAL'}:raise ValueError(f'{pid}: unknown risk')
        special=risk in policy['specialRiskClasses'] or pkt.get('specialApprovalRequired') is True
        if not special and any(any(word in (' '+c.lower()) for word in ELEVATED) for c in commands):
            raise ValueError(f'{pid}: elevated command requires isolated special approval')
        if (current is None or current['macroId']!=mid or current['specialApprovalRequired'] or special):
            current={'macroId':mid,'macroBundleId':None,'stageIds':[],'packetIds':[],
                     'scopeIds':[],'allowedPaths':[],'allowedCommands':[],
                     'riskClass':risk,'specialApprovalRequired':bool(special)}
            groups.append(current)
        if current['riskClass']!=risk: # never mix different risk classes
            current={'macroId':mid,'macroBundleId':None,'stageIds':[],'packetIds':[],
                     'scopeIds':[],'allowedPaths':[],'allowedCommands':[],
                     'riskClass':risk,'specialApprovalRequired':bool(special)}
            groups.append(current)
        if stage not in current['stageIds']:current['stageIds'].append(stage)
        current['packetIds'].append(pid)
        for field,items in [('scopeIds',scopes),('allowedPaths',paths),('allowedCommands',commands)]:
            for item in items:
                if item not in current[field]:current[field].append(item)
    counts=defaultdict(int)
    for b in groups:
        counts[b['macroId']]+=1
        b['macroBundleId']=f"{b['macroId']}.B{counts[b['macroId']]:03d}"
        b.update(status='PLANNED',presentedToUserRevision=None,planApprovalId=None,
                 acceptanceApprovalId=None,specialApprovalId=None,evidencePaths=[],inputHashes={})
    return groups


def _qc_ready(packet):
    if packet.get('status')=='SKIPPED':
        return bool(packet.get('skipReason') and packet.get('evidencePaths'))
    if packet.get('qcStatus')!='PASS' or packet.get('status') not in ('READY_FOR_REVIEW','PASS'):
        return False
    if not packet.get('evidencePaths'):return False
    outputs=packet.get('outputPaths',[])
    hashes=packet.get('outputHashes',{})
    return all(isinstance(hashes.get(x),str) and re.fullmatch(r'[0-9a-fA-F]{64}',hashes[x]) for x in outputs)


def _prior_stage_ready(index, prior_stage, owning_macro):
    s=index.get('stageStates',{}).get(prior_stage)
    if not isinstance(s,dict) or not s.get('evidencePaths'):return False
    if s.get('status')=='SKIPPED':return bool(s.get('skipReason'))
    return s.get('status') in ('PASS','QC_PASS') and s.get('qcStatus')=='PASS' and (s.get('macroId')==owning_macro or s.get('status')=='PASS')


def next_eligible_packet(index:dict, macro_bundle_id:str, policy:dict)->str|None:
    """Select only packet in already approved macro, respecting stage QC and user decisions.

    Intra-macro cross-stage dependencies can use internal QC; cross-macro needs
    actual user acceptance. Never treats a plan, log, or QC as an approval.
    """
    b=next((b for b in index.get('macroBundles',[]) if b.get('macroBundleId')==macro_bundle_id),None)
    if not b or b.get('status') not in ('APPROVED','IN_PROGRESS') or not b.get('planApprovalId'):
        return None
    owns=b.get('packetIds',[])
    pkts={p.get('packetId'):p for p in index.get('packets',[])}
    # P00–P05 is not an implied user authorization; it must be verified.
    if b.get('macroId')=='M0':
        for pre in policy['macros'][0]['preflightStages']:
            status=index.get('preflightGates',{}).get(pre,{})
            if status.get('status')!='PASS' or not status.get('evidencePaths'):
                return None
    ordered=_ordered_packets(index,policy)
    placement={p.get('packetId'):pos for pos,p in enumerate(ordered)}
    if not owns or any(i not in pkts for i in owns):return None
    if b.get('specialApprovalRequired') and (len(owns)!=1 or not b.get('specialApprovalId')):return None
    if any(pkts[i].get('status') in ('FAIL','BLOCKED','INVALIDATED') for i in owns):return None
    all_macro_stages=[s for macro in policy['macros'] for s in macro['stages']]
    for pid in owns:
        p=pkts[pid];sid=p['stageId']
        if p.get('status') not in ('PLANNED','WAITING_APPROVAL'):continue
        if sid not in b['stageIds'] or _macro_of(sid,policy)!=b.get('macroId'):return None
        if not set(p.get('inputPaths',[])+p.get('outputPaths',[])).issubset(set(b.get('allowedPaths',[]))):return None
        if not set(p.get('allowedCommands',[])).issubset(set(b.get('allowedCommands',[]))):return None
        if p.get('specialApprovalRequired') and not b.get('specialApprovalId'):return None
        # Strict chronological order for technical templates. An external macro's
        # preceding packet requires *user macro acceptance*, not internal QC.
        for preceding in ordered[:placement[pid]]:
            prev_id=preceding.get('packetId')
            if preceding.get('stageId')!=sid:continue
            if prev_id in owns:
                if not _qc_ready(preceding):return None
            elif preceding.get('status')=='SKIPPED':
                if not (preceding.get('skipReason') and preceding.get('evidencePaths')):return None
            elif preceding.get('status')!='PASS' or not preceding.get('acceptanceApprovalId'):
                return None
        # User decisions are separate gate events; one macro plan does not invent an approval.
        gate=policy.get('humanDecisionGates',{}).get(sid)
        if gate:
            decision=index.get('decisionGates',{}).get(gate,{})
            if decision.get('status')!='APPROVED' or not decision.get('approvalId') or not decision.get('evidencePaths'):
                if not (gate in policy.get('gateWaivers',{}) and decision.get('status')==policy['gateWaivers'][gate] and decision.get('evidencePaths')):
                    return None
        # Earlier stages must have internal PASS even when no explicit deps in a packet.
        for prior in all_macro_stages[:all_macro_stages.index(sid)]:
            # Conditions only enforce stages in this macro and already completed earlier macros.
            if prior not in b['stageIds'] and _macro_of(prior,policy)!=b['macroId']:
                # Current macro may start when its earlier macro groups are closed.
                earlier_groups=[x for x in index.get('macroBundles',[]) if prior in x.get('stageIds',[])]
                if not earlier_groups: # existing resume preflight stage may be recorded separately
                    if not _prior_stage_ready(index,prior,b['macroId']):return None
                elif not all(x.get('status')=='PASS' and x.get('acceptanceApprovalId') for x in earlier_groups):return None
                continue
            if prior==sid:continue
            if prior in b['stageIds'] and not _prior_stage_ready(index,prior,b['macroId']):return None
            if _macro_of(prior,policy)==b['macroId'] and prior not in b['stageIds']:
                earlier_segments=[x for x in index.get('macroBundles',[])
                                  if x.get('macroBundleId')!=b.get('macroBundleId') and
                                     prior in x.get('stageIds',[])]
                if earlier_segments and not all(x.get('status')=='PASS' and x.get('acceptanceApprovalId') for x in earlier_segments):
                    return None
                if not _prior_stage_ready(index,prior,b['macroId']):return None
        ready=True
        for dep in p.get('dependencies',[]):
            other=pkts.get(dep)
            if not other:ready=False;break
            if dep in owns:
                if not _qc_ready(other):ready=False;break
            else:
                if other.get('status') not in ('PASS','SKIPPED') or (other.get('status')=='PASS' and not other.get('acceptanceApprovalId')):
                    ready=False;break
        if ready:return pid
    return None
