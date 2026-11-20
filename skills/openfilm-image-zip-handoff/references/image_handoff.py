#!/usr/bin/env python3
"""Produce or verify a provenance-bearing, workspace-relative image ZIP handoff.

No remote writes. Uses stdlib only. Outputs a ZIP containing exact workspace-relative
PNG paths and handoffs/<id>/MANIFEST.json + HUONG_DAN.txt.
"""
import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
import zlib
from pathlib import Path, PurePosixPath

PNG_SIG = b'\x89PNG\r\n\x1a\n'
HANDOFF_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{2,79}$')
MAX_IMAGE = 60 * 1024 * 1024
MAX_PIXELS = 90_000_000
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def safe_rel(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('INVALID_RELATIVE_PATH')
    p = PurePosixPath(value)
    if p.is_absolute() or str(p) != value or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('UNSAFE_RELATIVE_PATH')
    if any(s.rstrip(' .') != s or s.split('.')[0].upper() in WINDOWS_RESERVED for s in p.parts):
        raise ValueError('WINDOWS_UNSAFE_FILENAME')
    if len(value) > 245:
        raise ValueError('PATH_TOO_LONG')
    return value


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def png_info(payload):
    if len(payload) < 57 or not payload.startswith(PNG_SIG):
        raise ValueError('NOT_A_PNG')
    pos, width, height, chunk_count, saw_ihdr, saw_iend = 8, None, None, 0, False, False
    while pos < len(payload):
        if pos + 12 > len(payload):
            raise ValueError('TRUNCATED_PNG')
        length = int.from_bytes(payload[pos:pos + 4], 'big')
        ctype = payload[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(payload) or length > MAX_IMAGE:
            raise ValueError('BAD_PNG_CHUNK')
        chunk_data = payload[pos + 8:pos + 8 + length]
        recorded_crc = int.from_bytes(payload[pos + 8 + length:end], 'big')
        calc_crc = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if recorded_crc != calc_crc:
            raise ValueError('PNG_CRC_MISMATCH')
        chunk_count += 1
        if not saw_ihdr:
            if ctype != b'IHDR' or length != 13:
                raise ValueError('PNG_IHDR_MISSING')
            width, height = struct.unpack('>II', chunk_data[:8])
            if not 1 <= width <= 16384 or not 1 <= height <= 16384 or width * height > MAX_PIXELS:
                raise ValueError('INVALID_IMAGE_DIMENSIONS')
            saw_ihdr = True
        if ctype == b'IEND':
            if length != 0 or end != len(payload):
                raise ValueError('INVALID_PNG_END')
            saw_iend = True
            break
        pos = end
    if not saw_iend or chunk_count < 3:
        raise ValueError('INCOMPLETE_PNG')
    return width, height


def build(spec_path, output_path):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    handoff_id = spec.get('handoffId')
    if not isinstance(handoff_id, str) or not HANDOFF_RE.fullmatch(handoff_id):
        raise ValueError('INVALID_HANDOFF_ID')
    target_workspace = spec.get('targetWorkspace')
    if not isinstance(target_workspace, str) or not target_workspace or not target_workspace.endswith('VIDEO_HOAT_HINH_WORKSPACE'):
        raise ValueError('MISSING_EXACT_WORKSPACE_ROOT')
    files = spec.get('images')
    if not isinstance(files, list) or not files or len(files) > 25:
        raise ValueError('IMAGE_COUNT_INVALID')
    prefix = f'handoffs/{handoff_id}/'
    targets = set()
    records = []
    contents = {}
    for entry in files:
        src = Path(entry['inputPng'])
        if not src.is_file() or src.is_symlink() or src.stat().st_size > MAX_IMAGE:
            raise ValueError('MISSING_OR_UNSAFE_INPUT_PNG')
        target = safe_rel(entry['targetRelativePath'])
        if not target.lower().endswith('.png') or not target.startswith('projects/'):
            raise ValueError('TARGET_MUST_BE_PROJECT_PNG')
        if target.casefold() in targets:
            raise ValueError('DUPLICATE_TARGET')
        targets.add(target.casefold())
        data = src.read_bytes()
        w, h = png_info(data)
        contents[target] = data
        records.append({
            'targetId': entry.get('targetId', src.stem),
            'targetRelativePath': target,
            'pngSha256': sha_bytes(data),
            'byteCount': len(data),
            'width': w, 'height': h,
            'sourceTextPath': entry.get('sourceTextPath'),
            'sourceTextSha256': entry.get('sourceTextSha256'),
            'status': 'PENDING_USER_EXTRACTION_AND_REMOTE_IMAGE_REVIEW',
            'imageActuallyReceivedFromWindows': False,
        })
    manifest_rel = prefix + 'MANIFEST.json'
    guide_rel = prefix + 'HUONG_DAN_GIAI_NEN.txt'
    manifest = {
        'schemaVersion': 1, 'handoffId': handoff_id,
        'targetWorkspaceRootWindows': target_workspace,
        'manifestRelativePath': manifest_rel,
        'images': records,
        'packageStatus': 'ZIP_CREATED_FOR_USER_DOWNLOAD',
        'remoteFileVerification': 'PENDING',
        'visualQC': 'NOT_STARTED',
        'userMacroAcceptance': False,
        'notes': 'No remote PNG or image receipt is implied. ImageGen chat previews are not remote evidence.',
    }
    instructions = f'''VIDEO-HOAT-HINH: HUONG DAN GIAI NEN ANH\n\n1. Tai ZIP tu tin nhan ChatGPT.\n2. Giai nen NOI DUNG ZIP (khong them thu muc long nhau) tai:\n   {target_workspace}\n3. Sau giai nen, duong dan anh se la:\n''' + ''.join(f'   {target_workspace}\\{row["targetRelativePath"].replace("/", chr(92))}\n' for row in records) + f'''\n4. Khong doi ten file. Khong ghi de anh cu neu chua duoc phe duyet.\n5. Quay lai ChatGPT, bao "Da giai nen {handoff_id}".\n6. ChatGPT se doi chieu SHA-256 va doc lai PNG tu Windows de QC thi giac.\n   ZIP duoc tao KHONG co nghia da QC VISUAL_PASS.\n\nManifest: {target_workspace}\\{manifest_rel.replace('/', chr(92))}\n'''
    out = Path(output_path)
    if out.exists():
        raise FileExistsError('OUTPUT_ZIP_ALREADY_EXISTS')
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in contents.items():
            z.writestr(name, data)
        z.writestr(manifest_rel, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        z.writestr(guide_rel, instructions)
    # Read back actual ZIP bytes, not just trust the write call.
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(contents) | {manifest_rel, guide_rel}
        for name, raw in contents.items():
            assert sha_bytes(z.read(name)) == sha_bytes(raw)
    result = {'status': 'ZIP_READY_FOR_DOWNLOAD', 'zipPath': str(out), 'zipSha256': sha_bytes(out.read_bytes()), 'manifestRelativePath': manifest_rel, 'imageCount': len(records), 'targetWorkspaceRootWindows': target_workspace, 'visualQC': 'NOT_STARTED'}
    print(json.dumps(result, ensure_ascii=False))
    return result


def verify(workspace, manifest_rel):
    base = Path(workspace).resolve(strict=True)
    path = base / safe_rel(manifest_rel)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(base):
        raise ValueError('MANIFEST_NOT_IN_WORKSPACE')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    assert manifest['manifestRelativePath'] == manifest_rel
    seen = set()
    for entry in manifest['images']:
        rel = safe_rel(entry['targetRelativePath'])
        if rel.casefold() in seen: raise ValueError('DUPLICATE_IMPORTED_TARGET')
        seen.add(rel.casefold())
        file = base / rel
        if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(base):
            raise ValueError('MISSING_IMPORTED_IMAGE:' + rel)
        data = file.read_bytes()
        w, h = png_info(data)
        if len(data) != entry['byteCount'] or sha_bytes(data) != entry['pngSha256'] or (w, h) != (entry['width'], entry['height']):
            raise ValueError('IMPORTED_IMAGE_MISMATCH:' + rel)
    result = {'status': 'IMPORTED_PNG_HASHES_VERIFIED', 'fileCount': len(seen), 'visualQC': 'NOT_STARTED', 'imageActuallyReceivedByChatGPT': False}
    print(json.dumps(result, ensure_ascii=False))
    return result


def main():
    p = argparse.ArgumentParser(description='Safe Video-hoat-hinh ZIP image handoff')
    cmd = p.add_subparsers(dest='action', required=True)
    buildcmd = cmd.add_parser('pack')
    buildcmd.add_argument('--spec', required=True)
    buildcmd.add_argument('--output', required=True)
    verifycmd = cmd.add_parser('verify')
    verifycmd.add_argument('--workspace', required=True)
    verifycmd.add_argument('--manifest', required=True)
    args = p.parse_args()
    try:
        if args.action == 'pack': build(args.spec, args.output)
        else: verify(args.workspace, args.manifest)
    except (OSError, ValueError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
