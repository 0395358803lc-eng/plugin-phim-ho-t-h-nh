"""Validate work packet structure and user-approval gate (read only, stdlib)."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import importlib.util as _iu
_spec=_iu.spec_from_file_location('validate_completion',Path(__file__).resolve().parents[2]/'openfilm-macro-bundles/references/validate_completion.py')
_vc=_iu.module_from_spec(_spec);_spec.loader.exec_module(_vc)


STATUSES={'PLANNED','WAITING_APPROVAL','IN_PROGRESS','READY_FOR_REVIEW','PASS','FAIL','BLOCKED','SKIPPED','INVALIDATED'}
QCS={'NOT_TESTED','PASS','FAIL','BLOCKED','NOT_APPLICABLE'}

def relative_path(p):
    return isinstance(p,str) and bool(p) and not p.startswith(('/', '\\')) and ':' not in p and '..' not in p.replace('\\','/').split('/')

def validate(index, definitions=None):
    if _vc.f.enabled(index):return _vc.validate_packets(index,definitions)
    errors=[]
    if index.get('schemaVersion')!=1: errors.append('schemaVersion must be 1')
    if type(index.get('stateRevision')) is not int or index['stateRevision']<0: errors.append('stateRevision invalid')
    packets=index.get('packets')
    if not isinstance(packets,list): return errors+['packets must be list']
    known={x['templateId']:x for s in definitions.get('stages',[]) for x in s['packets']} if definitions else None
    ids=set()
    for p in packets:
        if not isinstance(p,dict):errors.append('packet not object');continue
        i=p.get('packetId')
        if not isinstance(i,str) or not re.fullmatch(r'P(?:0[6-9]|1[0-9]|2[01])\.\d{2}(?:\.[A-Za-z0-9_-]+)*',i):
            errors.append(f'invalid packetId {i}');continue
        if i in ids: errors.append(f'duplicate packetId {i}')
        ids.add(i)
        template=i[:6]
        if known is not None and template not in known:errors.append(f'unknown template {template}')
        if p.get('stageId')!=i[:3]:errors.append(f'{i} mismatched stageId')
        if p.get('status') not in STATUSES:errors.append(f'{i} invalid status')
        if p.get('qcStatus') not in QCS:errors.append(f'{i} invalid qcStatus')
        for key in ('inputPaths','outputPaths','evidencePaths'):
            if key in p and (not isinstance(p[key],list) or any(not relative_path(x) for x in p[key])):
                errors.append(f'{i} invalid {key}')
        if p.get('status')=='PASS':
            if p.get('qcStatus')!='PASS': errors.append(f'{i} PASS without QC PASS')
            if not p.get('evidencePaths'):errors.append(f'{i} PASS without evidence')
            if not p.get('acceptanceApprovalId'):errors.append(f'{i} PASS without user acceptance approval')
            if not p.get('planApprovalId'):errors.append(f'{i} PASS without plan approval')
        if p.get('status')=='READY_FOR_REVIEW' and p.get('qcStatus')!='PASS':
            errors.append(f'{i} review-ready requires QC PASS')
        if p.get('status')=='FAIL' and p.get('qcStatus')=='PASS': errors.append(f'{i} FAIL but QC PASS')
    bundles=index.get('approvalBundles',[])
    if not isinstance(bundles,list):errors.append('approvalBundles must be list');bundles=[]
    seen_bundles=set(); assigned=set()
    for bundle in bundles:
        if not isinstance(bundle,dict):errors.append('bundle not object');continue
        bid=bundle.get('bundleId')
        if not isinstance(bid,str) or not bid:errors.append('bundleId invalid');continue
        if bid in seen_bundles:errors.append(f'duplicate bundleId {bid}')
        seen_bundles.add(bid)
        pids=bundle.get('packetIds')
        if not isinstance(pids,list) or not pids or len(set(pids))!=len(pids):errors.append(f'{bid} invalid packetIds');continue
        if any(pid not in ids for pid in pids):errors.append(f'{bid} unknown packet')
        if any(pid in assigned for pid in pids):errors.append(f'{bid} packet assigned twice')
        assigned.update(pids)
        if any(not pid.startswith(str(bundle.get('stageId'))+'.') for pid in pids):errors.append(f'{bid} cross-stage packet')
        for key in ('allowedPaths','evidencePaths'):
            if any(not relative_path(v) for v in bundle.get(key,[])):
                errors.append(f'{bid} invalid {key}')
        if bundle.get('status')=='PASS':
            if not bundle.get('acceptanceApprovalId'):errors.append(f'{bid} PASS without acceptance')
            for pid in pids:
                packet=next((p for p in packets if isinstance(p,dict) and p.get('packetId')==pid),{})
                if packet.get('status') not in ('PASS','SKIPPED'):errors.append(f'{bid} PASS but internal packet incomplete')
                if packet.get('status')=='PASS' and packet.get('acceptanceApprovalId')!=bundle.get('acceptanceApprovalId'):
                    errors.append(f'{bid} internal acceptance mismatch')
    # v1.11 macro orchestration: legacy approvalBundles remain unmodified.
    # A planned macro may cross Pxx boundaries. No packet in a macro becomes
    # user-accepted until that macro's explicit user acceptance event.
    macro_stages={
      'M0':{'P06'}, 'M1':{'P07','P08','P09'}, 'M2':{'P10','P11'},
      'M3':{'P12','P13'}, 'M4':{'P14','P15','P16'}, 'M5':{'P17','P18'},
      'M6':{'P19','P20'}, 'M7':{'P21'}}
    macros=index.get('macroBundles',[])
    if not isinstance(macros,list): errors.append('macroBundles must be list');macros=[]
    seen=set();macro_assigned=set()
    for macro in macros:
        if not isinstance(macro,dict):errors.append('macro not object');continue
        bid=macro.get('macroBundleId');mid=macro.get('macroId')
        if not isinstance(bid,str) or not bid.startswith(str(mid)+'.B'):
            errors.append('invalid macroBundleId');continue
        if bid in seen:errors.append('duplicate macroBundleId')
        seen.add(bid)
        if mid not in macro_stages:errors.append(f'{bid} unknown macroId');continue
        stage_ids=macro.get('stageIds',[]);pids=macro.get('packetIds',[])
        if not isinstance(stage_ids,list) or not stage_ids or any(x not in macro_stages[mid] for x in stage_ids):
            errors.append(f'{bid} stage outside macro policy')
        if not isinstance(pids,list) or not pids or len(set(pids))!=len(pids):
            errors.append(f'{bid} invalid packet IDs');continue
        if any(pid not in ids for pid in pids):errors.append(f'{bid} unknown packet')
        if any(pid in macro_assigned for pid in pids):errors.append(f'{bid} packet assigned twice')
        macro_assigned.update(pids)
        for pid in pids:
            packet=next((p for p in packets if isinstance(p,dict) and p.get('packetId')==pid),{})
            if packet.get('stageId') not in stage_ids:errors.append(f'{bid} packet outside declared stages')
            if any(not relative_path(x) for x in packet.get('inputPaths',[])+packet.get('outputPaths',[])):
                errors.append(f'{bid} packet has unsafe paths')
        if any(not relative_path(x) for x in macro.get('allowedPaths',[])):
            errors.append(f'{bid} unsafe allowed paths')
        status=macro.get('status')
        if status in ('APPROVED','IN_PROGRESS','READY_FOR_REVIEW','PASS'):
            if not macro.get('planApprovalId'):errors.append(f'{bid} missing macro plan approval')
        if status=='PASS':
            if not macro.get('acceptanceApprovalId'):
                errors.append(f'{bid} macro PASS without user acceptance')
            for pid in pids:
                packet=next((p for p in packets if isinstance(p,dict) and p.get('packetId')==pid),{})
                if packet.get('status') not in ('PASS','SKIPPED'):
                    errors.append(f'{bid} incomplete accepted internal packet')
                if packet.get('status')=='PASS' and packet.get('acceptanceApprovalId')!=macro.get('acceptanceApprovalId'):
                    errors.append(f'{bid} packet acceptance differs from macro')
    
    for key in ('currentPacketId','nextPacketId'):
        if index.get(key) is not None and index[key] not in ids:errors.append(f'{key} does not refer to a packet')
    return errors

def check_files(index,root:Path):
    if _vc.f.enabled(index):return _vc.validate_packets({**index,'workspace':str(root.resolve())})
    import hashlib
    issues=[];root=root.resolve()
    for p in index.get('packets',[]):
        if not isinstance(p,dict) or p.get('status')!='PASS':continue
        for key in ('outputPaths','evidencePaths'):
            for name in p.get(key,[]):
                if not relative_path(name): issues.append(f'{p.get("packetId")} unsafe {key}: {name}');continue
                path=(root/name.replace('\\','/')).resolve()
                if not path.is_relative_to(root) or not path.is_file() or not path.stat().st_size:
                    issues.append(f'{p.get("packetId")} missing {key}: {name}');continue
                if key=='outputPaths':
                    expected=p.get('outputHashes',{}).get(name)
                    if expected and hashlib.sha256(path.read_bytes()).hexdigest()!=expected: issues.append(f'{p.get("packetId")} hash mismatch: {name}')
    return issues

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('index',type=Path);ap.add_argument('--definitions',type=Path);ap.add_argument('--check-files',type=Path)
    a=ap.parse_args();index=json.loads(a.index.read_text(encoding='utf-8'))
    defs=json.loads(a.definitions.read_text(encoding='utf-8')) if a.definitions else None
    errs=validate(index,defs)
    if a.check_files: errs+=check_files(index,a.check_files)
    print(json.dumps({'status':'PASS' if not errs else 'FAIL','errors':errs},indent=2,ensure_ascii=False))
    raise SystemExit(0 if not errs else 2)
