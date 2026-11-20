"""File-backed contracts for Finish First; no fake visual/QC receipts."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
import wave
import pytest

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'skills/openfilm-macro-bundles/references'
def load(name):
    s=importlib.util.spec_from_file_location(name,REF/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
f=load('finish_first');scheduler=load('macro_scheduler');flow=load('production_flow')
policy=json.loads((REF/'MACRO_POLICY.json').read_text(encoding='utf-8'))

def file(root,path,content='{}'):
    p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
    return f.digest(p)

def setup(root, stages=('P07','P10')):
    packets=[]
    for i,stage in enumerate(stages):
        packets.append({'packetId':stage+'.01.A','stageId':stage,'status':'PLANNED',
            'scopeIds':[stage],'inputPaths':['input.json'] if i==0 else [packets[-1]['outputPaths'][0]],
            'outputPaths':[f'out/{stage}.json'],'allowedCommands':[],
            'riskClass':'NORMAL','dependencies':[] if i==0 else [packets[-1]['packetId']]})
    state={'schemaVersion':1,'stateRevision':1,'deviceId':'test-pc','workspace':str(root),
        'filmId':'fixture','packets':packets,'macroBundles':[], 'preflightGates':{}}
    for i in range(6):
        p=f'reports/P{i:02d}.json';file(root,p)
        state['preflightGates'][f'P{i:02d}']={'status':'OUTPUT_READY','evidencePaths':[p]}
    sha=file(root,'input.json')
    state['stageStates']={f'P{i:02d}':{'status':'OUTPUT_READY','outputPaths':['input.json'],'outputHashes':{'input.json':sha}} for i in range(6,22) if f'P{i:02d}' not in stages}
    state['macroBundles']=scheduler.propose(state,policy)
    for b in state['macroBundles']:
        b['presentedToUserRevision']=1
        b['inputHashes']={'input.json':sha} if b==state['macroBundles'][0] else {}
    return state

def event(state,action,bundle=None):
    e={k:state[k] for k in ('stateRevision','deviceId','workspace','filmId')}
    e.update(action=action,approvalId='actual-test-user-event',source='USER_CHAT',at='2026-11-20T12:00:00+07:00')
    if action=='APPROVE_PRODUCTION':
        e['macroBundleIds']=[b['macroBundleId'] for b in state['macroBundles']]
        e['bundles']={b['macroBundleId']:{k:copy.deepcopy(b.get(k)) for k in flow.SCOPE_FIELDS} for b in state['macroBundles']}
    else:
        b=bundle or state['macroBundles'][0];e['macroBundleId']=b['macroBundleId']
        e.update({k:copy.deepcopy(b.get(k)) for k in flow.SCOPE_FIELDS})
    return e

def ready(state,root,n):
    p=state['packets'][n];sha=file(root,p['outputPaths'][0])
    p.update(status='OUTPUT_READY',outputHashes={p['outputPaths'][0]:sha})

def test_one_scope_crosses_macros_without_qc_or_acceptance(tmp_path):
    state=setup(tmp_path);approved=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    assert state['macroBundles'][0]['status']=='PLANNED'
    assert scheduler.next_eligible_packet(approved,'M1.B001',policy)=='P07.01.A'
    ready(approved,tmp_path,0)
    assert scheduler.next_eligible_packet(approved,'M2.B001',policy)=='P10.01.A'
    assert all('acceptanceApprovalId' not in p for p in approved['packets'])
    resumed=json.loads(json.dumps(approved))
    assert scheduler.next_eligible_packet(resumed,'M2.B001',policy)=='P10.01.A'

@pytest.mark.parametrize('mutation',['missing','hash','escape','command','scope','unapproved'])
def test_no_progress_on_missing_output_or_changed_authority(tmp_path,mutation):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy);ready(state,tmp_path,0)
    if mutation=='missing':(tmp_path/'out/P07.json').unlink()
    elif mutation=='hash':file(tmp_path,'out/P07.json','{"changed":true}')
    elif mutation=='escape':state['packets'][1]['outputPaths']=['../outside.json']
    elif mutation=='command':state['packets'][1]['allowedCommands']=['pip install evil']
    elif mutation=='scope':state['macroBundles'][1]['allowedCommands']=['arbitrary']
    else:state['macroBundles'][1]['planApprovalId']=None
    assert scheduler.next_eligible_packet(state,'M2.B001',policy) is None

def test_source_hash_and_revision_verified_against_disk(tmp_path):
    state=setup(tmp_path);e=event(state,'APPROVE_PRODUCTION')
    e['stateRevision']=0;assert flow.validate_event(state,e,policy)
    e=event(state,'APPROVE_PRODUCTION');file(tmp_path,'input.json','{"changed":1}')
    assert any('hash' in x for x in flow.validate_event(state,e,policy))

def test_special_action_cannot_hide_in_production_scope(tmp_path):
    state=setup(tmp_path);state['packets'][0].update(riskClass='PACKAGE_INSTALL',specialApprovalRequired=True)
    assert flow.validate_event(state,event(state,'APPROVE_PRODUCTION'),policy)

def test_legacy_migration_backups_and_never_invents_completion(tmp_path):
    state=setup(tmp_path);ready(state,tmp_path,0)
    state['packets'][0]['status']='QC_PASS';state['packets'][1]['status']='READY_FOR_REVIEW'
    state['legacyData']={'old':'preserved'}
    path=tmp_path/'checkpoint.json';path.write_text(json.dumps(state),encoding='utf-8');before=path.read_bytes()
    new,backup=load('migrate_checkpoint').migrate(path,tmp_path)
    assert backup.read_bytes()==before
    assert new['packets'][0]['status']=='OUTPUT_READY'
    assert new['packets'][1]['status']=='FAILED_TECHNICAL'
    assert new['legacyData']==state['legacyData']
    assert load('migrate_checkpoint').migrate(path,tmp_path)[1] is None

def test_skip_is_reasoned_but_does_not_supply_a_missing_input(tmp_path):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    state['packets'][0].update(status='SKIPPED',skipReason='not used')
    assert scheduler.next_eligible_packet(state,'M2.B001',policy) is None
    assert f.completion_errors({'status':'SKIPPED'},tmp_path)

@pytest.mark.parametrize('path',['../secret','/absolute','C:/absolute','a//b','CON.txt','trailing.','a/../b'])
def test_confined_paths(tmp_path,path):
    with pytest.raises(ValueError):f.confined(tmp_path,path)

def make_video(root,path='V01.mp4',audio=True):
    if not shutil.which('ffmpeg'):pytest.skip('installed ffmpeg unavailable')
    args=['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','color=c=blue:s=160x90:r=10:d=0.4']
    if audio:args+=['-f','lavfi','-i','sine=frequency=440:duration=0.4']
    args+=['-c:v','libx264','-pix_fmt','yuv420p']
    if audio:args+=['-c:a','aac','-shortest']
    subprocess.run(args+[str(root/path)],check=True,capture_output=True)

def test_video_decode_and_required_audio(tmp_path):
    make_video(tmp_path,audio=False)
    assert not f.check_file(tmp_path,'V01.mp4')
    assert f.check_file(tmp_path,'V01.mp4',require_audio=True)
    file(tmp_path,'bad.mp4','not video');assert f.check_file(tmp_path,'bad.mp4')

def test_delivery_then_user_revision_preserves_v01(tmp_path):
    state=setup(tmp_path,('P21',));state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    ready(state,tmp_path,0);make_video(tmp_path)
    state['video']={'path':'V01.mp4','sha256':f.digest(tmp_path/'V01.mp4'),'version':1,'status':'OUTPUT_READY','requiresAudio':True}
    assert flow.validate_event(state,event(state,'ACCEPT_VIDEO'),policy)
    state=flow.apply_event(state,event(state,'DELIVER_VIDEO'),policy)
    assert state['video']['status']=='DELIVERED_FOR_REVIEW'
    feedback=event(state,'REQUEST_REVISION');feedback['feedback']=[{'category':'scene','targetIds':['shot-A'],'request':'change blue to red'}]
    revisions=load('revision_history');state=revisions.plan_revision(state,feedback)
    assert state['revisionPlan']['outputPath']=='./V02.mp4' or state['revisionPlan']['outputPath']=='V02.mp4'
    old=(tmp_path/'V01.mp4').read_bytes();make_video(tmp_path,'V02.mp4')
    state=revisions.register_revision(state)
    assert (tmp_path/'V01.mp4').read_bytes()==old and state['video']['version']==2
    assert state['video']['status']=='OUTPUT_READY'

def test_packet_validator_requires_real_files_even_without_check_files(tmp_path):
    state=setup(tmp_path);ready(state,tmp_path,0);state['packets'][0]['planApprovalId']='user'
    state['macroBundles']=[]
    validator=load('validate_completion')
    assert not validator.validate_packets(state)
    (tmp_path/'out/P07.json').unlink()
    assert validator.validate_packets(state)

def test_policy_has_same_99_ids_and_eight_macros():
    defs=json.loads((ROOT/'skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json').read_text(encoding='utf-8'))
    assert len({p['templateId'] for s in defs['stages'] for p in s['packets']})==99
    assert [m['id'] for m in policy['macros']]==[f'M{i}' for i in range(8)]
    assert 'visualInspectionRequiredForAcceptance' not in policy
    assert 'stageQC' not in policy

def test_missing_prior_stage_cannot_be_omitted_from_plan(tmp_path):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    state['stageStates'].pop('P06')
    assert scheduler.next_eligible_packet(state,'M1.B001',policy) is None

def test_accept_video_requires_real_user_event_after_delivery(tmp_path):
    state=setup(tmp_path,('P21',));state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    ready(state,tmp_path,0);make_video(tmp_path)
    state['video']={'path':'V01.mp4','sha256':f.digest(tmp_path/'V01.mp4'),'version':1,'status':'OUTPUT_READY'}
    state=flow.apply_event(state,event(state,'DELIVER_VIDEO'),policy)
    e=event(state,'ACCEPT_VIDEO');e['source']='AGENT'
    assert flow.validate_event(state,e,policy)
    e=event(state,'ACCEPT_VIDEO');state=flow.apply_event(state,e,policy)
    assert state['video']['status']=='USER_ACCEPTED'

def test_resume_checks_derived_input_from_another_approved_macro(tmp_path):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    ready(state,tmp_path,0)
    e=event(state,'RESUME_APPROVED_MACRO',state['macroBundles'][1])
    assert not flow.validate_event(state,e,policy)
    file(tmp_path,'out/P07.json','{"tampered":true}')
    assert flow.validate_event(state,e,policy)

def test_migration_keeps_runtime_proofs_and_user_metadata(tmp_path):
    state=setup(tmp_path);state['runtime']={'status':'PASS','data':'untouched'}
    original_preflight=copy.deepcopy(state['preflightGates'])
    state['packets'][0]['status']='VISUAL_BLOCKED';state['packets'][1]['status']='BLOCKED'
    p=tmp_path/'state.json';p.write_text(json.dumps(state),encoding='utf-8')
    result,_=load('migrate_checkpoint').migrate(p,tmp_path)
    assert result['runtime']==state['runtime'] and result['preflightGates']==original_preflight
    assert result['packets'][0]['status']=='PLANNED' and result['packets'][1]['status']=='BLOCKED'

def test_stage_can_complete_without_qc_but_not_without_files(tmp_path):
    state=json.loads((ROOT/'skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json').read_text(encoding='utf-8'))
    state['workspace']=str(tmp_path);p=state['stages'][0]
    p.update(status='OUTPUT_READY',outputPaths=['runtime.json'],outputHashes={'runtime.json':file(tmp_path,'runtime.json')})
    p['planApproval']={'status':'APPROVED','approvalId':'user','source':'USER_CHAT','at':'2026-11-20','scope':'M0'}
    validator=load('validate_completion')
    assert not validator.validate_stages(state)
    (tmp_path/'runtime.json').unlink();assert validator.validate_stages(state)
