import json,unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'skills/openfilm-batch-approval/references/BUNDLE_POLICY.json'
F=ROOT/'skills/openfilm-batch-approval/references/bundle_scheduler.py'
spec=spec_from_file_location('bundle_scheduler',F);mod=module_from_spec(spec);spec.loader.exec_module(mod)
class BundleSchedulerTests(unittest.TestCase):
 def policy(self):return json.loads(P.read_text('utf8'))
 def packet(self,id,dep=None,risk='NORMAL',special=False):return {'packetId':id,'stageId':id[:3],'scopeIds':['C01'],'inputPaths':['scene/film.json'],'outputPaths':[f'out/{id}.json'],'allowedCommands':['python:read_only'],'status':'PLANNED','qcStatus':'NOT_TESTED','dependencies':dep or [],'riskClass':risk,'specialApprovalRequired':special}
 def test_group_five_packets_one_click(self):
  ps=[self.packet(f'P07.0{i}.A') for i in range(1,6)]
  groups=mod.propose({'packets':ps},self.policy());self.assertEqual(len(groups),1);self.assertEqual(len(groups[0]['packetIds']),5)
 def test_special_separated(self):
  ps=[self.packet('P06.01.A'),self.packet('P06.02.B',risk='MODEL_DOWNLOAD',special=True),self.packet('P06.03.C')]
  groups=mod.propose({'packets':ps},self.policy());self.assertEqual([len(b['packetIds']) for b in groups],[1,1,1]);self.assertTrue(groups[1]['specialApprovalRequired'])
 def test_unsafe_command_not_silent(self):
  p=self.packet('P07.01.A');p['allowedCommands']=['winget install app']
  with self.assertRaises(ValueError):mod.propose({'packets':[p]},self.policy())
 def test_unresolved_scope_rejected(self):
  p=self.packet('P07.01.A');p['scopeIds']=['<film-id>']
  with self.assertRaises(ValueError):mod.propose({'packets':[p]},self.policy())
 def test_traversal_rejected(self):
  p=self.packet('P07.01.A');p['outputPaths']=['../outside']
  with self.assertRaises(ValueError):mod.propose({'packets':[p]},self.policy())
 def test_internal_qc_ready_allows_next_in_same_bundle(self):
  a=self.packet('P07.01.A');b=self.packet('P07.02.B',[a['packetId']]);a.update(status='READY_FOR_REVIEW',qcStatus='PASS')
  ix={'packets':[a,b],'approvalBundles':[{'bundleId':'P07.B01','stageId':'P07','packetIds':[a['packetId'],b['packetId']],'allowedPaths':a['outputPaths']+b['outputPaths'],'allowedCommands':['python:read_only'],'status':'IN_PROGRESS','planApprovalId':'user-approved'}]}
  self.assertEqual(mod.next_eligible_packet(ix,'P07.B01'),b['packetId'])
 def test_cross_bundle_needs_user_acceptance(self):
  a=self.packet('P07.01.A');b=self.packet('P07.02.B',[a['packetId']]);a.update(status='READY_FOR_REVIEW',qcStatus='PASS')
  ix={'packets':[a,b],'approvalBundles':[{'bundleId':'P07.B02','stageId':'P07','packetIds':[b['packetId']],'allowedPaths':b['outputPaths'],'allowedCommands':['python:read_only'],'status':'IN_PROGRESS','planApprovalId':'user-approved'}]}
  self.assertIsNone(mod.next_eligible_packet(ix,'P07.B02'))
  a.update(status='PASS',acceptanceApprovalId='real');self.assertEqual(mod.next_eligible_packet(ix,'P07.B02'),b['packetId'])
 def test_unapproved_bundle_no_execution(self):
  a=self.packet('P07.01.A');ix={'packets':[a],'approvalBundles':[{'bundleId':'P07.B01','stageId':'P07','packetIds':[a['packetId']],'status':'PLANNED'}]}
  self.assertIsNone(mod.next_eligible_packet(ix,'P07.B01'))
 def test_unlisted_command_rejected(self):
  a=self.packet('P07.01.A');ix={'packets':[a],'approvalBundles':[{'bundleId':'P07.B01','stageId':'P07','packetIds':[a['packetId']],'status':'APPROVED','planApprovalId':'user-approved','allowedPaths':a['outputPaths'],'allowedCommands':[]}]}
  self.assertIsNone(mod.next_eligible_packet(ix,'P07.B01'))
 def test_failure_stops_bundle(self):
  a=self.packet('P07.01.A');b=self.packet('P07.02.B');a.update(status='FAIL',qcStatus='FAIL')
  ix={'packets':[a,b],'approvalBundles':[{'bundleId':'P07.B01','stageId':'P07','packetIds':[a['packetId'],b['packetId']],'status':'APPROVED','planApprovalId':'real','allowedPaths':a['outputPaths']+b['outputPaths'],'allowedCommands':['python:read_only']}]}
  self.assertIsNone(mod.next_eligible_packet(ix,'P07.B01'))
if __name__=='__main__':unittest.main()
