"""Behavioral acceptance for cross-stage macro approvals, no Remote IO."""
import copy,importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'skills/openfilm-macro-bundles/references'

def load(name):
    spec=importlib.util.spec_from_file_location(name,M/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def policy():
    p=json.loads((M/'MACRO_POLICY.json').read_text('utf-8'));p['humanDecisionGates']={'P08':'PROFILE_CHOICE'};return p

def packet(pid, stage, *, risk='NORMAL', special=False, dependencies=None):
    return {'packetId':pid,'stageId':stage,'scopeIds':[pid],
            'inputPaths':[f'projects/a/input/{pid}.json'], 'outputPaths':[f'projects/a/output/{pid}.json'],
            'allowedCommands':[],'dependencies':dependencies or [],'riskClass':risk,
            'specialApprovalRequired':special,'status':'PLANNED','qcStatus':'NOT_TESTED'}

def index(packets):
    return {'productionMode':'LEGACY_QC','stateRevision':4,'deviceId':'pc1','workspace':r'D:\animation\VIDEO_HOAT_HINH_WORKSPACE',
            'filmId':'a','packets':packets,'macroBundles':[], 'stageStates':{},'decisionGates':{}}

def mark_preconditions(ix, earliest):
    for i in range(6,int(earliest[1:])):
        sid=f'P{i:02d}'
        ix['stageStates'][sid]={'status':'PASS','qcStatus':'PASS','evidencePaths':[f'qc/{sid}.json'],'macroId':'PREVIOUS_ACCEPTED'}

def event(index,b,action):
    return {**{k:index[k] for k in ('stateRevision','deviceId','workspace','filmId')},
            'action':action,'macroBundleId':b['macroBundleId'],
            **{k:copy.deepcopy(b[k]) for k in ('macroId','stageIds','packetIds','scopeIds','allowedPaths','allowedCommands','riskClass','inputHashes')}}

def test_policy_has_eight_macros_covering_all_stages_in_order():
    p=policy();m=p['macros'];assert len(m)==8
    assert [x['id'] for x in m]==[f'M{i}' for i in range(8)]
    assert m[0]['preflightStages']==['P00','P01','P02','P03','P04','P05']
    assert [y for x in m for y in x['stages']]==[f'P{i:02d}' for i in range(6,22)]

def test_cross_stage_plan_is_one_user_approval_bundle():
    p=policy();s=load('macro_scheduler')
    ix=index([packet('P07.01.A','P07'),packet('P08.01.A','P08'),packet('P09.01.A','P09')])
    macros=s.propose(ix,p)
    assert len(macros)==1
    assert macros[0]['macroId']=='M1'
    assert macros[0]['stageIds']==['P07','P08','P09']
    assert len(macros[0]['packetIds'])==3
    assert macros[0]['macroBundleId']=='M1.B001'

def test_special_packet_is_single_separate_approval_and_splits_normal():
    s=load('macro_scheduler');p=policy()
    ix=index([packet('P06.09.ONE','P06'),packet('P06.10.ONE','P06',special=True),packet('P06.11.ONE','P06')])
    macros=s.propose(ix,p)
    assert len(macros)==3
    assert [x['specialApprovalRequired'] for x in macros]==[False,True,False]
    assert macros[1]['packetIds']==['P06.10.ONE']

def test_single_approved_macro_runs_multiple_stages_after_internal_qc():
    s=load('macro_scheduler');p=policy()
    a=packet('P07.01.A','P07');b=packet('P08.01.A','P08',dependencies=[a['packetId']]);c=packet('P09.01.A','P09',dependencies=[b['packetId']])
    ix=index([a,b,c]);bundle=s.propose(ix,p)[0];bundle.update(status='APPROVED',planApprovalId='user-click-1')
    ix['macroBundles']=[bundle]
    mark_preconditions(ix,'P07')
    assert s.next_eligible_packet(ix,bundle['macroBundleId'],p)=='P07.01.A'
    a.update(status='READY_FOR_REVIEW',qcStatus='PASS',evidencePaths=['qc/a.json'],outputHashes={a['outputPaths'][0]:'a'*64},planApprovalId='user-click-1')
    assert s.next_eligible_packet(ix,bundle['macroBundleId'],p) is None  # P07 stage QC gate missing
    ix['stageStates']['P07']={'status':'QC_PASS','qcStatus':'PASS','evidencePaths':['qc/P07.json'],'macroId':'M1'}
    assert s.next_eligible_packet(ix,bundle['macroBundleId'],p) is None  # P08 decision needs user
    ix['decisionGates']['PROFILE_CHOICE']={'status':'APPROVED','approvalId':'user-choice','evidencePaths':['reports/profile.json']}
    assert s.next_eligible_packet(ix,bundle['macroBundleId'],p)=='P08.01.A'
    b.update(status='READY_FOR_REVIEW',qcStatus='PASS',evidencePaths=['qc/b.json'],outputHashes={b['outputPaths'][0]:'b'*64},planApprovalId='user-click-1')
    ix['stageStates']['P08']={'status':'QC_PASS','qcStatus':'PASS','evidencePaths':['qc/P08.json'],'macroId':'M1'}
    assert s.next_eligible_packet(ix,bundle['macroBundleId'],p)=='P09.01.A'

def test_cross_macro_dependency_requires_user_acceptance():
    s=load('macro_scheduler');p=policy()
    a=packet('P09.01.A','P09');b=packet('P10.01.A','P10',dependencies=[a['packetId']]);ix=index([a,b]);m1,m2=s.propose(ix,p)
    m1.update(status='READY_FOR_REVIEW',planApprovalId='ua1');m2.update(status='APPROVED',planApprovalId='ua2')
    ix['macroBundles']=[m1,m2];mark_preconditions(ix,'P09');a.update(status='READY_FOR_REVIEW',qcStatus='PASS',evidencePaths=['qc/a.json'],outputHashes={'projects/a/output/P09.01.A.json':'a'*64})
    ix['stageStates']['P09']={'status':'QC_PASS','qcStatus':'PASS','evidencePaths':['qc/P09.json'],'macroId':'M1'}
    assert s.next_eligible_packet(ix,m2['macroBundleId'],p) is None
    a.update(status='PASS',acceptanceApprovalId='ua-accept-1');m1.update(status='PASS',acceptanceApprovalId='ua-accept-1');ix['stageStates']['P09']['status']='PASS'
    assert s.next_eligible_packet(ix,m2['macroBundleId'],p)=='P10.01.A'

def test_event_approval_requires_same_revision_and_exact_scope():
    s=load('macro_scheduler');g=load('validate_macro_event');p=policy()
    ix=index([packet('P07.01.A','P07')]);bundle=s.propose(ix,p)[0];bundle['presentedToUserRevision']=4;bundle['inputHashes']={ix['packets'][0]['inputPaths'][0]:'a'*64};ix['macroBundles']=[bundle]
    ev=event(ix,bundle,'APPROVE_MACRO')
    assert not g.validate(ix,ev,p)
    ev['stateRevision']=3;assert any('stale' in x for x in g.validate(ix,ev,p))
    ev=event(ix,bundle,'APPROVE_MACRO');ev['allowedPaths']=['other/file'];assert g.validate(ix,ev,p)
    ev=event(ix,bundle,'APPROVE_MACRO');ev['scopeIds']=['UNLISTED'];assert g.validate(ix,ev,p)

def test_resume_approved_macro_is_not_a_new_permission():
    s=load('macro_scheduler');g=load('validate_macro_event');p=policy()
    ix=index([packet('P07.01.A','P07')]);b=s.propose(ix,p)[0];b.update(status='IN_PROGRESS',planApprovalId='user-click-1',inputHashes={ix['packets'][0]['inputPaths'][0]:'a'*64});ix['macroBundles']=[b]
    assert not g.validate(ix,event(ix,b,'RESUME_APPROVED_MACRO'),p)
    ix['packets'][0]['outputPaths'].append('not-in-approved-scope');assert g.validate(ix,event(ix,b,'RESUME_APPROVED_MACRO'),p)

def test_macro_accept_rejects_missing_qc_and_unapproved_special():
    s=load('macro_scheduler');g=load('validate_macro_event');p=policy()
    ix=index([packet('P06.10.ONE','P06',special=True)]);b=s.propose(ix,p)[0];b.update(status='PLANNED',presentedToUserRevision=4);ix['macroBundles']=[b]
    assert g.validate(ix,event(ix,b,'APPROVE_MACRO'),p)  # special ID not approved
    b.update(status='READY_FOR_REVIEW',planApprovalId='user-click-1',specialApprovalId='user-special-1',evidencePaths=['qc/test.json'])
    assert g.validate(ix,event(ix,b,'ACCEPT_MACRO'),p)  # packet still planned

def test_commands_with_download_cannot_be_reclassified_normal():
    s=load('macro_scheduler');p=policy();pkt=packet('P07.01.A','P07');pkt['allowedCommands']=['npx openfilm@latest']
    with pytest.raises(ValueError):s.propose(index([pkt]),p)

def test_no_invented_paths_or_scope_and_no_duplicate_packets():
    s=load('macro_scheduler');p=policy();pkt=packet('P07.01.A','P07');pkt['outputPaths']=['../secret']
    with pytest.raises(ValueError):s.propose(index([pkt]),p)
    pkt['outputPaths']=['reports/p07.json'];ix=index([pkt,copy.deepcopy(pkt)])
    with pytest.raises(ValueError):s.propose(ix,p)

def test_template_order_not_source_index_controls_special_boundary():
    s=load('macro_scheduler');p=policy()
    # Legacy index may have P06.12 *after* P06.10; always canonicalize.
    ps=[packet('P06.09.A','P06'),packet('P06.10.A','P06',special=True),packet('P06.12.A','P06')]
    groups=s.propose(index(ps),p)
    assert [pid for b in groups for pid in b['packetIds']]==['P06.12.A','P06.09.A','P06.10.A']

def test_M0_requires_verified_P00_to_P05_before_any_operation():
    s=load('macro_scheduler');p=policy()
    ix=index([packet('P06.01.A','P06')]);b=s.propose(ix,p)[0];b.update(status='APPROVED',planApprovalId='user-plan');ix['macroBundles']=[b]
    assert s.next_eligible_packet(ix,b['macroBundleId'],p) is None
    ix['preflightGates']={f'P{i:02d}':{'status':'PASS','evidencePaths':[f'qc/P{i:02d}.json']} for i in range(0,6)}
    assert s.next_eligible_packet(ix,b['macroBundleId'],p)=='P06.01.A'

def test_macro_approval_rejects_missing_input_hashes():
    s=load('macro_scheduler');g=load('validate_macro_event');p=policy()
    ix=index([packet('P07.01.A','P07')]);b=s.propose(ix,p)[0];b['presentedToUserRevision']=4;ix['macroBundles']=[b]
    assert any('input' in x.lower() and 'hash' in x.lower() for x in g.validate(ix,event(ix,b,'APPROVE_MACRO'),p))

def test_same_stage_special_cannot_jump_over_unaccepted_regular_packets():
    s=load('macro_scheduler');p=policy()
    a=packet('P06.09.A','P06');b=packet('P06.10.A','P06',special=True)
    ix=index([a,b]);regular,special=s.propose(ix,p)
    mark_preconditions(ix,'P06')
    ix['preflightGates']={f'P{i:02d}':{'status':'PASS','evidencePaths':[f'qc/P{i:02d}.json']} for i in range(0,6)}
    special.update(status='APPROVED',planApprovalId='user-plan-special',specialApprovalId='explicit-user-special')
    ix['macroBundles']=[regular,special]
    assert s.next_eligible_packet(ix,special['macroBundleId'],p) is None
    a.update(status='PASS',qcStatus='PASS',acceptanceApprovalId='user-accept',evidencePaths=['qc/a.md'],outputHashes={a['outputPaths'][0]:'a'*64})
    regular.update(status='PASS',acceptanceApprovalId='user-accept')
    assert s.next_eligible_packet(ix,special['macroBundleId'],p)=='P06.10.A'

def test_generated_input_inside_approved_macro_does_not_require_impossible_prebuild_hash():
    s=load('macro_scheduler');g=load('validate_macro_event');p=policy()
    a=packet('P07.01.A','P07');b=packet('P08.01.A','P08')
    b['inputPaths']=[a['outputPaths'][0]]  # generated only after P07; cannot pre-hash
    ix=index([a,b]);group=s.propose(ix,p)[0];group['presentedToUserRevision']=4
    group['inputHashes']={a['inputPaths'][0]:'c'*64}
    ix['macroBundles']=[group]
    assert not g.validate(ix,event(ix,group,'APPROVE_MACRO'),p)

def test_missing_prerequisite_same_macro_different_subbundle_must_be_accepted():
    s=load('macro_scheduler');p=policy()
    a=packet('P07.01.A','P07');b=packet('P08.01.A','P08')
    ix=index([a,b]);group=s.propose(ix,p)[0]
    # Model a prior P07 subbundle that is QC-ready but not user accepted.
    earlier={**group,'macroBundleId':'M1.B000','stageIds':['P07'],'packetIds':[a['packetId']], 'status':'READY_FOR_REVIEW', 'planApprovalId':'user-plan'}
    later={**group,'macroBundleId':'M1.B002','stageIds':['P08'],'packetIds':[b['packetId']], 'status':'APPROVED','planApprovalId':'user-plan-2'}
    ix['macroBundles']=[earlier,later];mark_preconditions(ix,'P07')
    a.update(status='READY_FOR_REVIEW',qcStatus='PASS',evidencePaths=['qc/a.md'],outputHashes={a['outputPaths'][0]:'a'*64})
    ix['stageStates']['P07']={'status':'QC_PASS','qcStatus':'PASS','evidencePaths':['qc/P07.md'],'macroId':'M1'}
    ix['decisionGates']['PROFILE_CHOICE']={'status':'APPROVED','approvalId':'human-decision','evidencePaths':['reports/profile.md']}
    assert s.next_eligible_packet(ix,later['macroBundleId'],p) is None
    a.update(status='PASS',acceptanceApprovalId='human-accept');earlier.update(status='PASS',acceptanceApprovalId='human-accept')
    ix['stageStates']['P07']['status']='PASS'
    assert s.next_eligible_packet(ix,later['macroBundleId'],p)==b['packetId']
