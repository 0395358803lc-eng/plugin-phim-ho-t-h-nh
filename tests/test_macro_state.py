"""Cross-stage internal-QC acceptance is not a forged user approval."""
import json,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def module(path,name):
    sp=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

def test_order_fixes_and_99_packet_templates():
    defs=read('skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json')
    assert sum(len(s['packets']) for s in defs['stages'])==99
    for stage,first,last in [('P06','P06.12','P06.10'),('P10','P10.06','P10.03'),('P14','P14.06','P14.05'),('P17','P17.07','P17.06')]:
        ids=[p['templateId'] for s in defs['stages'] if s['stageId']==stage for p in s['packets']]
        assert ids.index(first)<ids.index(last)
    for s in defs['stages']:
        for p in s['packets']:
            assert p['approvalMode'] in ('INHERIT_MACRO','SPECIAL_SEPARATE')
            assert p['qcRequired'] is True
            assert p['requiresExplicitApproval']==(p['approvalMode']=='SPECIAL_SEPARATE')

def test_stage_defs_use_internal_macro_qc_not_user_stage_acceptance():
    defs=read('skills/openfilm-production-p06-p21/references/STAGE_DEFINITIONS.json')
    assert len(defs['stages'])==16
    for stage in defs['stages']:
        assert stage['macroId'] in {f'M{i}' for i in range(8)}
        assert stage['requiresEvidence'] is True
        assert stage['requiresAcceptance'] is False
        assert stage['acceptanceMode']=='INTERNAL_QC_UNTIL_MACRO_ACCEPTED'
    assert next(s for s in defs['stages'] if s['id']=='P21')['finalAcceptanceGate']=='USER_FINAL'

def test_legacy_pass_requires_user_approval():
    val=module('skills/openfilm-checkpoint-approval/references/validate_production_state.py','state_validator')
    state=read('skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json')
    stage=state['stages'][0]
    stage.update(status='PASS',qcStatus='PASS',evidence=['qc/P06.md'])
    assert any('without approvals' in x for x in val.validate(state))

def test_macro_internal_pass_does_not_claim_user_acceptance():
    val=module('skills/openfilm-checkpoint-approval/references/validate_production_state.py','macro_state_validator')
    state=read('skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json')
    stage=state['stages'][0]
    stage.update(status='PASS',qcStatus='PASS',evidence=['qc/P06.md'],
        macroInternalGate={'macroId':'M0','planApprovalId':'real-user-macro-plan',
                           'qcStatus':'PASS','evidencePaths':['qc/P06.md']})
    stage['planApproval'].update(status='APPROVED',approvalId='real-user-macro-plan',scope='macro:M0',source='chat-click',at='2026-11-20T00:00:00+07:00')
    assert not any('without approvals' in x for x in val.validate(state))
    assert stage['acceptanceApproval']['status']=='NOT_REQUESTED'

def test_macro_internal_missing_qc_or_real_plan_rejected():
    val=module('skills/openfilm-checkpoint-approval/references/validate_production_state.py','macro_state_validator_bad')
    state=read('skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json')
    stage=state['stages'][0]
    stage.update(status='PASS',qcStatus='PASS',evidence=['qc/P06.md'],macroInternalGate={'macroId':'M0','qcStatus':'PASS','evidencePaths':['qc/P06.md']})
    assert val.validate(state)

def test_P21_cannot_auto_accept_even_with_macro_internal_gate():
    val=module('skills/openfilm-checkpoint-approval/references/validate_production_state.py','macro_state_validator_final')
    state=read('skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json')
    for s in state['stages'][:-1]:
        s.update(status='PASS',qcStatus='PASS',evidence=['qc/stage.md'])
        s['planApproval'].update(status='APPROVED',approvalId='user-macro',scope='macro',source='chat',at='2026-11-20')
        s['acceptanceApproval'].update(status='APPROVED',approvalId='user-final',scope='macro',source='chat',at='2026-11-20')
    final=state['stages'][-1]
    final.update(status='PASS',qcStatus='PASS',evidence=['qc/P21.md'],macroInternalGate={'macroId':'M7','planApprovalId':'user-plan','qcStatus':'PASS','evidencePaths':['qc/P21.md']})
    final['planApproval'].update(status='APPROVED',approvalId='user-plan',scope='macro',source='chat',at='2026-11-20')
    assert any('without approvals' in x for x in val.validate(state))

def test_work_index_accepts_cross_stage_macro_plan_without_packet_approval():
    v=module('skills/openfilm-high-workpackets/references/validate_work_packets.py','macro_packet_validator')
    index={'schemaVersion':1,'stateRevision':4,'packets':[
        {'packetId':'P07.01.A','stageId':'P07','status':'PLANNED','qcStatus':'NOT_TESTED'},
        {'packetId':'P08.01.A','stageId':'P08','status':'PLANNED','qcStatus':'NOT_TESTED'}],
        'macroBundles':[{'macroBundleId':'M1.B001','macroId':'M1','stageIds':['P07','P08'],
                         'packetIds':['P07.01.A','P08.01.A'],'status':'PLANNED','allowedPaths':[],
                         'inputHashes':{},'riskClass':'NORMAL'}]}
    assert v.validate(index)==[]

def test_work_index_rejects_macro_closed_without_user_acceptance():
    v=module('skills/openfilm-high-workpackets/references/validate_work_packets.py','macro_packet_validator_bad')
    index={'schemaVersion':1,'stateRevision':4,'packets':[{'packetId':'P07.01.A','stageId':'P07','status':'READY_FOR_REVIEW','qcStatus':'PASS'}],
           'macroBundles':[{'macroBundleId':'M1.B001','macroId':'M1','stageIds':['P07'],
                            'packetIds':['P07.01.A'],'status':'PASS','allowedPaths':[],'riskClass':'NORMAL'}]}
    assert any('macro' in e.lower() and 'accept' in e.lower() for e in v.validate(index))

def test_work_index_rejects_macro_scopes_outside_stage_policy():
    v=module('skills/openfilm-high-workpackets/references/validate_work_packets.py','macro_packet_validator_scope')
    index={'schemaVersion':1,'stateRevision':4,'packets':[{'packetId':'P21.01.A','stageId':'P21','status':'PLANNED','qcStatus':'NOT_TESTED'}],
           'macroBundles':[{'macroBundleId':'M1.B001','macroId':'M1','stageIds':['P21'],
                            'packetIds':['P21.01.A'],'status':'PLANNED','allowedPaths':[],'riskClass':'NORMAL'}]}
    assert v.validate(index)
