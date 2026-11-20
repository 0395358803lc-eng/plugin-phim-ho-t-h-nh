"""Regression tests for the ZIP handoff protocol. Run with python -m unittest ..."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import image_handoff

# 1x1 RGBA transparent PNG generated in-memory by stdlib; no external assets.
def tiny_png():
    import struct, zlib
    def chunk(name, payload):
        return struct.pack('>I', len(payload)) + name + payload + struct.pack('>I', zlib.crc32(name + payload) & 0xFFFFFFFF)
    ihdr = struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0)
    idat = zlib.compress(b'\x00\x00\x00\x00\x00')
    return image_handoff.PNG_SIG + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.image = self.root / 'generated.png'
        self.image.write_bytes(tiny_png())
        self.target = 'projects/film/storyboard/previews/SHOT-SC001-01.png'
        self.workspace = str(self.root / 'VIDEO_HOAT_HINH_WORKSPACE')
        self.spec = {'handoffId': 'M2_PILOT_20261120', 'targetWorkspace': self.workspace, 'images': [{'inputPng': str(self.image), 'targetRelativePath': self.target, 'targetId': 'SHOT-SC001-01', 'sourceTextPath': 'projects/film/storyboard/shots/SHOT-SC001-01.md', 'sourceTextSha256': 'a'*64}]}
        self.specpath = self.root / 'spec.json'
        self.out = self.root / 'images.zip'

    def write_spec(self):
        self.specpath.write_text(json.dumps(self.spec), encoding='utf-8')

    def test_pack_and_verify_no_visual_qc_claims(self):
        self.write_spec()
        result = image_handoff.build(self.specpath, self.out)
        self.assertEqual(result['status'], 'ZIP_READY_FOR_DOWNLOAD')
        with zipfile.ZipFile(self.out) as z:
            entries = z.namelist()
            self.assertIn(self.target, entries)
            self.assertIn('handoffs/M2_PILOT_20261120/MANIFEST.json', entries)
            manifest = json.loads(z.read('handoffs/M2_PILOT_20261120/MANIFEST.json'))
            self.assertEqual(manifest['visualQC'], 'NOT_STARTED')
            self.assertFalse(manifest['images'][0]['imageActuallyReceivedFromWindows'])
            self.assertEqual(manifest['images'][0]['pngSha256'], image_handoff.sha_bytes(self.image.read_bytes()))
            self.assertNotIn('..', '\n'.join(entries))
            Path(self.workspace).mkdir()
            z.extractall(self.workspace)
        verification = image_handoff.verify(self.workspace, 'handoffs/M2_PILOT_20261120/MANIFEST.json')
        self.assertEqual(verification['fileCount'], 1)
        self.assertFalse(verification['imageActuallyReceivedByChatGPT'])

    def test_path_traversal_rejected(self):
        self.spec['images'][0]['targetRelativePath'] = 'projects/film/../../outside.png'
        self.write_spec()
        with self.assertRaises(ValueError):
            image_handoff.build(self.specpath, self.out)
        self.assertFalse(self.out.exists())

    def test_missing_binary_rejected(self):
        self.spec['images'][0]['inputPng'] = str(self.root / 'not_on_disk.png')
        self.write_spec()
        with self.assertRaises(ValueError):
            image_handoff.build(self.specpath, self.out)

    def test_duplicate_target_case_insensitive_rejected(self):
        copy = dict(self.spec['images'][0])
        copy['targetRelativePath'] = self.target.upper().replace('.PNG', '.png')
        self.spec['images'].append(copy)
        self.write_spec()
        with self.assertRaises(ValueError):
            image_handoff.build(self.specpath, self.out)

    def test_remote_tamper_fails(self):
        self.write_spec()
        image_handoff.build(self.specpath, self.out)
        Path(self.workspace).mkdir()
        with zipfile.ZipFile(self.out) as z:
            z.extractall(self.workspace)
        imported = Path(self.workspace) / self.target
        imported.write_bytes(imported.read_bytes()[:-1] + b'\x00')
        with self.assertRaises(ValueError):
            image_handoff.verify(self.workspace, 'handoffs/M2_PILOT_20261120/MANIFEST.json')

    def test_png_crc_rejects_corrupted_bytes(self):
        corrupted = bytearray(tiny_png()); corrupted[45] ^= 0x02
        with self.assertRaises(ValueError):
            image_handoff.png_info(bytes(corrupted))


if __name__ == '__main__':
    unittest.main()
