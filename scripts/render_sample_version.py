"""Render with installed OpenFilm; preserve original logs and redact Studio keys in delivery logs."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path

def render(project,output,cli):
    project=project.resolve(strict=True);output=output.resolve();cli=cli.resolve(strict=True)
    if output.exists():raise FileExistsError('will not overwrite '+str(output))
    args=[str(cli),'render','--out',str(output),'--fps','24','--workers','1']
    result=subprocess.run(args,cwd=project,capture_output=True,encoding='utf-8',errors='replace',timeout=900)
    log=output.with_suffix('.render.log');log.write_text(re.sub(r'(key=)[^\s&]+',r'\1[REDACTED]',result.stdout+'\n'+result.stderr),encoding='utf-8')
    receipt={'command':args,'cwd':str(project),'exitCode':result.returncode,'log':log.name}
    if result.returncode:raise RuntimeError('OpenFilm render failed: '+str(log))
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)],capture_output=True,text=True,check=True)
    receipt['probe']=json.loads(probe.stdout)
    decode=subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],capture_output=True,text=True)
    receipt['decodeExitCode']=decode.returncode;receipt['decodeErrors']=decode.stderr
    if decode.returncode or decode.stderr:raise RuntimeError('MP4 decode failed')
    receipt['sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.render.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'path':str(output),'exitCode':result.returncode,'decodeExitCode':decode.returncode,'sha256':receipt['sha256']},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--cli',required=True,type=Path);a=p.parse_args();render(a.project,a.output,a.cli)
