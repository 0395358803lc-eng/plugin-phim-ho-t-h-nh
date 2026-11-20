import json, unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'skills/openfilm-oneclick-approval/references/validate_approval_event.py'
spec=spec_from_file_location('oneclick',FILE);mod=module_from_spec(spec);spec.loader.exec_module(mod)
class GateTest(unittest.TestCase):
    def state(self):
        return {'productionMode':'LEGACY_QC','stateRevision':7,'deviceId':'verified-device','workspace':r'D:\film\VIDEO_HOAT_HINH_WORKSPACE','currentPacketId':'P14.02.C005','nextPacketId':'P14.02.C006','packets':[
        {'packetId':'P14.02.C005','scopeIds':['C005'],'status':'READY_FOR_REVIEW','qcStatus':'PASS','evidencePaths':['qc/C005.md'],'outputPaths':['out/C005.html'],'outputHashes':{'out/C005.html':'abc'},'planApprovalId':'P-A'},
        {'packetId':'P14.02.C006','scopeIds':['C006'],'status':'PLANNED','presentedToUserRevision':7}]}
    def event(self,action='ACCEPT_AND_RUN_NEXT'):
        return {'action':action,'stateRevision':7,'deviceId':'verified-device','workspace':r'D:\film\VIDEO_HOAT_HINH_WORKSPACE','currentPacketId':'P14.02.C005','scopeIds':['C005'],'nextPacketId':'P14.02.C006','nextScopeIds':['C006']}
    def test_valid_accept_next_metadata(self):self.assertEqual(mod.validate(self.state(),self.event()),[])
    def test_stale_revision_blocked(self):
        e=self.event();e['stateRevision']=6;self.assertTrue(any('stale' in x for x in mod.validate(self.state(),e)))
    def test_wrong_device_blocked(self):
        e=self.event();e['deviceId']='another';self.assertTrue(any('deviceId' in x for x in mod.validate(self.state(),e)))
    def test_missing_evidence_blocked(self):
        s=self.state();s['packets'][0]['evidencePaths']=[];self.assertTrue(any('evidence' in x for x in mod.validate(s,self.event())))
    def test_next_not_shown_blocked(self):
        s=self.state();s['packets'][1]['presentedToUserRevision']=6;self.assertTrue(any('presented' in x for x in mod.validate(s,self.event())))
    def test_next_special_approval_cannot_merge(self):
        s=self.state();s['packets'][1]['specialApprovalRequired']=True;self.assertTrue(any('special approval' in x for x in mod.validate(s,self.event())))
    def test_scope_change_rejected(self):
        e=self.event();e['nextScopeIds']=['C007'];self.assertTrue(any('nextScopeIds' in x for x in mod.validate(self.state(),e)))
    def test_fail_cannot_accept_next(self):
        s=self.state();s['packets'][0]['status']='FAIL';s['packets'][0]['qcStatus']='FAIL';self.assertTrue(any('not QC PASS' in x for x in mod.validate(s,self.event())))
    def test_repair_requires_issue_and_shown_plan(self):
        s=self.state();s['packets'][0]['status']='FAIL';s['packets'][0]['qcStatus']='FAIL';s['packets'][0]['issueId']='E1';e=self.event('APPROVE_REPAIR');e['issueId']='E1';self.assertTrue(any('repair plan not shown' in x for x in mod.validate(s,e)))
    def test_pause_no_action(self):self.assertEqual(mod.validate(self.state(),self.event('PAUSE')),[])
if __name__=='__main__':unittest.main()
