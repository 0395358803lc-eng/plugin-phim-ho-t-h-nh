"""Backend action contract only; these tests do not claim a native ChatGPT click."""
import copy
import importlib.util
import pytest
from test_finish_first import ROOT, setup, event, ready, flow, policy

spec=importlib.util.spec_from_file_location('oneclick',ROOT/'skills/openfilm-oneclick-approval/references/validate_approval_event.py')
oneclick=importlib.util.module_from_spec(spec);spec.loader.exec_module(oneclick)

def test_progress_and_resume_keep_existing_authority(tmp_path):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    before=copy.deepcopy(state)
    assert oneclick.validate(state,event(state,'VIEW_PROGRESS'))==[]
    assert state==before
    resumed=flow.apply_event(state,event(state,'RESUME_APPROVED_MACRO'),policy)
    assert [b['planApprovalId'] for b in resumed['macroBundles']]==[b['planApprovalId'] for b in state['macroBundles']]
    assert [b['approvedScopeSha256'] for b in resumed['macroBundles']]==[b['approvedScopeSha256'] for b in state['macroBundles']]
    stale=event(state,'VIEW_PROGRESS');stale['stateRevision']-=1
    assert oneclick.validate(state,stale)

def test_read_actions_never_accept_a_missing_video(tmp_path):
    state=setup(tmp_path);state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy)
    before=copy.deepcopy(state)
    assert oneclick.validate(state,event(state,'VIEW_VIDEO'))
    assert state==before and 'video' not in state

@pytest.mark.parametrize('action',['ACCEPT_VIDEO','REQUEST_REVISION'])
def test_user_actions_reject_manufactured_non_user_event(tmp_path,action):
    state=setup(tmp_path,stages=('P21',));state=flow.apply_event(state,event(state,'APPROVE_PRODUCTION'),policy);ready(state,tmp_path,0)
    e=event(state,action);e.update(source='SYSTEM',feedback=[{'category':'effect','targetIds':['S02'],'request':'change color'}])
    assert any('explicit user event' in err for err in oneclick.validate(state,e))
    with pytest.raises(ValueError):flow.apply_event(state,e,policy)
