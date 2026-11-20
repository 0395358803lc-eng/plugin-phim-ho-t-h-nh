"""Read-only bundle plan/action gate. Never grants permission or runs any command."""
from __future__ import annotations
import json,sys
from pathlib import Path

SPECIAL = {'PACKAGE_INSTALL','MODEL_DOWNLOAD','BROWSER_DOWNLOAD','SYSTEM_CHANGE',
           'GPU_TO_CPU_FALLBACK','VOICE_CLONING','EXTERNAL_PROVIDER','PAID_ACTION',
           'DELETE','PUBLISH','OUT_OF_SCOPE'}
BUNDLE_ACTIONS={'APPROVE_BUNDLE','ACCEPT_BUNDLE','ACCEPT_AND_APPROVE_NEXT_BUNDLE',
                'RESUME_APPROVED_BUNDLE','APPROVE_BUNDLE_REPAIR'}

def _safe_relative_path(p):
    return isinstance(p,str) and bool(p) and not p.startswith(('/', '\\')) and ':' not in p and '..' not in p.replace('\\','/').split('/')

def validate(index:dict, event:dict)->list[str]:
    errs=[]
    action=event.get('action')
    if action not in BUNDLE_ACTIONS:return ['unknown bundle action']
    if type(index.get('stateRevision')) is not int or event.get('stateRevision') != index['stateRevision']:
        errs.append('stale stateRevision')
    for k in ('deviceId','workspace'):
        if not index.get(k) or event.get(k)!=index.get(k):errs.append(f'{k} mismatch')
    listed_bundles=[b for b in index.get('approvalBundles',[]) if isinstance(b,dict)]
    bundle_ids=[b.get('bundleId') for b in listed_bundles]
    if len(bundle_ids)!=len(set(bundle_ids)):errs.append('duplicate bundleId')
    bundles={b.get('bundleId'):b for b in listed_bundles}
    packets={p.get('packetId'):p for p in index.get('packets',[]) if isinstance(p,dict)}
    bundle=bundles.get(event.get('bundleId'))
    if bundle is None:return errs+['bundleId unknown']
    pkt_ids=bundle.get('packetIds')
    if not isinstance(pkt_ids,list) or not pkt_ids or len(set(pkt_ids))!=len(pkt_ids):errs.append('invalid packetIds');pkt_ids=[]
    if event.get('packetIds')!=pkt_ids:errs.append('packetIds mismatch')
    if any(x not in packets for x in pkt_ids):errs.append('bundle packet missing')
    if any(packets[x].get('stageId')!=bundle.get('stageId') for x in pkt_ids if x in packets):errs.append('cross-stage packet')
    if event.get('stageId')!=bundle.get('stageId'):errs.append('stageId mismatch')
    scope=bundle.get('scopeIds')
    if event.get('scopeIds')!=scope or not isinstance(scope,list):errs.append('scopeIds mismatch')
    apaths=bundle.get('allowedPaths',[])
    if any(not _safe_relative_path(x) for x in apaths):errs.append('unsafe allowedPaths')
    if event.get('allowedPaths')!=apaths:errs.append('allowedPaths mismatch')
    cmds=bundle.get('allowedCommands',[])
    if event.get('allowedCommands')!=cmds or not isinstance(cmds,list):errs.append('allowedCommands mismatch')
    if bundle.get('riskClass') not in SPECIAL | {'NORMAL'}:errs.append('invalid riskClass')
    if event.get('riskClass')!=bundle.get('riskClass'):errs.append('riskClass mismatch')
    if event.get('inputHashes')!=bundle.get('inputHashes'):errs.append('inputHashes mismatch')
    for pid in pkt_ids:
        packet=packets.get(pid)
        if not packet:continue
        if not set(packet.get('scopeIds',[])).issubset(set(bundle.get('scopeIds',[]))):
            errs.append('bundle omits packet scope')
        if not set(packet.get('outputPaths',[])).issubset(set(bundle.get('allowedPaths',[]))):
            errs.append('bundle omits packet outputPaths')
        if not set(packet.get('allowedCommands',[])).issubset(set(bundle.get('allowedCommands',[]))):
            errs.append('bundle omits packet allowedCommands')

    special=bundle.get('riskClass') in SPECIAL or any(packets[x].get('specialApprovalRequired') for x in pkt_ids if x in packets)
    if special:
        if not bundle.get('specialApprovalRequired') or len(pkt_ids)!=1:errs.append('special action requires separate single-packet bundle')
        if action=='ACCEPT_AND_APPROVE_NEXT_BUNDLE':errs.append('cannot combine special approval with next bundle')
    if action=='APPROVE_BUNDLE':
        if bundle.get('status') not in ('PLANNED','WAITING_APPROVAL'):errs.append('bundle not waiting approval')
        if bundle.get('presentedToUserRevision')!=index.get('stateRevision'):errs.append('bundle not presented at current revision')
        if any(packets[x].get('status') not in ('PLANNED','WAITING_APPROVAL') for x in pkt_ids if x in packets):errs.append('packet already started or wrong status')
    if action=='RESUME_APPROVED_BUNDLE':
        if bundle.get('status') not in ('APPROVED','IN_PROGRESS') or not bundle.get('planApprovalId'):errs.append('bundle not approved for resume')
        if special and not bundle.get('specialApprovalId'):errs.append('special action has no separate approval')
    if action in ('ACCEPT_BUNDLE','ACCEPT_AND_APPROVE_NEXT_BUNDLE'):
        if bundle.get('status')!='READY_FOR_REVIEW':errs.append('bundle not review-ready')
        if not bundle.get('planApprovalId') or not bundle.get('evidencePaths'):errs.append('missing bundle plan approval or evidence')
        for x in pkt_ids:
            p=packets.get(x,{})
            if p.get('status') not in ('READY_FOR_REVIEW','SKIPPED') or p.get('qcStatus') not in ('PASS','NOT_APPLICABLE'):
                errs.append(f'packet {x} not QC ready')
            if not p.get('planApprovalId') or (p.get('status')!='SKIPPED' and not p.get('evidencePaths')):
                errs.append(f'packet {x} missing approval/evidence')
            if p.get('outputPaths') and not p.get('outputHashes'):errs.append(f'packet {x} missing hashes')
        if action=='ACCEPT_AND_APPROVE_NEXT_BUNDLE':
            next_b=bundles.get(event.get('nextBundleId'))
            if not next_b or next_b.get('status') not in ('PLANNED','WAITING_APPROVAL') or next_b.get('presentedToUserRevision')!=index.get('stateRevision'):
                errs.append('next bundle absent/not presented/not waiting')
            elif next_b.get('specialApprovalRequired') or next_b.get('riskClass') in SPECIAL or any(packets.get(x,{}).get('specialApprovalRequired') for x in next_b.get('packetIds',[])):
                errs.append('special next bundle requires separate approval')
            elif event.get('nextBundlePacketIds')!=next_b.get('packetIds') or event.get('nextBundleScopeIds')!=next_b.get('scopeIds'):
                errs.append('next bundle scope mismatch')
            elif event.get('nextBundleAllowedPaths')!=next_b.get('allowedPaths') or event.get('nextBundleAllowedCommands')!=next_b.get('allowedCommands'):
                errs.append('next bundle action/path mismatch')
            elif event.get('nextBundleRiskClass')!=next_b.get('riskClass'):
                errs.append('next bundle riskClass mismatch')
            elif event.get('nextBundleInputHashes')!=next_b.get('inputHashes'):
                errs.append('next bundle inputHashes mismatch')
    if action=='APPROVE_BUNDLE_REPAIR':
        if bundle.get('status')!='FAIL' or not bundle.get('issueIds') or event.get('issueIds')!=bundle.get('issueIds') or not bundle.get('repairPlanShown'):
            errs.append('repair plan/issues not ready')
    return errs

if __name__=='__main__':
    index=json.loads(Path(sys.argv[1]).read_text('utf-8'))
    event=json.loads(Path(sys.argv[2]).read_text('utf-8'))
    errors=validate(index,event)
    print(json.dumps({'status':'ALLOW_FOR_AGENT_REVIEW' if not errors else 'REJECT','errors':errors},ensure_ascii=False,indent=2))
    sys.exit(0 if not errors else 2)
