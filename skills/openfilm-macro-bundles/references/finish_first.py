"""Technical completion only. No creative QC, execution, or implicit consent."""
from __future__ import annotations
import hashlib
import json
import re
import shutil
import subprocess
import wave
import zipfile
from pathlib import Path

MODE = 'FINISH_FIRST_USER_REVIEW'
READY = {'OUTPUT_READY', 'DELIVERED_FOR_REVIEW', 'USER_ACCEPTED'}
LEGACY_READY = {'PASS', 'QC_PASS', 'READY_FOR_REVIEW'}
STATES = READY | {'NOT_STARTED', 'PLANNED', 'WAITING_APPROVAL', 'APPROVED',
                  'IN_PROGRESS', 'SKIPPED', 'REVISION_REQUESTED', 'FAILED_TECHNICAL',
                  'BLOCKED', 'INVALIDATED', 'VISUAL_BLOCKED', 'FAIL'} | LEGACY_READY
SPECIAL = {'PACKAGE_INSTALL', 'MODEL_DOWNLOAD', 'BROWSER_DOWNLOAD', 'SYSTEM_CHANGE',
           'GPU_TO_CPU_FALLBACK', 'VOICE_CLONING', 'EXTERNAL_PROVIDER', 'PAID_ACTION',
           'DELETE', 'PUBLISH', 'OUT_OF_SCOPE'}

def enabled(state):
    return state.get('productionMode', MODE) != 'LEGACY_QC'

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def confined(root, relative):
    if not root or not Path(root).is_absolute() or not Path(root).is_dir():
        raise ValueError('workspace must be an existing absolute directory')
    if not isinstance(relative, str) or not relative or any(c in relative for c in ':\x00<>'):
        raise ValueError('unsafe relative path')
    parts = relative.replace('\\', '/').split('/')
    if any(p in ('', '.', '..') or p.rstrip(' .') != p or
           p.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}
           for p in parts):
        raise ValueError('unsafe relative path')
    root = Path(root).resolve()
    candidate = root.joinpath(*parts).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError('path outside workspace')
    return candidate

def command(args):
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
    if result.returncode:
        raise ValueError('media decode/probe failed: ' + result.stderr[-500:])
    return result.stdout

def check_file(root, relative, expected=None, *, require_audio=False):
    """Read and decode required artifacts; never rate appearance or voice quality."""
    try:
        p = confined(root, relative)
        if not p.is_file() or not p.stat().st_size:
            raise ValueError('missing or empty file')
        if expected is not None and (not isinstance(expected, str) or
                not re.fullmatch('[0-9a-fA-F]{64}', expected) or digest(p) != expected.lower()):
            raise ValueError('source/output hash mismatch')
        suffix = p.suffix.lower()
        if suffix == '.json':
            json.loads(p.read_text(encoding='utf-8'))
        elif suffix == '.wav':
            with wave.open(str(p), 'rb') as w:
                n = w.getnframes()
                if n <= 0 or w.getframerate() <= 0 or len(w.readframes(n)) != n*w.getnchannels()*w.getsampwidth():
                    raise ValueError('invalid/truncated WAV')
        elif suffix in ('.srt', '.vtt'):
            text = p.read_text(encoding='utf-8-sig')
            if suffix == '.vtt' and not text.startswith('WEBVTT'):
                raise ValueError('VTT header missing')
            cues = re.findall(r'((?:\d+:)?\d{2}:\d{2}[.,]\d{3})\s+-->\s+((?:\d+:)?\d{2}:\d{2}[.,]\d{3})[^\n]*\n([^\n]+)', text)
            def seconds(t):
                fields = t.replace(',', '.').split(':')
                return sum(float(x)*60**i for i,x in enumerate(reversed(fields)))
            if not cues or any(seconds(b) <= seconds(a) or not caption.strip() for a,b,caption in cues):
                raise ValueError('invalid subtitle cues')
        elif suffix in ('.html', '.js', '.tsx', '.jsx', '.ts'):
            text = p.read_text(encoding='utf-8')
            if not text.strip() or 'data-placeholder="true"' in text:
                raise ValueError('scene source missing/placeholder')
            if suffix == '.html' and not re.search(r'<(?:html|div|svg|canvas|script)\b', text, re.I):
                raise ValueError('invalid scene HTML')
        elif suffix == '.zip':
            with zipfile.ZipFile(p) as z:
                if not z.namelist() or z.testzip():
                    raise ValueError('invalid ZIP')
                for name in z.namelist():
                    confined(root, name.rstrip('/'))
        elif suffix in ('.mp4', '.mov', '.png', '.jpg', '.jpeg', '.webp'):
            ffprobe, ffmpeg = shutil.which('ffprobe'), shutil.which('ffmpeg')
            if not ffprobe or not ffmpeg:
                raise ValueError('existing ffprobe and ffmpeg required; do not auto-install')
            info = json.loads(command([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)]))
            kinds = {s.get('codec_type') for s in info.get('streams', [])}
            if 'video' not in kinds or (require_audio and 'audio' not in kinds):
                raise ValueError('required video/audio stream missing')
            if suffix in ('.mp4', '.mov') and float(info.get('format', {}).get('duration', 0)) <= 0:
                raise ValueError('video duration invalid')
            command([ffmpeg, '-nostdin', '-v', 'error', '-xerror', '-i', str(p), '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-'])
        return []
    except (OSError, ValueError, TypeError, EOFError, wave.Error, zipfile.BadZipFile, subprocess.SubprocessError) as exc:
        return [f'{relative}: {exc}']

def outputs(row):
    paths = row.get('outputPaths', [])
    hashes = dict(row.get('outputHashes', {}))
    if not paths and row.get('outputs'):
        paths = [o['path'] for o in row['outputs']]
        hashes.update({o['path']:o.get('sha256') for o in row['outputs']})
    return paths, hashes

def completion_errors(row, root, *, legacy=False):
    if row.get('status') == 'SKIPPED':
        return [] if row.get('skipReason') else ['SKIPPED requires reason']
    if row.get('status') not in READY | (LEGACY_READY if legacy else set()):
        return ['output not ready']
    paths, hashes = outputs(row)
    if not paths:
        return ['required output files not declared']
    errors = []
    for p in paths:
        if not hashes.get(p):
            errors.append(f'{p}: output checksum missing')
        errors += check_file(root, p, hashes.get(p), require_audio=row.get('requiresAudio', False))
    return errors

def scope_digest(bundle):
    keys = ('macroId','macroIds','stageIds','packetIds','scopeIds','allowedPaths','allowedCommands','riskClass','inputHashes','specialApprovalRequired')
    return hashlib.sha256(json.dumps({k:bundle.get(k) for k in keys}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def user_event(event):
    return bool(event.get('approvalId') and event.get('source') in ('USER_CHAT','HOST_BUTTON') and event.get('at'))

def authorized(bundle):
    return bool(bundle.get('planApprovalId') and bundle.get('approvedScopeSha256') == scope_digest(bundle))

def packet_scope_errors(packet, bundle, policy):
    errors=[]
    for pk,bk in (('scopeIds','scopeIds'),('allowedCommands','allowedCommands')):
        if not set(packet.get(pk,[])).issubset(bundle.get(bk,[])):
            errors.append(f'packet {pk} outside approved scope')
    if not set(packet.get('inputPaths',[])+packet.get('outputPaths',[])).issubset(bundle.get('allowedPaths',[])):
        errors.append('packet paths outside approved scope')
    risk=packet.get('riskClass','NORMAL')
    if risk not in SPECIAL | {'NORMAL'}:
        errors.append('unknown risk class')
    special = risk in SPECIAL or packet.get('specialApprovalRequired')
    if special and (not bundle.get('specialApprovalRequired') or not bundle.get('specialApprovalId') or len(bundle.get('packetIds',[])) != 1):
        errors.append('special action requires separate approval')
    if risk != bundle.get('riskClass'):
        errors.append('riskClass mismatch')
    elevated = r'\b(npx|install|download|publish|remove-item|delete|rmdir|curl|wget|set-executionpolicy)\b'
    if not special and any(re.search(elevated,c,re.I) for c in packet.get('allowedCommands',[])):
        errors.append('elevated command requires separate approval')
    return errors

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Verify a real output without creative QC')
    parser.add_argument('--workspace',required=True)
    parser.add_argument('--path',required=True,help='Exact workspace-relative file')
    parser.add_argument('--sha256')
    parser.add_argument('--require-audio',action='store_true')
    args=parser.parse_args()
    errors=check_file(args.workspace,args.path,args.sha256,require_audio=args.require_audio)
    print(json.dumps({'status':'OUTPUT_READY' if not errors else 'FAILED_TECHNICAL','errors':errors},ensure_ascii=False,indent=2))
    raise SystemExit(2 if errors else 0)
