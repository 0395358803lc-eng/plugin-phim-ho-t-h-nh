"""Read-only exact-scope approval gate, never performs user consent or CLI action."""
from __future__ import annotations
from pathlib import Path
import importlib.util as _iu
_ffspec=_iu.spec_from_file_location('finish_first', Path(__file__).with_name('finish_first.py'))
_ff=_iu.module_from_spec(_ffspec);_ffspec.loader.exec_module(_ff)

_flowspec=_iu.spec_from_file_location('production_flow',Path(__file__).with_name('production_flow.py'))
_flow=_iu.module_from_spec(_flowspec);_flowspec.loader.exec_module(_flow)

import json,sys,re,hashlib,importlib.util

ACTIONS={'APPROVE_MACRO','RESUME_APPROVED_MACRO','ACCEPT_MACRO',
         'ACCEPT_AND_APPROVE_NEXT_MACRO','APPROVE_MACRO_REPAIR'}

def _safe_path(p):
    if not isinstance(p,str) or not p or p.startswith(('/', '\\')) or ':' in p or '<' in p or '>' in p:return False
    return all(s not in ('..','') for s in p.replace('\\','/').split('/'))

VISUAL_MACROS={'M2','M4','M5','M6','M7'}

def _validate_visual_accept(index:dict,event:dict,b:dict)->list[str]:
    """Require a fresh file-verified visual review for each mandatory macro.

    This metadata/file gate cannot authenticate model perception. The agent must
    read actual multimodal image responses before creating the receipt; never
    construct one from file names, tool logs, JSON or metrics alone.
    """
    mid=b.get('macroId')
    if mid not in VISUAL_MACROS:return []
    errors=[]
    gate=index.get('visualGates',{}).get(mid)
    targets=index.get('visualTargets',{}).get(mid)
    if not isinstance(gate,dict) or gate.get('status')!='VISUAL_PASS':return [f'{mid} mandatory visual review missing/not PASS']
    if not isinstance(targets,list) or not targets:return [f'{mid} visual target manifest missing']
    if gate.get('stateRevision')!=index.get('stateRevision'):errors.append(f'{mid} visual review stale after checkpoint revision')
    relative=gate.get('reportPath');sha=gate.get('reportSha256')
    if not _safe_path(relative):return errors+[f'{mid} unsafe visual report path']
    if not isinstance(sha,str) or not re.fullmatch(r'[0-9a-fA-F]{64}',sha):return errors+[f'{mid} visual report hash invalid']
    if event.get('visualReportSha256')!=sha:errors.append(f'{mid} visual report hash not in user acceptance event')
    root=Path(index.get('workspace','')).resolve()
    path=(root/relative.replace('\\','/')).resolve()
    if not path.is_relative_to(root) or not path.is_file():return errors+[f'{mid} actual visual report not accessible on workspace']
    try:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha.lower():
            return errors+[f'{mid} visual report hash mismatch']
        report=json.loads(path.read_text(encoding='utf-8'))
        if report.get('macroId')!=mid or report.get('filmId')!=index.get('filmId'):
            errors.append(f'{mid} visual source project mismatch')
        spec=Path(__file__).resolve().parents[2]/'openfilm-visual-inspection/references'
        loader=importlib.util.spec_from_file_location('visual_validator',spec/'validate_visual_qc.py')
        if loader is None or loader.loader is None:return errors+[f'{mid} visual validator unavailable']
        validator=importlib.util.module_from_spec(loader);loader.loader.exec_module(validator)
        config=json.loads((spec/'VISUAL_QC_POLICY.json').read_text(encoding='utf-8'))
        errors.extend(f'{mid} visual: {e}' for e in validator.validate(report,config,root,targets))
    except (OSError,ValueError,TypeError) as exc:
        errors.append(f'{mid} visual report unreadable: {exc}')
    return errors

def validate(index:dict,event:dict,policy:dict)->list[str]:
    if _ff.enabled(index):return _flow.validate_event(index,event,policy)
    err=[];action=event.get('action')
    if action not in ACTIONS:return ['unknown macro action']
    if type(index.get('stateRevision')) is not int or event.get('stateRevision')!=index.get('stateRevision'):err.append('stale stateRevision')
    for k in ('deviceId','workspace','filmId'):
        if not index.get(k) or index.get(k)!=event.get(k):err.append(f'{k} mismatch')
    bundles=index.get('macroBundles',[])
    if len([b.get('macroBundleId') for b in bundles])!=len(set(b.get('macroBundleId') for b in bundles)):err.append('duplicate macroBundleId')
    b=next((x for x in bundles if x.get('macroBundleId')==event.get('macroBundleId')),None)
    if not b:return err+['unknown macroBundleId']
    for k in ('macroId','stageIds','packetIds','scopeIds','allowedPaths','allowedCommands','riskClass','inputHashes'):
        if event.get(k)!=b.get(k):err.append(f'{k} mismatch')
    macros={m['id']:m['stages'] for m in policy['macros']}
    if b.get('macroId') not in macros or any(st not in macros.get(b.get('macroId'),[]) for st in b.get('stageIds',[])):
        err.append('macro stage outside policy')
    pkts={p.get('packetId'):p for p in index.get('packets',[])}
    packet_ids=b.get('packetIds',[])
    if not isinstance(packet_ids,list) or not packet_ids or len(packet_ids)!=len(set(packet_ids)):return err+['invalid packetIds']
    if any(i not in pkts for i in packet_ids):return err+['missing packet']
    for k in ('allowedPaths',):
        if not all(map(_safe_path,b.get(k,[]))):err.append('unsafe allowedPaths')
    if not isinstance(b.get('allowedCommands'),list):err.append('allowedCommands invalid')
    if not isinstance(b.get('inputHashes'),dict) or not all(isinstance(v,str) and re.fullmatch('[0-9a-fA-F]{64}',v) for v in b.get('inputHashes',{}).values()):err.append('inputHashes malformed')
    # Only already-existing external input files can have a pre-approval hash.
    # An input generated by a preceding packet in THIS approved macro is
    # checked against that producer's output hash after it actually runs.
    produced={path:position for position,pid in enumerate(packet_ids)
              for path in pkts[pid].get('outputPaths',[])}
    external_inputs=set()
    for position,pid in enumerate(packet_ids):
        for path in pkts[pid].get('inputPaths',[]):
            if path in produced:
                if produced[path]>=position:
                    err.append(f'{pid} derived input not produced by preceding macro packet')
            else:
                external_inputs.add(path)
    if not external_inputs.issubset(set(b.get('inputHashes',{}))):
        err.append('input hashes missing for actual external paths')
    for pid in packet_ids:
        p=pkts[pid]
        if p.get('stageId') not in b.get('stageIds',[]):err.append(f'{pid} outside stages')
        if not set(p.get('scopeIds',[])).issubset(set(b.get('scopeIds',[]))):err.append('missing packet scope')
        if not set(p.get('inputPaths',[])+p.get('outputPaths',[])).issubset(set(b.get('allowedPaths',[]))):err.append('missing packet path')
        if not set(p.get('allowedCommands',[])).issubset(set(b.get('allowedCommands',[]))):err.append('missing packet command')
    special=b.get('specialApprovalRequired') or b.get('riskClass') in policy['specialRiskClasses'] or any(pkts[x].get('specialApprovalRequired') for x in packet_ids)
    if special and b.get('specialApprovalId')!=event.get('specialApprovalId'):
        err.append('specialApprovalId mismatch')
    if special and (len(packet_ids)!=1 or not b.get('specialApprovalRequired')):err.append('special action not isolated')
    if action=='APPROVE_MACRO':
        if b.get('status') not in ('PLANNED','WAITING_APPROVAL') or b.get('presentedToUserRevision')!=index.get('stateRevision'):err.append('macro not presented/waiting')
        if any(pkts[x].get('status') not in ('PLANNED','WAITING_APPROVAL') for x in packet_ids):err.append('packet not planned')
        if special and not b.get('specialApprovalId'):err.append('special action requires separate approval')
    if action=='RESUME_APPROVED_MACRO':
        if b.get('status') not in ('APPROVED','IN_PROGRESS') or not b.get('planApprovalId'):err.append('macro not approved for resume')
        if special and not b.get('specialApprovalId'):err.append('special resume without special approval')
    if action in ('ACCEPT_MACRO','ACCEPT_AND_APPROVE_NEXT_MACRO'):
        err.extend(_validate_visual_accept(index,event,b))
        if b.get('status')!='READY_FOR_REVIEW' or not b.get('planApprovalId') or not b.get('evidencePaths'):err.append('macro not QC review-ready')
        for pid in packet_ids:
            p=pkts[pid]
            if p.get('status')=='SKIPPED' and p.get('skipReason') and p.get('evidencePaths'):continue
            if p.get('status')!='READY_FOR_REVIEW' or p.get('qcStatus')!='PASS' or not p.get('evidencePaths') or not p.get('planApprovalId'):
                err.append(f'{pid} incomplete QC')
            if any(not re.fullmatch(r'[0-9a-fA-F]{64}',p.get('outputHashes',{}).get(x,'')) for x in p.get('outputPaths',[])):
                err.append(f'{pid} output checksum missing')
        stage_states=index.get('stageStates',{})
        for sid in b.get('stageIds',[]):
            s=stage_states.get(sid,{})
            if s.get('status')=='SKIPPED' and s.get('skipReason') and s.get('evidencePaths'):continue
            if s.get('status') not in ('QC_PASS','PASS') or s.get('qcStatus')!='PASS' or not s.get('evidencePaths'):
                err.append(f'{sid} internal stage QC missing')
        if action=='ACCEPT_AND_APPROVE_NEXT_MACRO':
            n=next((x for x in bundles if x.get('macroBundleId')==event.get('nextMacroBundleId')),None)
            if not n or n.get('status') not in ('PLANNED','WAITING_APPROVAL') or n.get('presentedToUserRevision')!=index.get('stateRevision'):err.append('next macro not presented')
            elif n.get('specialApprovalRequired') or n.get('riskClass') in policy['specialRiskClasses']:
                err.append('next special action needs separate approval')
            else:
                for k in ('packetIds','scopeIds','stageIds','allowedPaths','allowedCommands','inputHashes','riskClass'):
                    if event.get('next_'+k)!=n.get(k):err.append('next_'+k+' mismatch')
    if action=='APPROVE_MACRO_REPAIR':
        if b.get('status')!='FAIL' or not b.get('repairPlanShown') or not b.get('issueIds') or event.get('issueIds')!=b.get('issueIds'):
            err.append('repair issues/plan invalid')
    return err

if __name__=='__main__':
    src=json.loads(Path(sys.argv[1]).read_text('utf-8'));ev=json.loads(Path(sys.argv[2]).read_text('utf-8'));policy=json.loads(Path(sys.argv[3]).read_text('utf-8'))
    errs=validate(src,ev,policy);print(json.dumps({'result':'ALLOW_FOR_AGENT_REVIEW' if not errs else 'REJECT','errors':errs},ensure_ascii=False,indent=2));sys.exit(0 if not errs else 2)
