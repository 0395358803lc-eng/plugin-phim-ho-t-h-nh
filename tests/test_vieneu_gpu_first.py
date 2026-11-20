import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/openfilm-vieneu-tts/references/validate_gpu_decision.py'
spec = importlib.util.spec_from_file_location('validate_gpu_decision', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class GPUFirstTests(unittest.TestCase):
    def base(self):
        return json.loads((ROOT/'skills/openfilm-vieneu-tts/references/GPU_DECISION_TEMPLATE.json').read_text(encoding='utf-8'))
    def test_default_is_gpu_first_pending(self):
        x=self.base()
        self.assertEqual(x['desiredBackend'], 'cuda-pytorch')
        self.assertEqual(x['selectedBackend'], 'undecided')
        self.assertEqual(module.validate(x), [])
    def test_gpu_pass_requires_smoke_and_evidence(self):
        x=self.base();x.update(selectedBackend='cuda-pytorch',gpuAssessment='GPU_RUNTIME_PASS')
        self.assertTrue(module.validate(x))
        x.update(gpuEvidencePaths=['qc/tts/cuda.json'],runtimeGpuWavEvidence='qc/tts/gpu.wav')
        self.assertEqual(module.validate(x),[])
    def test_cpu_cannot_be_selected_when_gpu_ready(self):
        x=self.base();x.update(selectedBackend='onnx-cpu',gpuAssessment='GPU_RUNTIME_PASS',gpuEvidencePaths=['qc/gpu.json'],cpuFallbackApprovalId='approval-01',reason='short test')
        self.assertTrue(any('CPU fallback requires GPU_UNSUPPORTED' in e for e in module.validate(x)))
    def test_cpu_fallback_requires_failure_and_user_approval(self):
        x=self.base();x.update(selectedBackend='onnx-cpu',gpuAssessment='GPU_INSUFFICIENT',gpuEvidencePaths=['qc/gpu.log'],reason='OOM after safe batch reduction')
        self.assertTrue(any('cpuFallbackApprovalId' in e for e in module.validate(x)))
        x['cpuFallbackApprovalId']='approved-T07-01'
        self.assertEqual(module.validate(x), [])
    def test_cpu_fallback_no_evidence_is_rejected(self):
        x=self.base();x.update(selectedBackend='onnx-cpu',gpuAssessment='GPU_UNSUPPORTED',cpuFallbackApprovalId='approved-T07-01',reason='no cuda')
        self.assertTrue(any('gpuEvidencePaths' in e for e in module.validate(x)))
    def test_invalid_gpu_evidence_path_is_rejected(self):
        x=self.base();x.update(selectedBackend='cuda-pytorch',gpuAssessment='GPU_RUNTIME_PASS',gpuEvidencePaths=['../outside/gpu.json'],runtimeGpuWavEvidence='qc/gpu.wav')
        self.assertTrue(any('invalid' in e for e in module.validate(x)))
    def test_windows_absolute_path_is_rejected(self):
        x=self.base();x.update(selectedBackend="cuda-pytorch",gpuAssessment="GPU_RUNTIME_PASS",gpuEvidencePaths=["C:/outside.log"],runtimeGpuWavEvidence="qc/gpu.wav")
        self.assertTrue(any("invalid" in e for e in module.validate(x)))
    def test_install_policy_docs_have_no_cpu_first(self):
        for rel in ['skills/openfilm-moi-truong/SKILL.md','skills/openfilm-vieneu-tts/SKILL.md','skills/openfilm-moi-truong/references/VIENEU-TTS-WINDOWS.md']:
            body=(ROOT/rel).read_text(encoding='utf8')
            self.assertNotIn('Ưu tiên CPU ONNX',body)
            self.assertNotIn('CPU ONNX là mặc định',body)
    def test_p06_p12_gpu_gates_exist(self):
        p=ROOT/'skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json'
        x=json.loads(p.read_text(encoding='utf8'))
        ids={q['templateId'] for s in x['stages'] for q in s['packets']}
        self.assertTrue({'P06.05','P06.06','P06.07','P12.07'}.issubset(ids))

if __name__=='__main__': unittest.main()
