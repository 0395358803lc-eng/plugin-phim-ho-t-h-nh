"""Regression for missing-mode v1.13 checkpoints and retained authorization."""
import copy
import json
import pytest
from test_finish_first import setup, event, file, load, policy, f, scheduler, flow

@pytest.mark.parametrize('version',[None,'1.13.0','1.14.0','1.14.1'])
def test_missing_mode_never_selects_finish_first(tmp_path,version):
    state=setup(tmp_path);state.pop('productionMode')
    if version:state['pluginVersion']=version
    assert not f.enabled(state)
    assert f.checkpoint_kind(state)=='LEGACY_UNDECLARED'
    assert scheduler.next_eligible_packet(state,'M1.B001',policy) is None
    assert any('MIGRATION_REQUIRED' in x for x in flow.validate_event(state,event(state,'APPROVE_PRODUCTION'),policy))
    assert load('validate_completion').validate_packets(state)

@pytest.mark.parametrize('mode',['unknown','',None])
def test_oneclick_does_not_guess_a_mode(tmp_path,mode):
    state=setup(tmp_path);state['productionMode']=mode
    import importlib.util
    from test_finish_first import ROOT
    spec=importlib.util.spec_from_file_location('oneclick',ROOT/'skills/openfilm-oneclick-approval/references/validate_approval_event.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert m.validate(state,event(state,'APPROVE_PRODUCTION'))

def test_migration_preserves_grants_but_cannot_execute_until_receipt_revalidated(tmp_path):
    state=setup(tmp_path)
    approval=event(state,'APPROVE_PRODUCTION');state=flow.apply_event(state,approval,policy)
    state.pop('productionMode');state['pluginVersion']='1.13.0'
    original=copy.deepcopy(state)
    p=tmp_path/'WORK_UNIT_INDEX.json';p.write_text(json.dumps(state),encoding='utf-8');before=p.read_bytes()
    migrated,backup=load('migrate_checkpoint').migrate(p,tmp_path)
    assert backup.read_bytes()==before
    assert migrated['eventHistory']==original['eventHistory']
    for new,old in zip(migrated['macroBundles'],original['macroBundles']):
        for key,value in old.items():assert new[key]==value
        assert new['scopeRevalidationRequired'] and not f.authorized(new)
    assert scheduler.next_eligible_packet(migrated,'M1.B001',policy) is None
    restored=load('migrate_checkpoint').restore_existing_approval(migrated,'M1.B001',approval['approvalId'])
    assert restored['macroBundles'][0]['planApprovalId']==approval['approvalId']
    assert scheduler.next_eligible_packet(restored,'M1.B001',policy)=='P07.01.A'
    assert restored['eventHistory']==original['eventHistory']

def test_no_new_receipt_or_changed_scope_can_restore_authority(tmp_path):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    state.pop('productionMode');p=tmp_path/'state.json';p.write_text(json.dumps(state),encoding='utf-8')
    m=load('migrate_checkpoint');state,_=m.migrate(p,tmp_path)
    state['macroBundles'][0]['allowedCommands'].append('unapproved command')
    with pytest.raises(ValueError,match='scope differs'):m.restore_existing_approval(state,'M1.B001','actual-test-user-event')
    state['eventHistory']=[]
    with pytest.raises(ValueError,match='receipt required'):m.restore_existing_approval(state,'M1.B001','actual-test-user-event')

@pytest.mark.parametrize('status',['PLANNED','WAITING_APPROVAL','IN_PROGRESS','BLOCKED','FAILED_TECHNICAL','INVALIDATED'])
def test_incomplete_status_is_never_promoted_even_if_a_file_exists(tmp_path,status):
    state=setup(tmp_path);state.pop('productionMode');packet=state['packets'][0]
    packet.update(status=status,outputHashes={packet['outputPaths'][0]:file(tmp_path,packet['outputPaths'][0])})
    p=tmp_path/'state.json';p.write_text(json.dumps(state),encoding='utf-8')
    migrated,_=load('migrate_checkpoint').migrate(p,tmp_path)
    assert migrated['packets'][0]['status']==status

def test_explicit_new_mode_with_old_version_still_requires_migration(tmp_path):
    state=setup(tmp_path);state['pluginVersion']='1.13.0'
    assert not f.enabled(state) and f.migration_errors(state)

def test_copy_migration_preserves_original_bytes_and_identity(tmp_path):
    root=tmp_path/'source';root.mkdir();dest=tmp_path/'audit';dest.mkdir()
    state=setup(root);state.pop('productionMode');state['pluginVersion']='1.13.0'
    p=root/'state.json';p.write_text(json.dumps(state),encoding='utf-8');before=p.read_bytes()
    migrated,backup=load('migrate_checkpoint').migrate(p,root,copy_to=dest/'migrated.json')
    assert p.read_bytes()==backup.read_bytes()==before
    assert migrated['workspace']==state['workspace']
    assert json.loads((dest/'migrated.json').read_text(encoding='utf-8'))==migrated
    with pytest.raises(ValueError,match='new file'):
        load('migrate_checkpoint').migrate(p,root,copy_to=dest/'migrated.json')
