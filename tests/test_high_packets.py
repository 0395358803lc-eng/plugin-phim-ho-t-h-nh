import json
import unittest
import tempfile
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT=Path(__file__).resolve().parents[1]
DEF=ROOT/'skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json'
VAL=ROOT/'skills/openfilm-high-workpackets/references/validate_work_packets.py'
spec=spec_from_file_location('validate_work_packets',VAL)
m=module_from_spec(spec)
spec.loader.exec_module(m)

class PacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.defs=json.loads(DEF.read_text(encoding='utf-8'))
    def fresh(self): return {'schemaVersion':1,'stateRevision':0,'packets':[],'currentPacketId':None,'nextPacketId':None}
    def test_all_16_stages_present(self):
        self.assertEqual([s['stageId'] for s in self.defs['stages']],[f'P{i:02d}' for i in range(6,22)])
    def test_all_have_bound_packets(self):
        for s in self.defs['stages']:
            self.assertGreaterEqual(len(s['packets']),4)
            for p in s['packets']:
                self.assertGreaterEqual(p['batchMax'],1)
                self.assertLessEqual(p['batchMax'],12)
                self.assertTrue(p['qcRequired'])
                self.assertEqual(p['requiresExplicitApproval'],p['approvalMode']=='SPECIAL_SEPARATE')
                self.assertIn(p['approvalMode'], ('INHERIT_MACRO','SPECIAL_SEPARATE'))
    def test_unique_templates(self):
        names=[p['templateId'] for s in self.defs['stages'] for p in s['packets']]
        self.assertEqual(len(names),len(set(names)))
    def test_empty_template_valid(self): self.assertEqual(m.validate(self.fresh(),self.defs),[])
    def test_pass_without_user_acceptance_rejected(self):
        state=self.fresh();state['packets']=[{'packetId':'P14.02.C005','stageId':'P14','status':'PASS','qcStatus':'PASS','evidencePaths':['qc/C005.md'],'planApprovalId':'a'}]
        self.assertTrue(any('acceptance approval' in e for e in m.validate(state,self.defs)))
    def test_review_ready_requires_pass_qc(self):
        state=self.fresh();state['packets']=[{'packetId':'P14.02.C005','stageId':'P14','status':'READY_FOR_REVIEW','qcStatus':'FAIL'}]
        self.assertTrue(any('review-ready' in e for e in m.validate(state,self.defs)))
    def test_pass_requires_evidence(self):
        state=self.fresh();state['packets']=[{'packetId':'P14.02.C005','stageId':'P14','status':'PASS','qcStatus':'PASS','planApprovalId':'a','acceptanceApprovalId':'b'}]
        self.assertTrue(any('without evidence' in e for e in m.validate(state,self.defs)))
    def test_duplicate_packet_ids_rejected(self):
        state=self.fresh();x={'packetId':'P14.02.C005','stageId':'P14','status':'PLANNED','qcStatus':'NOT_TESTED'};state['packets']=[x,x.copy()]
        self.assertTrue(any('duplicate' in e for e in m.validate(state,self.defs)))
    def test_traversal_rejected(self):
        state=self.fresh();state['packets']=[{'packetId':'P14.02.C005','stageId':'P14','status':'PASS','qcStatus':'PASS','evidencePaths':['../bad.md'],'outputPaths':['../../evil'],'planApprovalId':'a','acceptanceApprovalId':'b'}]
        self.assertTrue(any('invalid' in e for e in m.validate(state,self.defs)))
    def test_stale_next_packet_rejected(self):
        state=self.fresh();state['nextPacketId']='P21.01';self.assertTrue(any('nextPacketId' in e for e in m.validate(state,self.defs)))
    def test_file_check_missing(self):
        state=self.fresh();state['packets']=[{'packetId':'P14.02.C005','stageId':'P14','status':'PASS','qcStatus':'PASS','evidencePaths':['qc/missing.md'],'outputPaths':['renders/absent.mp4'],'planApprovalId':'a','acceptanceApprovalId':'b'}]
        with tempfile.TemporaryDirectory() as p: self.assertTrue(m.check_files(state,Path(p)))
    def test_valid_pass_with_files(self):
        with tempfile.TemporaryDirectory() as p:
            root=Path(p);(root/'qc').mkdir();(root/'qc/e.md').write_text('OK');(root/'out').mkdir();(root/'out/x.txt').write_text('OK')
            state=self.fresh();state['packets']=[{'packetId':'P14.02.C005','stageId':'P14','status':'PASS','qcStatus':'PASS','evidencePaths':['qc/e.md'],'outputPaths':['out/x.txt'],'planApprovalId':'a','acceptanceApprovalId':'b'}]
            self.assertEqual(m.validate(state,self.defs),[])
            self.assertEqual(m.check_files(state,root),[])
if __name__=='__main__':unittest.main()
