import json,unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'skills/openfilm-batch-approval/references/validate_bundle_gate.py'
spec=spec_from_file_location('vhh_batch_validator',FILE);mod=module_from_spec(spec);spec.loader.exec_module(mod)

class BundleTests(unittest.TestCase):
    def base(self):
        b={'bundleId':'P07.B01','stageId':'P07','packetIds':['P07.01.KICH','P07.02.B01'],'scopeIds':['SRC-01','CSV-01'],
            'allowedPaths':['reports/INPUT_AUDIT.md'],'allowedCommands':['python:read_only'],
            'riskClass':'NORMAL','inputHashes':{'source.md':'abc'},'status':'WAITING_APPROVAL',
            'presentedToUserRevision':8,'planApprovalId':None,'evidencePaths':[]}
        ix={'stateRevision':8,'deviceId':'dev-A','workspace':r'D:\video\VIDEO_HOAT_HINH_WORKSPACE',
            'approvalBundles':[b],
            'packets':[{'packetId':'P07.01.KICH','stageId':'P07','status':'PLANNED','scopeIds':['SRC-01'],'qcStatus':'NOT_TESTED'},
                       {'packetId':'P07.02.B01','stageId':'P07','status':'PLANNED','scopeIds':['CSV-01'],'qcStatus':'NOT_TESTED'}]}
        e={'action':'APPROVE_BUNDLE','stateRevision':8,'deviceId':'dev-A','workspace':ix['workspace'],'bundleId':'P07.B01',
            'stageId':'P07','packetIds':b['packetIds'].copy(),'scopeIds':b['scopeIds'].copy(),
            'allowedPaths':b['allowedPaths'].copy(),'allowedCommands':b['allowedCommands'].copy(),
            'riskClass':'NORMAL','inputHashes':b['inputHashes'].copy()}
        return ix,e
    def test_one_click_can_approve_two_micro_packets(self):
        i,e=self.base();self.assertEqual(mod.validate(i,e),[])
    def test_stale_revision_rejected(self):
        i,e=self.base();e['stateRevision']=7;self.assertIn('stale stateRevision',mod.validate(i,e))
    def test_not_presented_rejected(self):
        i,e=self.base();i['approvalBundles'][0]['presentedToUserRevision']=4;self.assertIn('bundle not presented at current revision',mod.validate(i,e))
    def test_cross_stage_packet_rejected(self):
        i,e=self.base();i['packets'][0]['stageId']='P08';self.assertIn('cross-stage packet',mod.validate(i,e))
    def test_bundle_changed_scope_rejected(self):
        i,e=self.base();e['scopeIds']=['BOTHER'];self.assertIn('scopeIds mismatch',mod.validate(i,e))
    def test_unsafe_path_rejected(self):
        i,e=self.base();i['approvalBundles'][0]['allowedPaths']=['../secret'];e['allowedPaths']=['../secret'];self.assertIn('unsafe allowedPaths',mod.validate(i,e))
    def test_absolute_path_rejected(self):
        i,e=self.base();i['approvalBundles'][0]['allowedPaths']=[r'C:\Windows\System32'];e['allowedPaths']=[r'C:\Windows\System32'];self.assertIn('unsafe allowedPaths',mod.validate(i,e))
    def test_command_mismatch_rejected(self):
        i,e=self.base();e['allowedCommands']=['openfilm render'];self.assertIn('allowedCommands mismatch',mod.validate(i,e))
    def test_input_hash_change_rejected(self):
        i,e=self.base();e['inputHashes']={'source.md':'def'};self.assertIn('inputHashes mismatch',mod.validate(i,e))
    def test_special_packet_cannot_be_hidden_in_bundle(self):
        i,e=self.base();i['packets'][1]['specialApprovalRequired']=True;self.assertIn('special action requires separate single-packet bundle',mod.validate(i,e))
    def test_special_action_requires_separate_bundle(self):
        i,e=self.base();i['approvalBundles'][0]['riskClass']='MODEL_DOWNLOAD';e['riskClass']='MODEL_DOWNLOAD'
        self.assertIn('special action requires separate single-packet bundle',mod.validate(i,e))
    def test_special_single_packet_approved(self):
        i,e=self.base();b=i['approvalBundles'][0];b['packetIds']=['P07.01.KICH'];e['packetIds']=['P07.01.KICH'];b['riskClass']='MODEL_DOWNLOAD';e['riskClass']='MODEL_DOWNLOAD';b['specialApprovalRequired']=True
        self.assertEqual(mod.validate(i,e),[])
    def test_resume_requires_prior_approval(self):
        i,e=self.base();e['action']='RESUME_APPROVED_BUNDLE';i['approvalBundles'][0]['status']='IN_PROGRESS'
        self.assertIn('bundle not approved for resume',mod.validate(i,e))
    def test_resume_approved_bundle_no_new_approval(self):
        i,e=self.base();e['action']='RESUME_APPROVED_BUNDLE';i['approvalBundles'][0].update({'status':'IN_PROGRESS','planApprovalId':'real-user-approved'})
        self.assertEqual(mod.validate(i,e),[])
    def test_bundle_accept_with_two_qc_ready_packets(self):
        i,e=self.base();e['action']='ACCEPT_BUNDLE';b=i['approvalBundles'][0]
        b.update(status='READY_FOR_REVIEW',planApprovalId='approved',evidencePaths=['qc/bundle.md'])
        for p in i['packets']:
            p.update(status='READY_FOR_REVIEW',qcStatus='PASS',planApprovalId='approved',evidencePaths=[p['packetId']+'.md'],outputPaths=[p['packetId']+'.json'],outputHashes={p['packetId']+'.json':'ff'})
        b['allowedPaths'] += [p['packetId']+'.json' for p in i['packets']]
        e['allowedPaths']=b['allowedPaths'].copy()
        self.assertEqual(mod.validate(i,e),[])
    def test_bundle_accept_rejects_missing_qc(self):
        i,e=self.base();e['action']='ACCEPT_BUNDLE';b=i['approvalBundles'][0]
        b.update(status='READY_FOR_REVIEW',planApprovalId='approved',evidencePaths=['qc/bundle.md'])
        self.assertTrue(any('not QC ready' in x for x in mod.validate(i,e)))
    def test_next_bundle_must_be_presented(self):
        i,e=self.base();e['action']='ACCEPT_AND_APPROVE_NEXT_BUNDLE';b=i['approvalBundles'][0]
        b.update(status='READY_FOR_REVIEW',planApprovalId='approved',evidencePaths=['qc/bundle.md'])
        for p in i['packets']:
            p.update(status='READY_FOR_REVIEW',qcStatus='PASS',planApprovalId='approved',evidencePaths=['qc/'+p['packetId']+'.md'])
        e['nextBundleId']='P07.B02'
        self.assertTrue(any('next bundle absent' in x for x in mod.validate(i,e)))
    def test_policy_covers_16_stages(self):
        x=json.loads((ROOT/'skills/openfilm-batch-approval/references/BUNDLE_POLICY.json').read_text('utf-8'))
        self.assertEqual([s['stageId'] for s in x['stages']],[f'P{i:02d}' for i in range(6,22)])
        self.assertTrue(x['defaults']['specialApprovalSeparate'])
    def test_normal_scope_invalid_risk_should_fail(self):
        i,e=self.base();i['approvalBundles'][0]['riskClass']='UNRECOGNIZED';e['riskClass']='UNRECOGNIZED'
        self.assertIn('invalid riskClass',mod.validate(i,e))
    def test_bundle_omitting_packet_scope_should_fail(self):
        i,e=self.base();i['packets'][0]['scopeIds']=['SECRET']
        self.assertIn('bundle omits packet scope',mod.validate(i,e))
    def test_bundle_omitting_packet_output_path_should_fail(self):
        i,e=self.base();i['packets'][1]['outputPaths']=['other/private.txt']
        self.assertIn('bundle omits packet outputPaths',mod.validate(i,e))
    def test_bundle_omitting_packet_command_should_fail(self):
        i,e=self.base();i['packets'][1]['allowedCommands']=['openfilm render']
        self.assertIn('bundle omits packet allowedCommands',mod.validate(i,e))
    def test_duplicate_bundle_ids_should_fail(self):
        i,e=self.base();i['approvalBundles'].append(dict(i['approvalBundles'][0]))
        self.assertIn('duplicate bundleId',mod.validate(i,e))
    def test_next_bundle_hash_mismatch_should_fail(self):
        i,e=self.base();e['action']='ACCEPT_AND_APPROVE_NEXT_BUNDLE';b=i['approvalBundles'][0]
        b.update(status='READY_FOR_REVIEW',planApprovalId='approved',evidencePaths=['qc/bundle.md'])
        for p in i['packets']:
            p.update(status='READY_FOR_REVIEW',qcStatus='PASS',planApprovalId='approved',evidencePaths=['qc/p.md'])
        newp={'packetId':'P07.03.OTHER','stageId':'P07','status':'PLANNED','qcStatus':'NOT_TESTED'}
        i['packets'].append(newp)
        n={'bundleId':'P07.B02','stageId':'P07','packetIds':[newp['packetId']],'scopeIds':['C003'],'allowedPaths':['out/C003.md'],'allowedCommands':['python:read_only'],'riskClass':'NORMAL','inputHashes':{'x':'a'},'presentedToUserRevision':8,'status':'WAITING_APPROVAL'}
        i['approvalBundles'].append(n)
        e.update(nextBundleId='P07.B02',nextBundlePacketIds=n['packetIds'],nextBundleScopeIds=n['scopeIds'],nextBundleAllowedPaths=n['allowedPaths'],nextBundleAllowedCommands=n['allowedCommands'],nextBundleRiskClass='NORMAL',nextBundleInputHashes={'x':'TAMPERED'})
        self.assertIn('next bundle inputHashes mismatch',mod.validate(i,e))
if __name__=='__main__':unittest.main()
