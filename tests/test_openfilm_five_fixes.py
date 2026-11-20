"""Offline integration-contract tests; never claim OpenFilm Windows E2E render from these."""
import copy,importlib.util,json,tempfile,unittest,wave
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(rel):
 p=ROOT/rel;sp=importlib.util.spec_from_file_location(p.stem,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
rt=load('skills/openfilm-runtime-control/references/validate_runtime_profile.py')
bs=load('skills/openfilm-runtime-control/references/bootstrap_openfilm.py')
fx=load('skills/openfilm-smoke-e2e/references/create_e2e_fixture.py')
eq=load('skills/openfilm-smoke-e2e/references/validate_e2e_report.py')
vs=load('skills/openfilm-vieneu-tts/references/validate_voice_source_lock.py')

class OpenFilmFiveFixTests(unittest.TestCase):
 def runtime(self):return json.loads((ROOT/'skills/openfilm-runtime-control/references/OPENFILM_RUNTIME_PROFILE_TEMPLATE.json').read_text(encoding='utf8'))
 def voice(self):return json.loads((ROOT/'skills/openfilm-vieneu-tts/references/VOICE_SOURCE_LOCK_TEMPLATE.json').read_text(encoding='utf8'))
 def test_runtime_template_pending_valid(self):self.assertEqual(rt.validate(self.runtime()),[])
 def test_runtime_ready_without_verified_capabilities_blocked(self):
  x=self.runtime();x.update(mode='cli',status='READY_FOR_RENDER',deviceId='xyz',workspace='D:/test',openFilmVersion='0.4',invocationMethod='cli',executablePath='C:/test/openfilm.exe',approvalId='x');self.assertTrue(rt.validate(x))
 def test_runtime_with_verified_capabilities_and_evidence(self):
  x=self.runtime();x.update(mode='cli',status='READY_FOR_RENDER',deviceId='xyz',workspace='D:/test',openFilmVersion='0.4',invocationMethod='cli',executablePath='C:/test/openfilm.exe',workingDirectory='D:/test/projects/film/openfilm',approvalId='x')
  for name in ('openProject','inspectFrame','renderClip'):x['capabilities'][name]={'status':'VERIFIED','evidencePaths':[f'qc/openfilm/{name}.txt']}
  self.assertEqual(rt.validate(x),[])
 def test_runtime_verified_missing_evidence_rejected(self):
  x=self.runtime();x['capabilities']['renderClip']['status']='VERIFIED';self.assertTrue(any('without evidence' in err for err in rt.validate(x)))
 def test_runtime_path_traversal_rejected(self):
  x=self.runtime();x['capabilities']['openCanvas']={'status':'VERIFIED','evidencePaths':['../../outside.txt']};self.assertTrue(rt.validate(x))
 def test_runtime_real_evidence_files_needed(self):
  x=self.runtime();x['capabilities']['openProject']={'status':'VERIFIED','evidencePaths':['qc/openfilm/open.log']}
  with tempfile.TemporaryDirectory() as tmp:self.assertTrue(rt.check_files(x,tmp))
 def test_voice_template_pending_gpu_first(self):
  x=self.voice();self.assertEqual(x['backend'],'cuda-pytorch');self.assertEqual(vs.validate(x),[])
 def test_voice_onnx_without_cpu_fallback_not_allowed(self):
  x=self.voice();x['backend']='onnx-cpu';self.assertTrue(vs.validate(x))
 def test_voice_onnx_with_approved_gpu_fallback(self):
  x=self.voice();x['backend']='onnx-cpu';gpu={'cpuFallbackApprovalId':'T07-approved','selectedBackend':'onnx-cpu','gpuAssessment':'GPU_INSUFFICIENT'};self.assertEqual(vs.validate(x,gpu),[])
 def test_voice_lock_cannot_enable_openfilm_tts(self):
  x=self.voice();x['openFilmTtsAllowed']=True;self.assertTrue(vs.validate(x))
 def test_locked_vieneu_without_gpu_runtime_rejected(self):
  x=self.voice();x.update(status='LOCKED',approvalId='a',evidencePaths=['reports/tts/lock.md'],modelRevision='v3turbo-r1',voicePresetIds=['voice-one'])
  self.assertTrue(any('GPU decision' in e for e in vs.validate(x)))
 def test_locked_vieneu_with_gpu_runtime_pass(self):
  x=self.voice();x.update(status='LOCKED',approvalId='a',evidencePaths=['reports/tts/lock.md'],modelRevision='v3turbo-r1',voicePresetIds=['voice-one'])
  gpu={'selectedBackend':'cuda-pytorch','gpuAssessment':'GPU_RUNTIME_PASS','runtimeGpuWavEvidence':'qc/tts/gpu.wav'}
  self.assertEqual(vs.validate(x,gpu),[])
 def test_voice_alternate_requires_approval(self):
  x=self.voice();x.update(source='alternate-approved',backend='alternate');self.assertTrue(vs.validate(x));x['alternateProviderApprovalId']='explicit-user-approved';self.assertEqual(vs.validate(x),[])
 def film_setup(self,tmp):
  r=Path(tmp);proj=r/'projects/film-1';proj.mkdir(parents=True);data=proj/'film.json';data.write_text(json.dumps({'schemaVersion':1,'filmId':'film-1','fps':30,'width':1280,'height':720,'durationInFrames':240,'shots':[{'id':'C001','startFrame':0,'durationInFrames':90},{'id':'C002','startFrame':90,'durationInFrames':150}],'dialogues':[]}),encoding='utf-8');return r,proj,data
 def test_bootstrap_dry_run_does_not_write(self):
  with tempfile.TemporaryDirectory() as tmp:
   r,p,data=self.film_setup(tmp);x=bs.build(r,p,data,False);self.assertEqual(x['status'],'PLAN');self.assertFalse((p/'openfilm').exists())
 def test_bootstrap_creates_early_timeline(self):
  with tempfile.TemporaryDirectory() as tmp:
   r,p,data=self.film_setup(tmp);x=bs.build(r,p,data,True)
   self.assertEqual(x['sceneCount'],2);self.assertTrue((p/'openfilm/film.html').is_file());film=(p/'openfilm/film.html').read_text();self.assertIn('scenes/C001.html#t=0,3',film);self.assertIn('at="3.000000"',film)
   self.assertEqual(len(bs.check_ready(p,data)),2)
 def test_bootstrap_no_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   r,p,data=self.film_setup(tmp);bs.build(r,p,data,True)
   with self.assertRaises(FileExistsError):bs.build(r,p,data,True)
 def test_bootstrap_rejects_path_escape(self):
  with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
   r,p,data=self.film_setup(tmp)
   with self.assertRaises(ValueError):bs.build(r,Path(outside),data,True)
 def test_bootstrap_reject_symlink_to_outside(self):
  with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
   r,p,data=self.film_setup(tmp);make_link(self,p/'openfilm',Path(outside))
   with self.assertRaises(ValueError):bs.build(r,p,data,True)
 def test_e2e_fixture_reject_symlink_to_outside(self):
  with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
   root=Path(tmp)/'qc/openfilm-e2e/fixture';root.mkdir(parents=True);make_link(self,root/'scenes',Path(outside))
   with self.assertRaises(ValueError):fx.build(tmp,True)
 def test_bootstrap_check_ready_after_scene_replaced(self):
  with tempfile.TemporaryDirectory() as tmp:
   r,p,data=self.film_setup(tmp);bs.build(r,p,data,True)
   for i in ('C001','C002'):(p/'openfilm/scenes'/f'{i}.html').write_text('<html><script>window.film={frame(t){}}</script></html>',encoding='utf8')
   self.assertEqual(bs.check_ready(p,data),[])
 def test_fixture_dry_run_no_disk_write(self):
  with tempfile.TemporaryDirectory() as tmp:
   x=fx.build(tmp);self.assertEqual(x['status'],'PLAN');self.assertFalse((Path(tmp)/fx.REL).exists())
 def test_fixture_contains_html_moving_ball_wav_48k_and_vtt(self):
  with tempfile.TemporaryDirectory() as tmp:
   x=fx.build(tmp,True);root=Path(tmp)/fx.REL
   self.assertEqual(x['status'],'CREATED');self.assertIn('window.film', (root/'scenes/probe.html').read_text(encoding='utf8'))
   self.assertIn('probe-tone.wav', (root/'film.html').read_text(encoding='utf8'))
   self.assertTrue((root/'captions/probe.vtt').read_text().startswith('WEBVTT'))
   with wave.open(str(root/'audio/probe-tone.wav'),'rb') as w:
    self.assertEqual(w.getframerate(),48000);self.assertEqual(w.getnframes(),120000)
 def test_fixture_no_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   fx.build(tmp,True)
   with self.assertRaises(FileExistsError):fx.build(tmp,True)
 def test_e2e_template_cannot_falsely_pass(self):
  x=json.loads((ROOT/'skills/openfilm-smoke-e2e/references/E2E_REPORT_TEMPLATE.json').read_text(encoding='utf-8'));self.assertEqual(eq.validate(x),[])
  x['status']='PASS';self.assertTrue(eq.validate(x))
 def test_e2e_remotion_output_cannot_claim_openfilm(self):
  x=json.loads((ROOT/'skills/openfilm-smoke-e2e/references/E2E_REPORT_TEMPLATE.json').read_text(encoding='utf-8'));x['engine']='remotion';self.assertTrue(eq.validate(x))
 def test_e2e_false_pass_media_missing(self):
  x=json.loads((ROOT/'skills/openfilm-smoke-e2e/references/E2E_REPORT_TEMPLATE.json').read_text(encoding='utf-8'));x.update(status='PASS',planApprovalId='A',acceptanceApprovalId='B',visualReview='PASS',audioReview='PASS',captionReview='PASS',reviewEvidencePaths=['qc/review.txt'])
  with tempfile.TemporaryDirectory() as tmp:self.assertTrue(eq.check_files(x,tmp))
 def test_packet_templates_integrated_and_ordered(self):
  defs=json.loads((ROOT/'skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json').read_text(encoding='utf-8'));stages={s['stageId']:s['packets'] for s in defs['stages']};ids=[p['templateId'] for s in defs['stages'] for p in s['packets']]
  for stage,seq in {'P06':[f'P06.{n:02}' for n in (8,9,10,11,4)],'P08':['P08.05'],'P09':['P09.06'],'P10':['P10.06','P10.07'],'P12':['P12.08','P12.03'],'P16':['P16.06','P16.05'],'P17':['P17.07']}.items():
   tpl=[p['templateId'] for p in stages[stage]]
   for item in seq:self.assertIn(item,tpl)
   self.assertEqual([tpl.index(i) for i in seq],sorted(tpl.index(i) for i in seq))
  self.assertTrue(next(p for p in stages['P06'] if p['templateId']=='P06.10')['specialApprovalRequired'])
  self.assertEqual(len(ids),len(set(ids)))
 def test_p16_before_p17_and_p09_scaffold(self):
  x=json.loads((ROOT/'skills/openfilm-production-p06-p21/references/STAGE_DEFINITIONS.json').read_text(encoding='utf-8'));d={s['id']:s for s in x['stages']}
  self.assertTrue(d['P17']['existingTimelineOnly']);self.assertEqual(d['P09']['earlyOpenFilmProject'],'projects/<film-id>/openfilm/film.html')
  self.assertIn('Actual scene code',d['P16']['beforeP17'])
 def test_all_skill_files_have_yaml_frontmatter(self):
  files=list((ROOT/'skills').glob('*/SKILL.md'));self.assertGreaterEqual(len(files),28)
  for p in files:self.assertTrue(p.read_text(encoding='utf8').startswith('---\n'),p)

if __name__=='__main__':unittest.main()


def make_link(test, link, target):
 try: link.symlink_to(target,target_is_directory=True)
 except OSError as exc:
  if getattr(exc,"winerror",None)==1314:test.skipTest("Windows symlink privilege unavailable; no system change authorized")
  raise
