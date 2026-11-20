"""Restore a source ZIP into a NEW directory and compare with a pinned Git base."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path

def verify(archive,destination,base):
    archive=Path(archive).resolve(strict=True);root=Path(destination).resolve()
    if root.exists():raise ValueError('restore target already exists')
    root.mkdir(parents=True)
    records=[];duplicates=[]
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError('ZIP CRC failure')
        for item in z.infolist():
            relative=item.filename.replace('\\','/')
            p=(root/relative).resolve()
            if not p.is_relative_to(root) or relative.startswith('/') or ':' in relative or '..' in relative.split('/'):
                raise ValueError('unsafe backup member')
            if item.is_dir():p.mkdir(parents=True,exist_ok=True);continue
            raw=z.read(item);p.parent.mkdir(parents=True,exist_ok=True)
            if p.exists():
                if p.read_bytes()!=raw:raise ValueError('conflicting duplicate backup member '+relative)
                duplicates.append(relative);continue
            with p.open('xb') as stream:stream.write(raw)
            if p.read_bytes()!=raw:raise ValueError('restored bytes differ')
            records.append({'path':relative,'sha256':hashlib.sha256(raw).hexdigest()})
    files=subprocess.check_output(['git','ls-tree','-r','--name-only',base],text=True).splitlines()
    for name in files:
        expected=subprocess.check_output(['git','show',base+':'+name]);p=root/name
        if not p.is_file():raise ValueError('missing source '+name)
        restored=p.read_bytes()
        if restored!=expected and restored.replace(b'\r\n',b'\n')!=expected.replace(b'\r\n',b'\n'):
            raise ValueError('source differs '+name)
    return {'status':'PASS','archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'baseCommit':base,'restoredFiles':len(records),'gitFilesMatched':len(files),
            'manifestVersion':json.loads((root/'plugin.json').read_text(encoding='utf-8'))['version'],
            'skills':len(list((root/'skills').glob('*/SKILL.md'))),'identicalDuplicateEntries':duplicates,'records':records}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--archive',required=True);ap.add_argument('--destination',required=True)
    ap.add_argument('--base',required=True);ap.add_argument('--report',required=True);a=ap.parse_args()
    report=verify(a.archive,a.destination,a.base);Path(a.report).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'}))
