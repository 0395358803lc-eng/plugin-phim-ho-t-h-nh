"""Static tests only: no video / remote device / model execution."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(rel,name):
    p=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

audit=load('skills/openfilm-script-input/references/audit_seven_files.py','vhh_audit')
state=load('skills/openfilm-checkpoint-approval/references/validate_production_state.py','vhh_state')

class TestPipelineContract(unittest.TestCase):
    def setUp(self):
        self.template=json.loads((ROOT/'skills/openfilm-checkpoint-approval/references/PRODUCTION_STATUS_TEMPLATE.json').read_text(encoding='utf-8'))

    def test_stage_ids_are_exact_and_ordered(self):
        specs=json.loads((ROOT/'skills/openfilm-production-p06-p21/references/STAGE_DEFINITIONS.json').read_text(encoding='utf-8'))['stages']
        self.assertEqual([s['id'] for s in specs],state.IDS)
        self.assertEqual([s['id'] for s in self.template['stages']],state.IDS)

    def test_initial_template_has_no_fake_completion(self):
        self.assertEqual(state.validate(self.template),[])
        self.assertTrue(all(s['status']=='NOT_STARTED' and s['qcStatus']=='NOT_TESTED' for s in self.template['stages']))

    def test_p07_cannot_be_completed_without_environment_gate(self):
        p07=self.template['stages'][1]
        p07['status']='PASS';p07['qcStatus']='PASS';p07['evidence']=['reports/INPUT_AUDIT.md']
        p07['acceptanceApproval']=self._approved()
        self.assertTrue(any('before previous stage' in e for e in state.validate(self.template)))

    def test_p07_read_only_audit_can_pass_after_p06_skipped_and_accepted(self):
        p06=self.template['stages'][0]
        p06['status']='SKIPPED';p06['skipReason']='No installation needed; environment verified';p06['evidence']=['reports/ENV_ACCEPTANCE.md'];p06['acceptanceApproval']=self._approved()
        p07=self.template['stages'][1]
        p07['status']='PASS';p07['qcStatus']='PASS';p07['evidence']=['reports/INPUT_AUDIT.md'];p07['acceptanceApproval']=self._approved()
        self.assertEqual(state.validate(self.template),[])

    def test_fake_p21_pass_is_rejected(self):
        s=self.template['stages'][-1];s['status']='PASS'
        self.assertTrue(any('P21 PASS without' in e for e in state.validate(self.template)))

    def test_cannot_skip_mandatory_p20(self):
        s=self.template['stages'][-2];s['status']='SKIPPED';s['skipReason']='Not convenient';s['evidence']=['qc/QC20_REPORT.md'];s['acceptanceApproval']=self._approved()
        self.assertIn('P20 cannot be skipped',state.validate(self.template))

    def test_input_audit_all_files_and_csv(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in audit.REQUIRED:
                content='content' if name!='DANH_SACH_CANH.csv' else 'Ma canh,Noi dung,Thoi luong\nC001,Mo dau,5\n'
                (p/name).write_text(content,encoding='utf-8')
            r=audit.audit(p)
            self.assertEqual(r['status'],'PASS')
            self.assertEqual(len(r['files']),7)
            self.assertTrue(all(f['sha256'] and f['bytes']>0 for f in r['files']))
            self.assertEqual(next(f for f in r['files'] if f['name'].endswith('.csv'))['csvRows'],1)

    def test_input_missing_does_not_create_or_fake(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)
            result=audit.audit(p)
            self.assertEqual(result['status'],'BLOCKED')
            self.assertEqual(len(result['issues']),7)
            self.assertEqual(list(p.iterdir()),[])

    def test_csv_bom_semicolon_and_two_rows(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in audit.REQUIRED:
                raw='content' if name!='DANH_SACH_CANH.csv' else 'Mã cảnh;Nội dung;Thời lượng\nC001;Mở đầu;5\nC002;Kết;3\n'
                (p/name).write_text(raw,encoding='utf-8-sig')
            result=audit.audit(p)
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(next(f for f in result['files'] if f['name'].endswith('.csv'))['csvDelimiter'],';')

    def test_fake_evidence_file_rejected_by_optional_disk_check(self):
        s=self.template['stages'][0]
        s['status']='SKIPPED';s['skipReason']='All runtimes found';s['evidence']=['reports/ENV_ACCEPTANCE.md'];s['acceptanceApproval']=self._approved()
        with TemporaryDirectory() as tmp:
            self.assertTrue(any('missing/outside workspace' in x for x in state.validate_files(self.template,Path(tmp))))
            r=Path(tmp)/'reports';r.mkdir()
            (r/'ENV_ACCEPTANCE.md').write_text('verified',encoding='utf-8')
            self.assertEqual(state.validate_files(self.template,Path(tmp)),[])

    def test_traversal_evidence_path_is_rejected(self):
        s=self.template['stages'][0]
        s['status']='SKIPPED';s['skipReason']='All runtimes found';s['evidence']=['../../secret.txt'];s['acceptanceApproval']=self._approved()
        with TemporaryDirectory() as tmp:
            self.assertTrue(any('invalid evidence path' in x for x in state.validate_files(self.template,Path(tmp))))

    @staticmethod
    def _approved():
        return {'status':'APPROVED','approvalId':'ack-001','scope':'P06 approval','source':'chat','at':'2026-11-19T10:00:00+07:00'}

if __name__=='__main__':unittest.main()
