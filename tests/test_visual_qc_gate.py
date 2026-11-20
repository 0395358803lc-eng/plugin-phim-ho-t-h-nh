"""New RED -> GREEN coverage for actual visual review gate; no external IO."""
import importlib.util, hashlib, json, copy, struct, zlib
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'skills/openfilm-visual-inspection/references'
MAC=ROOT/'skills/openfilm-macro-bundles/references'

def module(path):
    sp=importlib.util.spec_from_file_location(path.stem,path)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def policy():return json.loads((BASE/'VISUAL_QC_POLICY.json').read_text('utf-8'))

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def png(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    def chunk(tag,data):
        body=tag+data
        return struct.pack('>I',len(data))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)
    w,h=128,72
    image=bytes([0]+[60,130,190,255]*w)*h
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))
        +chunk(b'IDAT',zlib.compress(image))+chunk(b'IEND',b''))

def fixture(tmp,macro='M5',source_kind=None):
    cfg=policy()['requiredMacros'][macro]
    kind=source_kind or cfg['sourceKind'];isvideo=kind.endswith('_MP4')
    source=tmp/('renders/'+kind.lower()+'/source.mp4' if isvideo else 'projects/a/source-manifest.json')
    source.parent.mkdir(parents=True,exist_ok=True)
    source.write_bytes(b'\x00\x00\x00\x18ftypisom-test' if isvideo else b'{"frames":"example"}')
    targets=['SMOKE'] if macro=='M5' else (['SB_C001','CHAR_A','BG01'] if macro=='M2' else ['C001','C002'])
    report={'schemaVersion':1,'macroId':macro,'filmId':'a','reviewId':'vision-review-2026-v1','reviewer':'CHATGPT_VISION',
            'source':{'kind':kind,'path':source.relative_to(tmp).as_posix(),'sha256':sha(source)},
            'requiredTargets':targets,'status':'VISUAL_PASS','observations':[], 'reviewScope':'SAMPLED_FRAMES_NOT_FULL_PLAYBACK'}
    for tid in targets:
        for role in cfg['requiredFrameRoles']:
            p=tmp/f'qc/visual/{macro}/{tid}-{role}.png';png(p)
            report['observations'].append({'targetId':tid,'frameRole':role,'imagePath':p.relative_to(tmp).as_posix(),
                'imageSha256':sha(p),'sourceSha256':sha(source),'transferMethod':'RDC_READ_FILE',
                'imageActuallyReceived':True,'hostImageEvidence':'remote-read-image-context-id',
                'observation':'Nhân vật nằm giữa khung hình, tỷ lệ khuôn mặt cân đối, màu nền ổn định và không thấy vật thể bị cắt.',
                'assessment':'PASS','issues':[]})
    if isvideo or macro=='M4':
        log=tmp/f'qc/visual/{macro}/extract.json'; log.parent.mkdir(parents=True,exist_ok=True)
        log.write_text(json.dumps({'sourcePath':report['source']['path'],'sourceSha256':sha(source),'exitCode':0,
             'engine':'OPENFILM_CLI' if macro=='M4' else 'FFMPEG_FROM_RENDERED_MP4',
             'imagePaths':[o['imagePath'] for o in report['observations']]}),encoding='utf-8')
        report['extractionEvidencePath']=log.relative_to(tmp).as_posix()
        report['extractionEvidenceSha256']=sha(log)
    f=tmp/f'qc/visual/{macro}/VISUAL_QC_REPORT.json';f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report,f

@pytest.mark.parametrize('macro', ['M2','M4','M5','M6','M7'])
def test_valid_real_image_hashes_and_multimodal_review_receipts(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py'); report,_=fixture(tmp_path,macro)
    assert m.validate(report,policy(),tmp_path)==[]

@pytest.mark.parametrize('macro', ['M2','M4','M5','M6','M7'])
def test_logs_ffprobe_and_approving_without_seen_images_never_pass(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py'); report,_=fixture(tmp_path,macro)
    report['observations'][0]['imageActuallyReceived']=False
    assert m.validate(report,policy(),tmp_path)
    report['observations']=[]
    assert m.validate(report,policy(),tmp_path)

@pytest.mark.parametrize('macro', ['M2','M4','M5','M6','M7'])
def test_missing_image_or_modified_hash_blocks_qc(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py');report,_=fixture(tmp_path,macro)
    path=tmp_path/report['observations'][0]['imagePath'];path.write_bytes(b'changed')
    assert any('hash' in s.lower() or 'image' in s.lower() for s in m.validate(report,policy(),tmp_path))

@pytest.mark.parametrize('macro', ['M2','M4','M5','M6','M7'])
def test_missing_frame_role_or_target_is_not_visual_pass(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py');report,_=fixture(tmp_path,macro)
    report['observations'].pop()
    assert m.validate(report,policy(),tmp_path)

@pytest.mark.parametrize('macro', ['M5','M6','M7'])
def test_render_macros_require_exact_kind_and_real_render_source(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py');report,_=fixture(tmp_path,macro)
    report['source']['kind']='DESIGN_MANIFEST'
    assert m.validate(report,policy(),tmp_path)

@pytest.mark.parametrize('macro', ['M2','M4','M5','M6','M7'])
def test_visual_failure_or_unresolved_issue_blocks_qc(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py');report,_=fixture(tmp_path,macro)
    report['observations'][0].update(assessment='FAIL',issues=['VIS-0001'])
    assert m.validate(report,policy(),tmp_path)
    report['observations'][0].update(assessment='PASS',issues=[])
    report['observations'][0]['observation']='OK'
    assert m.validate(report,policy(),tmp_path)

@pytest.mark.parametrize('macro', ['M2','M4','M5','M6','M7'])
def test_stale_render_source_or_unsafe_image_path_rejected(tmp_path,macro):
    m=module(BASE/'validate_visual_qc.py');report,_=fixture(tmp_path,macro)
    report['source']['sha256']='0'*64
    assert m.validate(report,policy(),tmp_path)
    report['source']['sha256']=report['observations'][0]['sourceSha256']
    report['observations'][0]['imagePath']='../outside.png'
    assert m.validate(report,policy(),tmp_path)

def test_macro_accept_requires_actual_visual_report_not_only_normal_qc(tmp_path):
    m=module(MAC/'validate_macro_event.py'); p=json.loads((MAC/'MACRO_POLICY.json').read_text('utf-8'))
    visual=module(BASE/'validate_visual_qc.py');report,report_file=fixture(tmp_path,'M5')
    # No additional packet approval; legacy-compatible macro evidence and internal QC.
    packet={'packetId':'P18.01.C001','stageId':'P18','status':'READY_FOR_REVIEW','qcStatus':'PASS',
            'planApprovalId':'user-approve','outputPaths':[],'inputPaths':[],'scopeIds':['SMOKE'],
            'allowedCommands':[],'evidencePaths':['qc/fine.json'],'outputHashes':{}}
    bundle={'macroBundleId':'M5.B001','macroId':'M5','stageIds':['P18'],'packetIds':[packet['packetId']],
            'scopeIds':['SMOKE'],'allowedPaths':[],'allowedCommands':[],'riskClass':'NORMAL','inputHashes':{},
            'specialApprovalRequired':False,'status':'READY_FOR_REVIEW','planApprovalId':'user-approve','evidencePaths':['qc/fine.json']}
    index={'stateRevision':7,'deviceId':'pc1','workspace':str(tmp_path),'filmId':'a','packets':[packet],
           'macroBundles':[bundle],'stageStates':{'P18':{'status':'QC_PASS','qcStatus':'PASS','evidencePaths':['qc/fine.json']}}}
    event={'action':'ACCEPT_MACRO','stateRevision':7,'deviceId':'pc1','workspace':str(tmp_path),'filmId':'a','macroBundleId':'M5.B001',
           **{k:bundle[k] for k in ('macroId','stageIds','packetIds','scopeIds','allowedPaths','allowedCommands','riskClass','inputHashes')}}
    assert any('visual' in x.lower() for x in m.validate(index,event,p))
    index['visualTargets']={'M5':['SMOKE']}
    index['visualGates']={'M5':{'status':'VISUAL_PASS','reportPath':report_file.relative_to(tmp_path).as_posix(),
                                     'reportSha256':sha(report_file),'stateRevision':7}}
    event['visualReportSha256']=sha(report_file)
    assert m.validate(index,event,p)==[]
    report['observations'][0]['imageActuallyReceived']=False
    report_file.write_text(json.dumps(report),encoding='utf-8')
    index['visualGates']['M5']['reportSha256']=sha(report_file)
    event['visualReportSha256']=sha(report_file)
    assert any('visual' in x.lower() for x in m.validate(index,event,p))


def test_visual_macro_contract_keeps_99_technical_packet_ids():
    defs=json.loads((ROOT/'skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json').read_text('utf-8'))
    assert sum(len(s['packets']) for s in defs['stages'])==99
    assert policy()['mandatoryMacroIds']==['M2','M4','M5','M6','M7']
