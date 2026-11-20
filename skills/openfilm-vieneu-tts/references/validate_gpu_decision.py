#!/usr/bin/env python3
"""Validate GPU-first VieNeu-TTS backend decision reports (stdlib only; read-only)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath

_ALLOWED = {"NOT_VERIFIED", "GPU_CANDIDATE", "GPU_RUNTIME_PASS", "GPU_UNSUPPORTED", "GPU_INSUFFICIENT", "GPU_FAILED"}
_DEFICIENT = {"GPU_UNSUPPORTED", "GPU_INSUFFICIENT", "GPU_FAILED"}

def safe_relative(path: object) -> bool:
    if not isinstance(path, str) or not path or "\\" in path:
        return False
    posix = PurePosixPath(path)
    windows = PureWindowsPath(path)
    return not posix.is_absolute() and not windows.is_absolute() and not windows.drive and ".." not in posix.parts and ".." not in windows.parts

def validate(data: dict) -> list[str]:
    e = []
    if not isinstance(data, dict):
        return ["report must be JSON object"]
    if data.get("schemaVersion") != 1:
        e.append("schemaVersion must be 1")
    if data.get("desiredBackend") != "cuda-pytorch":
        e.append("desiredBackend must remain cuda-pytorch (GPU-first)")
    assessment = data.get("gpuAssessment")
    if assessment not in _ALLOWED:
        e.append("gpuAssessment invalid")
    selected = data.get("selectedBackend")
    if selected not in {"undecided", "cuda-pytorch", "onnx-cpu"}:
        e.append("selectedBackend invalid")
    evidence = data.get("gpuEvidencePaths")
    if not isinstance(evidence, list) or not all(safe_relative(x) for x in evidence):
        e.append("gpuEvidencePaths invalid")
        evidence = []
    if selected == "cuda-pytorch":
        if assessment != "GPU_RUNTIME_PASS":
            e.append("CUDA selection requires GPU_RUNTIME_PASS")
        wav = data.get("runtimeGpuWavEvidence")
        if not safe_relative(wav):
            e.append("CUDA selection requires runtimeGpuWavEvidence")
        if not evidence:
            e.append("CUDA selection requires gpuEvidencePaths")
    if selected == "onnx-cpu":
        if assessment not in _DEFICIENT:
            e.append("CPU fallback requires GPU_UNSUPPORTED/INSUFFICIENT/FAILED")
        if not evidence:
            e.append("CPU fallback requires gpuEvidencePaths")
        if not isinstance(data.get('cpuFallbackApprovalId'),str) or not data.get('cpuFallbackApprovalId'):
            e.append("CPU fallback requires cpuFallbackApprovalId")
        if not data.get('reason'):
            e.append("CPU fallback requires reason")
    if selected == "undecided" and data.get('cpuFallbackApprovalId'):
        e.append("pending state cannot pre-authorize CPU")
    return e

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('report',type=Path)
    args=ap.parse_args()
    issues=validate(json.loads(args.report.read_text(encoding='utf-8')))
    if issues:
        print('\n'.join('FAIL: '+x for x in issues))
        raise SystemExit(1)
    print('PASS: GPU-first backend decision schema')
if __name__=='__main__': main()
