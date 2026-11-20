"""CLI-first policy regression; no Windows commands are executed."""
import json, importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(rel):return (ROOT/rel).read_text(encoding='utf-8')
def load(rel):
 p=ROOT/rel;sp=importlib.util.spec_from_file_location(p.stem,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
class OpenfilmCLIFirst(unittest.TestCase):
 def test_cli_policy_skill(self):
  s=read('skills/openfilm-cli-execution/SKILL.md')
  for tok in ('CLI-first','P04','P05','P06','openfilm look','openfilm render','workingDirectory','approval','exitCode','Desktop'):
   self.assertIn(tok,s)
 def test_main_cli_priority(self):
  s=read('skills/video-hoat-hinh/SKILL.md')
  self.assertIn('CLI_ONLY_FOR_OPENFILM',s)
  self.assertIn('openfilm-cli-execution',s)
 def test_read_only_audit_requires_cli(self):
  s=read('skills/openfilm-moi-truong/SKILL.md')
  self.assertIn('A02',s)
  self.assertIn('CLI_REQUIRED',s)
  self.assertIn('A01',s)
 def test_runtime_ready_reject_desktop(self):
  m=load('skills/openfilm-runtime-control/references/validate_runtime_profile.py')
  x=json.loads(read('skills/openfilm-runtime-control/references/OPENFILM_RUNTIME_PROFILE_TEMPLATE.json'))
  x.update(mode='desktop-ui',status='READY_FOR_RENDER',deviceId='x',workspace=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE',openFilmVersion='0.4',invocationMethod='desktop',executablePath=r'D:\test.exe',approvalId='ok')
  self.assertTrue(any('CLI' in v or 'mode' in v for v in m.validate(x)))
 def test_runtime_cli_verified(self):
  m=load('skills/openfilm-runtime-control/references/validate_runtime_profile.py')
  x=json.loads(read('skills/openfilm-runtime-control/references/OPENFILM_RUNTIME_PROFILE_TEMPLATE.json'))
  x.update(mode='cli',status='READY_FOR_RENDER',deviceId='x',workspace=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE',openFilmVersion='0.4.0',invocationMethod='absolute-path',executablePath=r'D:\tools\openfilm.cmd',approvalId='ok',workingDirectory=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE\projects\film\openfilm')
  for k in ('openProject','inspectFrame','renderClip'):
   x['capabilities'][k]={'status':'VERIFIED','evidencePaths':[f'qc/openfilm/{k}.log']}
  self.assertEqual(m.validate(x),[])
 def test_runtime_cli_wrong_cwd_block(self):
  m=load('skills/openfilm-runtime-control/references/validate_runtime_profile.py')
  x=json.loads(read('skills/openfilm-runtime-control/references/OPENFILM_RUNTIME_PROFILE_TEMPLATE.json'))
  x.update(mode='cli',status='READY_FOR_RENDER',deviceId='x',workspace=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE',openFilmVersion='0.4.0',invocationMethod='absolute-path',executablePath=r'D:\tools\openfilm.cmd',approvalId='ok',workingDirectory=r'D:\other')
  for k in ('openProject','inspectFrame','renderClip'):x['capabilities'][k]={'status':'VERIFIED','evidencePaths':[f'qc/openfilm/{k}.log']}
  self.assertTrue(m.validate(x))
 def test_cli_event_template_pending(self):
  m=load('skills/openfilm-cli-execution/references/validate_cli_run.py')
  x=json.loads(read('skills/openfilm-cli-execution/references/CLI_RUN_TEMPLATE.json'))
  self.assertEqual(m.validate(x),[])
 def test_cli_run_ready_command(self):
  m=load('skills/openfilm-cli-execution/references/validate_cli_run.py')
  x=json.loads(read('skills/openfilm-cli-execution/references/CLI_RUN_TEMPLATE.json'))
  x.update(status='PASS',deviceId='x',workspace=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE',cwd=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE\projects\film\openfilm',executablePath=r'D:\tools\openfilm.cmd',openFilmVersion='0.4.0',command='look',args=['0'],stageId='P16',packetId='P16.01.C001',approvalId='x',exitCode=0,logPath='logs/cli/look-0.log',evidencePaths=['qc/look/frame0.png'])
  self.assertEqual(m.validate(x),[])
  x['cwd']=r'D:\outside';self.assertTrue(m.validate(x))
  x['cwd']=r'D:\A\VIDEO_HOAT_HINH_WORKSPACE\projects\film\openfilm';x['args']=['& calc'];self.assertTrue(m.validate(x))
  x['args']=['0'];x['executablePath']='npx -y openfilm@latest';self.assertTrue(m.validate(x))
 def test_e2e_pass_requires_cli(self):
  m=load('skills/openfilm-smoke-e2e/references/validate_e2e_report.py')
  x=json.loads(read('skills/openfilm-smoke-e2e/references/E2E_REPORT_TEMPLATE.json'))
  x.update(status='PASS',planApprovalId='A',acceptanceApprovalId='B',visualReview='PASS',audioReview='PASS',captionReview='PASS',reviewEvidencePaths=['qc/review.txt'])
  self.assertTrue(any('CLI' in z for z in m.validate(x)))
 def test_packet_cli_gates(self):
  j=json.loads(read('skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json'))
  p={k['templateId']:k for s in j['stages'] for k in s['packets']}
  for a in ('P06.12','P16.07','P18.05','P21.06'):self.assertIn(a,p)
  self.assertFalse(p['P06.12']['requiresExplicitApproval'])
  self.assertEqual(p['P06.12']['approvalMode'],'INHERIT_MACRO')
  self.assertTrue(p['P06.10']['requiresExplicitApproval'])
  self.assertEqual(p['P06.10']['approvalMode'],'SPECIAL_SEPARATE')
 def test_remotion_master_still_possible(self):
  s=read('skills/openfilm-hybrid-master/SKILL.md');self.assertIn('Remotion Master',s);self.assertIn('OpenFilm CLI',s)
if __name__=='__main__':unittest.main()
