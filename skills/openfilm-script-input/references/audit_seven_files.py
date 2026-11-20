"""Read-only audit of the seven input documents. No file content is modified."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

REQUIRED = [
    'KICH_BAN_HOAN_CHINH.md', 'COT_TRUYEN.md', 'NHAN_VAT.md',
    'LOI_THOAI.md', 'DANH_SACH_CANH.csv',
    'HUONG_DAN_HINH_ANH_AM_THANH.md', 'BAO_CAO_NGHIEM_THU.md',
]

def audit(path: Path) -> dict:
    result = {'sourceDir': str(path), 'files': [], 'status': 'PASS', 'issues': []}
    if not path.is_dir():
        result['status'] = 'BLOCKED'
        result['issues'].append('SOURCE_DIR_NOT_FOUND')
        return result
    for name in REQUIRED:
        p = path / name
        row = {'name': name, 'exists': p.is_file(), 'sha256': None, 'bytes': None}
        if not p.is_file():
            result['issues'].append('MISSING:' + name)
            result['status'] = 'BLOCKED'
        elif p.is_symlink():
            result['issues'].append('SYMLINK_UNVERIFIED:' + name)
            result['status'] = 'BLOCKED'
        else:
            raw = p.read_bytes()
            row['bytes'] = len(raw)
            row['sha256'] = hashlib.sha256(raw).hexdigest()
            if not raw.strip():
                result['issues'].append('EMPTY:' + name)
                result['status'] = 'BLOCKED'
            try:
                text = raw.decode('utf-8-sig')
                row['encoding'] = 'utf-8-sig'
            except UnicodeDecodeError:
                row['encoding'] = 'UNVERIFIED'
                result['issues'].append('ENCODING:' + name)
                result['status'] = 'BLOCKED'
                text = ''
            if name.endswith('.csv') and text.strip():
                # Inconsistent delimiters and headers are flagged for human mapping.
                try:
                    dialect = csv.Sniffer().sniff(text[:4096], delimiters=',;\t')
                    reader = csv.reader(text.splitlines(), dialect)
                    rows = list(reader)
                    row['csvHeader'] = rows[0] if rows else []
                    row['csvRows'] = max(0, len(rows)-1)
                    row['csvDelimiter'] = dialect.delimiter
                    if not row['csvHeader'] or row['csvRows'] == 0:
                        result['issues'].append('CSV_HEADER_OR_ROWS:' + name)
                        result['status'] = 'BLOCKED'
                    if any(len(x) != len(row['csvHeader']) for x in rows[1:]):
                        result['issues'].append('CSV_UNEVEN_ROW_LENGTH:' + name)
                        result['status'] = 'BLOCKED'
                except csv.Error as exc:
                    result['issues'].append(f'CSV_PARSE:{name}:{exc}')
                    result['status'] = 'BLOCKED'
        result['files'].append(row)
    return result

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description='Read-only input manifest; do not confuse PASS with semantic QC.')
    ap.add_argument('source_dir',type=Path)
    ns=ap.parse_args()
    result=audit(ns.source_dir)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(0 if result['status']=='PASS' else 2)
