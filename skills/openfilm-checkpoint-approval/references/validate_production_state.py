"""Read-only structural gate validator. Does not validate existence of media files."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import importlib.util as _iu
_spec=_iu.spec_from_file_location('validate_completion',Path(__file__).resolve().parents[2]/'openfilm-macro-bundles/references/validate_completion.py')
_vc=_iu.module_from_spec(_spec);_spec.loader.exec_module(_vc)


STATES={'NOT_STARTED','PLANNED','WAITING_APPROVAL','IN_PROGRESS','READY_FOR_REVIEW','PASS','FAIL','BLOCKED','SKIPPED','INVALIDATED'}
APPROVAL={'NOT_REQUESTED','PENDING','APPROVED','REJECTED'}
QC={'NOT_TESTED','PASS','FAIL','BLOCKED','NOT_APPLICABLE'}
SKIPPABLE={'P06','P12','P13','P14','P15'}
IDS=[f'P{i:02d}' for i in range(6,22)]
MACRO_STAGE_MAP={'P06':'M0','P07':'M1','P08':'M1','P09':'M1',
                 'P10':'M2','P11':'M2','P12':'M3','P13':'M3',
                 'P14':'M4','P15':'M4','P16':'M4','P17':'M5',
                 'P18':'M5','P19':'M6','P20':'M6','P21':'M7'}

def internal_macro_gate(stage, status):
    """Technical QC marker only: never claims a user accepted the stage.

    Requires already-approved macro plan and evidence. Final P21 requires human
    acceptance, regardless of QC or macro plan approval.
    """
    if stage.get('id')=='P21':return False
    gate=stage.get('macroInternalGate')
    plan=stage.get('planApproval',{})
    if not isinstance(gate,dict) or not isinstance(plan,dict):return False
    if gate.get('macroId')!=MACRO_STAGE_MAP.get(stage['id']):return False
    if plan.get('status')!='APPROVED' or not plan.get('approvalId') or gate.get('planApprovalId')!=plan.get('approvalId'):return False
    if gate.get('qcStatus')!='PASS' or not gate.get('evidencePaths'):return False
    if not set(gate['evidencePaths']).issubset(set(stage.get('evidence',[]))):return False
    if status=='PASS' and stage.get('qcStatus')!='PASS':return False
    if status=='SKIPPED' and (not stage.get('skipReason') or stage.get('qcStatus') not in ('PASS','NOT_APPLICABLE')):return False
    return True


def validate(state:dict)->list[str]:
    if _vc.f.enabled(state):return _vc.validate_stages(state)
    errors=[]
    if state.get('schemaVersion')!=1:
        errors.append('schemaVersion must equal 1')
    stages=state.get('stages')
    if not isinstance(stages,list):
        return errors+['stages must be a list']
    if [s.get('id') for s in stages if isinstance(s,dict)]!=IDS or len(stages)!=16:
        errors.append('stages must exactly list P06..P21 in order')
    prior_valid=True
    for s in stages:
        if not isinstance(s,dict):
            errors.append('stage must be object')
            continue
        stage=s.get('id')
        status=s.get('status')
        if status not in STATES:
            errors.append(f'{stage} unknown status {status}')
        approvals=[]
        for approval_name in ['planApproval','acceptanceApproval']:
            v=s.get(approval_name)
            if not isinstance(v,dict) or v.get('status') not in APPROVAL:
                errors.append(f'{stage} invalid {approval_name}')
            else:
                approvals.append(v)
                if v['status']=='APPROVED' and not all(v.get(key) for key in ['approvalId','scope','source','at']):
                    errors.append(f'{stage} {approval_name} approved without audit fields')
        if s.get('qcStatus') not in QC:
            errors.append(f'{stage} invalid qcStatus')
        if not isinstance(s.get('evidence'),list):
            errors.append(f'{stage} evidence must be list')
        if not isinstance(s.get('workUnits'),list):
            errors.append(f'{stage} workUnits must be list')
        if status in ['PASS','SKIPPED'] and not prior_valid:
            errors.append(f'{stage} completed before previous stage complete')
        if status == 'PASS':
            if not isinstance(s.get('evidence'),list) or not s['evidence']:
                errors.append(f'{stage} PASS without evidence')
            if s.get('qcStatus')!='PASS':
                errors.append(f'{stage} PASS without QC PASS')
            if any(a.get('status')!='APPROVED' for a in approvals):
                # Internal macro QC is *not* a user acceptance. It is allowed only
                # when the macro plan was user-approved and QC evidence is present.
                if not internal_macro_gate(s,'PASS'):
                    # Keep v1.5 legacy P07 read-only plan exception.
                    if stage != 'P07' or not approvals or approvals[-1].get('status')!='APPROVED':
                        errors.append(f'{stage} PASS without approvals')
            for u in s.get('workUnits',[]) if isinstance(s.get('workUnits'),list) else []:
                if not isinstance(u,dict) or (
                        u.get('status') not in ('PASS','SKIPPED') and not (
                            internal_macro_gate(s,'PASS') and u.get('status')=='READY_FOR_REVIEW' and
                            u.get('qcStatus')=='PASS' and u.get('qcEvidence'))):
                    errors.append(f'{stage} has incomplete work unit')
        if status=='SKIPPED':
            if stage not in SKIPPABLE:
                errors.append(f'{stage} cannot be skipped')
            if not s.get('skipReason'):
                errors.append(f'{stage} SKIPPED without reason')
            if not s.get('evidence'):
                errors.append(f'{stage} SKIPPED without evidence')
            if len(approvals)<2 or approvals[-1].get('status')!='APPROVED':
                if not internal_macro_gate(s,'SKIPPED'):
                    errors.append(f'{stage} SKIPPED without acceptance')
        prior_valid=status in ('PASS','SKIPPED')
    return errors

def validate_files(state:dict,workspace:Path)->list[str]:
    """Optional file/hash check. No media playback or audio review is done."""
    if _vc.f.enabled(state):return _vc.validate_stages({**state,'workspace':str(workspace.resolve())})
    import hashlib
    issues=[]
    root=workspace.resolve()
    for stage in state.get('stages',[]):
        if stage.get('status') not in ('PASS','SKIPPED'):
            continue
        stage_id=stage.get('id','?')
        paths=[('evidence',x,None) for x in stage.get('evidence',[])]
        for unit in stage.get('workUnits',[]):
            if not isinstance(unit,dict) or unit.get('status') not in ('PASS','SKIPPED'):
                continue
            for output in unit.get('outputs',[]):
                if isinstance(output,dict):
                    paths.append(('output',output.get('path'),output.get('sha256')))
            paths.extend(('qcEvidence',x,None) for x in unit.get('qcEvidence',[]))
        for kind,raw,expected_sha in paths:
            if not isinstance(raw,str) or not raw or raw.startswith(('\\','/')) or ':' in raw or '..' in raw.replace('\\','/').split('/'):
                issues.append(f'{stage_id} invalid {kind} path: {raw!r}')
                continue
            candidate=(root / raw.replace('\\','/')).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                issues.append(f'{stage_id} missing/outside workspace {kind}: {raw}')
                continue
            if candidate.stat().st_size == 0:
                issues.append(f'{stage_id} empty {kind}: {raw}')
            if expected_sha:
                got=hashlib.sha256(candidate.read_bytes()).hexdigest()
                if got!=expected_sha:
                    issues.append(f'{stage_id} sha256 mismatch: {raw}')
    if any(s.get('id')=='P21' and s.get('status')=='PASS' for s in state.get('stages',[])):
        master=root/'renders/master/FINAL_MASTER.mp4'
        if not master.is_file() or master.stat().st_size == 0:
            issues.append('P21 missing/nonempty FINAL_MASTER.mp4')
    return issues

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('state_file',type=Path)
    ap.add_argument('--check-files',type=Path,metavar='WORKSPACE',help='Verify referenced evidence/output files and recorded SHA256 within WORKSPACE')
    ns=ap.parse_args()
    status=json.loads(ns.state_file.read_text(encoding='utf-8'))
    result=validate(status)
    if ns.check_files is not None:
        result.extend(validate_files(status,ns.check_files))
    print(json.dumps({'result':'PASS' if not result else 'FAIL','errors':result},indent=2,ensure_ascii=False))
    raise SystemExit(0 if not result else 2)
