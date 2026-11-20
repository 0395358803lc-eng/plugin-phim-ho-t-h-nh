"""Published-source guard for mandatory vision gates and preserved plugin features."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(path):return (ROOT/path).read_text(encoding='utf-8')

def test_five_macros_are_mandatory_not_packet_approval():
    p=json.loads(read('skills/openfilm-macro-bundles/references/MACRO_POLICY.json'))
    v=json.loads(read('skills/openfilm-visual-inspection/references/VISUAL_QC_POLICY.json'))
    assert [m['id'] for m in p['macros']]==[f'M{i}' for i in range(8)]
    assert 'visualInspectionRequiredForAcceptance' not in p
    assert p['defaultMode']=='FINISH_FIRST_USER_REVIEW'
    assert p['microPacketsRemainInternal']

def test_all_ninety_nine_packet_ids_unchanged_with_visual_entries():
    packet_spec=json.loads(read('skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json'))
    ids=[p['templateId'] for s in packet_spec['stages'] for p in s['packets']]
    assert len(ids)==len(set(ids))==99
    for pid in ['P10.05','P11.05','P14.05','P15.05','P16.05','P18.04','P19.04','P20.06','P21.03','P21.05']:
        found=next(p for s in packet_spec['stages'] for p in s['packets'] if p['templateId']==pid)
        assert 'visualEvidenceRequired' not in found

def test_m2_m4_m5_m6_m7_skill_routes_to_real_images():
    for rel in ['skills/video-hoat-hinh/SKILL.md', 'skills/openfilm-macro-bundles/SKILL.md',
                'skills/openfilm-qc-advanced/SKILL.md','skills/openfilm-qc-render/SKILL.md',
                'skills/openfilm-oneclick-approval/SKILL.md']:
        assert 'FINISH_FIRST_USER_REVIEW' in read(rel)
    text=read('skills/openfilm-visual-inspection/SKILL.md')
    for signal in ['tùy chọn','người dùng','V01','OUTPUT_READY','DELIVERED_FOR_REVIEW']:
        assert signal in text

def test_validator_is_enforced_by_macro_accept_events():
    event=read('skills/openfilm-macro-bundles/references/validate_macro_event.py')
    assert '_validate_visual_accept' in event
    assert 'visualReportSha256' in event
    assert "'ACCEPT_AND_APPROVE_NEXT_MACRO'" in event
    assert 'validator.validate(report,config,root,targets)' in event

def test_root_and_legacy_manifest_remain_in_sync_with_prompt_and_private_identity():
    root=json.loads(read('plugin.json'));leg=json.loads(read('.codex-plugin/plugin.json'))
    assert root['version']==leg['version']=='1.14.0'
    assert root['name']==leg['name']=='video-hoat-hinh'
    assert root['extensions']['com.openai']['interface']==leg['interface']
    assert len(root['extensions']['com.openai']['interface']['defaultPrompt'])==3
    assert len(list((ROOT/'skills').glob('*/SKILL.md')))==33

def test_no_download_or_cpu_fallback_from_visual_qc():
    content=read('skills/openfilm-visual-inspection/SKILL.md')
    assert 'phê duyệt' in content
    assert 'GPU' not in content or 'GPU' in read('skills/video-hoat-hinh/SKILL.md')
    assert 'CLI' in content
    assert 'không' in content.lower()

def test_report_template_is_never_auto_pass():
    report=json.loads(read('skills/openfilm-visual-inspection/references/VISUAL_QC_REPORT_TEMPLATE.json'))
    assert report['status']=='VISUAL_PENDING'
    assert report['observations']==[]
    assert report['requiredTargets']==[]
