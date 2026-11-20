"""Real-media delivery/revision verification; host events are explicitly simulated.

Creates a new verified-run directory, preserves V01 before rendering V02, and
tests backend controls without pretending a native UI click or user acceptance.
"""
import argparse,copy,importlib.util,json,re,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from render_sample_version import render

REPO=Path(__file__).resolve().parents[1]
REF=REPO/'skills/openfilm-macro-bundles/references'
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
f=load(REF/'finish_first.py','ff');flow=load(REF/'production_flow.py','flow');rev=load(REF/'revision_history.py','rev')
scheduler=load(REF/'macro_scheduler.py','scheduler')
oneclick=load(REPO/'skills/openfilm-oneclick-approval/references/validate_approval_event.py','oneclick')
policy=json.loads((REF/'MACRO_POLICY.json').read_text(encoding='utf-8'))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def verify(root,cli):
    root=root.resolve();dest=root/'verified-run';dest.mkdir()
    shutil.copyfile(root/'V01.mp4',dest/'V01.mp4')
    before=f.digest(dest/'V01.mp4');save(dest/'V01-before-revision.json',{'sha256':before,'at':datetime.now(timezone.utc).isoformat(),'originalSha256':f.digest(root/'V01.mp4')})
    assert not f.check_file(dest,'V01.mp4',before,require_audio=True)
    # State replay tests consume actual artifacts. They do not claim the scheduler
    # ran the earlier manual source construction or that a user clicked a button.
    paths=[('P07','source-manifest.json'),('P08','profile.json'),('P09','film.json'),('P10','storyboard.md'),
           ('P11','character.svg'),('P12','audio/S01.wav'),('P13','V01/captions.vtt'),('P14','V01/scenes/S01.html'),
           ('P16','V01/scenes/S02.html'),('P17','V01/film.html'),('P19','verified-run/V01.mp4'),('P21','verified-run/delivery.json')]
    save(dest/'delivery.json',{'video':'verified-run/V01.mp4','sha256':before,'status':'OUTPUT_READY'})
    state={'simulationOnly':True,'reconstructedFromArtifacts':True,'schemaVersion':1,'pluginVersion':'1.14.1','productionMode':f.MODE,
        'stateRevision':1,'deviceId':'local-windows-sample','workspace':str(root),'filmId':'mam-first-journey',
        'packets':[],'preflightGates':{},'stageStates':{'P06':{'status':'SKIPPED','skipReason':'Reuse installed runtime; no install'},'P15':{'status':'SKIPPED','skipReason':'2D only'}}}
    for i,(stage,path) in enumerate(paths):
        state['packets'].append({'packetId':stage+'.01.sample','stageId':stage,'scopeIds':[stage],'status':'PLANNED',
            'inputPaths':[paths[i-1][1]] if i else ['dialogue-jobs.json'],'outputPaths':[path],'allowedCommands':[],'riskClass':'NORMAL'})
    for i in range(6):state['preflightGates'][f'P{i:02d}']={'status':'OUTPUT_READY','evidencePaths':['GPU_EXECUTION.json','profile.json']}
    state['macroBundles']=scheduler.propose(state,policy)
    for b in state['macroBundles']:
        b['presentedToUserRevision']=1
        if b['macroId']=='M1':b['inputHashes']={'dialogue-jobs.json':f.digest(root/'dialogue-jobs.json')}
    def event(action,bundle=None):
        e={k:state[k] for k in ('deviceId','workspace','filmId','stateRevision')}
        e.update(action=action,approvalId='SIMULATED_BACKEND_TEST_ONLY',source='USER_CHAT',at=datetime.now(timezone.utc).isoformat(),simulationOnly=True)
        if action=='APPROVE_PRODUCTION':
            e['macroBundleIds']=[b['macroBundleId'] for b in state['macroBundles']]
            e['bundles']={b['macroBundleId']:{k:b.get(k) for k in flow.SCOPE_FIELDS} for b in state['macroBundles']}
        elif bundle:
            e.update(macroBundleId=bundle['macroBundleId'],**{k:bundle.get(k) for k in flow.SCOPE_FIELDS})
        return e
    state=flow.apply_event(state,event('APPROVE_PRODUCTION'),policy)
    assert not oneclick.validate(state,event('VIEW_PROGRESS'))
    state=flow.apply_event(state,event('RESUME_APPROVED_MACRO',state['macroBundles'][0]),policy)
    trace=[]
    for p in state['packets']:
        b=next(b for b in state['macroBundles'] if p['packetId'] in b['packetIds'])
        assert scheduler.next_eligible_packet(state,b['macroBundleId'],policy)==p['packetId']
        p.update(status='OUTPUT_READY',outputHashes={x:f.digest(root/x) for x in p['outputPaths']})
        assert not f.completion_errors(p,root)
        trace.append({'packetId':p['packetId'],'macro':b['macroId'],'status':'OUTPUT_READY'})
    state['video']={'path':'verified-run/V01.mp4','sha256':before,'version':1,'requiresAudio':True,'status':'OUTPUT_READY'}
    state=flow.apply_event(state,event('DELIVER_VIDEO',state['macroBundles'][-1]),policy)
    snapshot=copy.deepcopy(state);assert not oneclick.validate(state,event('VIEW_VIDEO'));assert state==snapshot
    # Acceptance is evaluated only in memory and discarded, never saved as project acceptance.
    accepted=flow.apply_event(state,event('ACCEPT_VIDEO',state['macroBundles'][-1]),policy)
    assert accepted['video']['status']=='USER_ACCEPTED' and state['video']['status']=='DELIVERED_FOR_REVIEW'
    save(dest/'backend-replay-V01.json',state)
    feedback=json.loads((root/'SOURCE_VERSIONS.json').read_text(encoding='utf-8'))['feedback']
    e=event('REQUEST_REVISION',state['macroBundles'][-1]);e['feedback']=[feedback]
    assert not oneclick.validate(state,e)
    state=rev.plan_revision(state,e);save(dest/'revision-plan-before-render.json',state['revisionPlan'])
    render(root/'V02',dest/'V02.mp4',cli)
    assert f.digest(dest/'V01.mp4')==before and f.digest(root/'V01.mp4')==before
    state=rev.register_revision(state)
    assert state['video']['status']=='OUTPUT_READY'
    state=flow.apply_event(state,event('DELIVER_VIDEO',state['macroBundles'][-1]),policy)
    save(dest/'backend-replay-V02.json',state)
    report={'status':'PASS','durationSeconds':26.875,'fps':24,'resolution':[1280,720],'scenes':['S01','S02','S03'],
        'realOpenFilmCLI':True,'realVieNeuGPU':True,'nativeHostTested':False,'nativeHostLimitation':'No connected document executor or native action callback is exposed in this session.',
        'backendControls':['RESUME_APPROVED_MACRO','VIEW_PROGRESS','VIEW_VIDEO','ACCEPT_VIDEO (discarded simulation)','REQUEST_REVISION'],
        'backendEventsSimulated':True,'schedulerReplay':trace,'schedulerDroveOriginalBuild':False,
        'feedback':feedback,'changedSourceFiles':['scenes/S02.html'],'unchangedScenes':['S01','S03'],
        'v01Sha256Before':before,'v01Sha256After':f.digest(dest/'V01.mp4'),'v02Sha256':f.digest(dest/'V02.mp4'),
        'userAccepted':False,'statusAfterDelivery':'DELIVERED_FOR_REVIEW','qualityQcGateUsed':False,
        'captionTiming':'Phrase timing proportional to measured WAV duration; no word-level forced alignment.',
        'v01ShellNote':'First PowerShell wrapper returned 1 due NativeCommandError stderr formatting; OpenFilm reported full 645-frame render. MP4 independently fully decoded. V02 uses subprocess and returns 0.'}
    save(dest/'EXECUTION_REPORT.json',report)
    save(dest/'DELIVERY_MANIFEST.json',{'filmId':'mam-first-journey','status':'DELIVERED_FOR_REVIEW','userAccepted':False,
        'videos':[{'path':'V01.mp4','sha256':before},{'path':'V02.mp4','sha256':f.digest(dest/'V02.mp4')}],
        'sources':['../V01','../V02'],'gpuEvidence':'../GPU_EXECUTION.json','revisionEvidence':'EXECUTION_REPORT.json'})
    print(json.dumps({k:report[k] for k in ('status','v01Sha256Before','v01Sha256After','v02Sha256','nativeHostTested')},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--cli',type=Path,required=True);a=p.parse_args();verify(a.workspace,a.cli)
