"""Opt-in real OpenFilm CLI regression. Uses installed runtime; never installs models.

This fixture uses synthetic tone WAV, not VieNeu speech. It proves the render and
delivery/revision flow only. All writes stay in a new directory under --workspace.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'skills/openfilm-macro-bundles/references'
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
f=load(REF/'finish_first.py','finish_first')
flow=load(REF/'production_flow.py','production_flow')
scheduler=load(REF/'macro_scheduler.py','macro_scheduler')
rev=load(REF/'revision_history.py','revision_history')
audit=load(ROOT/'skills/openfilm-script-input/references/audit_seven_files.py','audit')
fixture=load(ROOT/'skills/openfilm-smoke-e2e/references/create_e2e_fixture.py','fixture')

def run(workspace, cli):
    workspace=Path(workspace).resolve();cli=Path(cli).resolve()
    if not workspace.is_dir() or not cli.is_file():raise ValueError('existing workspace and installed CLI required')
    root=workspace/('finish-first-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));root.mkdir()
    def write(path,content):
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8');return path
    def record(path,data):return write(path,json.dumps(data,ensure_ascii=False,indent=2))
    def render(out):
        args=[str(cli),'render','--out',str(root/out),'--fps','10','--workers','1']
        result=subprocess.run(args,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=300)
        write(out+'.stdout.txt',result.stdout);write(out+'.stderr.txt',result.stderr)
        record(out+'.command.json',{'command':args,'cwd':str(root),'exitCode':result.returncode})
        if result.returncode:raise RuntimeError('OpenFilm render failed; see '+str(root/(out+'.stderr.txt')))
        errors=f.check_file(root,out,require_audio=True)
        if errors:raise ValueError('; '.join(errors))
    for name in audit.REQUIRED:
        write('source/'+name,'Ma canh,Noi dung,Thoi luong\nTEST-A,Fixture movement,2\n' if name.endswith('.csv') else 'Synthetic fixture: move a circle for two seconds. No real film content.\n')
    film={'schemaVersion':1,'filmId':'test-film','masterEngine':'openfilm','fps':10,'width':1280,'height':720,'durationInFrames':20,
          'shots':[{'id':'TEST-A','startFrame':0,'durationInFrames':20,'type':'2d','scene':'scenes/probe.html'}],
          'dialogues':[]}
    timeline='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=1280, height=720"></head><body>
<section><iframe src="scenes/probe.html#t=0,2" at="0" style="width:1280px;height:720px"></iframe></section>
<section><audio src="audio/tone.wav#t=0,2" at="0"></audio></section>
<section><track kind="captions" src="captions.vtt"></section></body></html>'''
    def input_audit():
        report=audit.audit(root/'source')
        if report['status']!='PASS':raise ValueError(report)
        record('source-manifest.json',report)
    def filmdata():
        validator=load(ROOT/'skills/openfilm-filmdata/references/validate_filmdata.py','filmdata_validator')
        errors=validator.validate(film)
        if errors:raise ValueError(errors)
        record('film.json',film);write('film.html',timeline)
    def asset():
        (root/'assets').mkdir();shutil.copyfile(ROOT/'assets/logo.png',root/'assets/logo.png')
    def audio():
        (root/'audio').mkdir();(root/'audio/tone.wav').write_bytes(fixture.wav_bytes())
    paths=[('P07','source-manifest.json'),('P08','profile.json'),('P09','film.json'),('P10','storyboard.md'),
           ('P11','assets/logo.png'),('P12','audio/tone.wav'),('P13','captions.vtt'),('P14','scenes/probe.html'),
           ('P16','scenes-ready.json'),('P17','film.html'),('P19','V01.mp4'),('P21','DELIVERY_MANIFEST.json')]
    actions={
        'P07':input_audit,'P08':lambda:record('profile.json',{'engine':'openfilm','fps':10,'audio':'fixture-tone'}),
        'P09':filmdata,'P10':lambda:write('storyboard.md','TEST-A: circle travels left to right in two seconds.'),
        'P11':asset,'P12':audio,
        'P13':lambda:write('captions.vtt','WEBVTT\n\n00:00:00.000 --> 00:00:01.800\nFinish First fixture\n'),
        'P14':lambda:write('scenes/probe.html',fixture.SCENE.replace('duration:7','duration:2').replace('t/7','t/2').replace('E2E 7s','Finish First V01')),
        'P16':lambda:record('scenes-ready.json',{'scene':'scenes/probe.html','sha256':f.digest(root/'scenes/probe.html')}),
        'P17':lambda:write('film.html',timeline), 'P19':lambda:render('V01.mp4'),
        'P21':lambda:record('DELIVERY_MANIFEST.json',{'video':'V01.mp4','sha256':f.digest(root/'V01.mp4'),'status':'OUTPUT_READY'})}
    state={'schemaVersion':1,'stateRevision':1,'deviceId':'windows-local','workspace':str(root),
           'filmId':'test-film','packets':[],'preflightGates':{},'productionMode':f.MODE,
           'stageStates':{'P06':{'status':'SKIPPED','skipReason':'reuse installed verified CLI'},'P15':{'status':'SKIPPED','skipReason':'2D-only fixture'}}}
    for stage,path in paths:
        inputs=['source/'+name for name in audit.REQUIRED] if stage=='P07' else [paths[len(state['packets'])-1][1]]
        state['packets'].append({'packetId':stage+'.01.fixture','stageId':stage,'scopeIds':[stage],
            'status':'PLANNED','inputPaths':inputs,'outputPaths':[path],'allowedCommands':[], 'riskClass':'NORMAL'})
    for i in range(6):
        path=record(f'preflight/P{i:02d}.json',{'fixtureApproval':'user requested T31/T32; installed runtime only','cli':str(cli)})
        state['preflightGates'][f'P{i:02d}']={'status':'OUTPUT_READY','evidencePaths':[path]}
    policy=json.loads((REF/'MACRO_POLICY.json').read_text(encoding='utf-8'))
    state['macroBundles']=scheduler.propose(state,policy)
    for b in state['macroBundles']:
        b['presentedToUserRevision']=1
        if b['macroId']=='M1':b['inputHashes']={'source/'+name:f.digest(root/'source'/name) for name in audit.REQUIRED}
    def event(action,b=None):
        e={k:state[k] for k in ('stateRevision','deviceId','workspace','filmId')}
        e.update(action=action,approvalId='FIXTURE_SIMULATED_EVENT',source='USER_CHAT',at=datetime.now(timezone.utc).isoformat(),fixtureOnly=True)
        if b:e.update(macroBundleId=b['macroBundleId'],**{k:b.get(k) for k in flow.SCOPE_FIELDS})
        return e
    e=event('APPROVE_PRODUCTION');e['macroBundleIds']=[b['macroBundleId'] for b in state['macroBundles']]
    e['bundles']={b['macroBundleId']:{k:b.get(k) for k in flow.SCOPE_FIELDS} for b in state['macroBundles']}
    state=flow.apply_event(state,e,policy)
    for p in state['packets']:
        b=next(b for b in state['macroBundles'] if p['packetId'] in b['packetIds'])
        if scheduler.next_eligible_packet(state,b['macroBundleId'],policy)!=p['packetId']:raise ValueError('scheduler blocked')
        actions[p['stageId']]()
        p.update(status='OUTPUT_READY',outputHashes={x:f.digest(root/x) for x in p['outputPaths']})
        if f.completion_errors(p,root):raise ValueError('incomplete '+p['packetId'])
        record('checkpoint-running.json',state)
    state['video']={'path':'V01.mp4','sha256':f.digest(root/'V01.mp4'),'version':1,'status':'OUTPUT_READY','requiresAudio':True}
    b=state['macroBundles'][-1];state=flow.apply_event(state,event('DELIVER_VIDEO',b),policy)
    record('checkpoint-V01.json',state)
    e=event('REQUEST_REVISION',state['macroBundles'][-1]);e['feedback']=[{'category':'scene','targetIds':['TEST-A'],'request':'change circle color'}]
    state=rev.plan_revision(state,e)
    scene=root/'scenes/probe.html';scene.write_text(scene.read_text(encoding='utf-8').replace('#ffc85a','#65d6ad'),encoding='utf-8')
    render('V02.mp4');state=rev.register_revision(state);record('checkpoint-V02.json',state)
    report={'status':'PASS','workspace':str(root),'realOpenFilmCLI':True,'renderedVersions':['V01.mp4','V02.mp4'],
            'v01Status':'DELIVERED_FOR_REVIEW','v01Preserved':True,'qualityQCRequired':False,
            'syntheticFixtureEvents':True,'vieneuSpeechValidated':False,'audio':'synthetic tone fixture',
            'limitation':'No live host click integration or VieNeu GPU inference tested.'}
    record('EXECUTION_REPORT.json',report);return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',required=True);ap.add_argument('--cli',required=True)
    args=ap.parse_args();print(json.dumps(run(args.workspace,args.cli),ensure_ascii=False,indent=2))
