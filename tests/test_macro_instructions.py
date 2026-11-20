import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(p):return (ROOT/p).read_text('utf-8')

def test_main_uses_eight_macro_groups_not_stage_packet_buttons():
    s=read('skills/video-hoat-hinh/SKILL.md')
    assert 'v1.14.0' in s
    assert 'openfilm-macro-bundles/SKILL.md' in s
    assert 'Không xin duyệt riêng từng packet' in s
    assert 'P00–P05' in s and 'OpenFilm CLI' in s and 'GPU' in s

def test_all_approval_skill_entrypoints_route_new_projects_to_macro():
    for p in ['skills/openfilm-oneclick-approval/SKILL.md','skills/openfilm-high-workpackets/SKILL.md',
              'skills/openfilm-batch-approval/SKILL.md','skills/openfilm-checkpoint-approval/SKILL.md',
              'skills/openfilm-production-p06-p21/SKILL.md']:
        s=read(p)
        assert 'v1.14.0' in s,p
        assert 'FINISH_FIRST_USER_REVIEW' in s,p
        assert 'FINISH_FIRST_USER_REVIEW' in s,p

def test_decision_risks_and_cli_gpu_preserved():
    s=read('skills/openfilm-macro-bundles/SKILL.md')
    for phrase in ['P00–P05','OpenFilm CLI','VieNeu-TTS','GPU','CPU','Phê duyệt cài đặt',
                   'M0','M1','M2','M3','M4','M5','M6','M7','đã duyệt','QC']:
        assert phrase in s
    for risk in ['MODEL_DOWNLOAD','PACKAGE_INSTALL','GPU_TO_CPU_FALLBACK','VOICE_CLONING','PAID_ACTION','PUBLISH']:
        assert risk in s

def test_original_prompt_and_metadata_same_with_new_version():
    m=json.loads(read('plugin.json')); l=json.loads(read('.codex-plugin/plugin.json'))
    assert m['version']==l['version']=='1.14.0'
    assert m['name']==l['name']=='video-hoat-hinh'
    assert m['extensions']['com.openai']['interface']==l['interface']
    assert len(l['interface']['defaultPrompt'])==3

def test_macro_source_and_existing_99_template_refs():
    policy=json.loads(read('skills/openfilm-macro-bundles/references/MACRO_POLICY.json'))
    defs=json.loads(read('skills/openfilm-high-workpackets/references/WORKPACKET_DEFINITIONS.json'))
    assert [x['id'] for x in policy['macros']]==[f'M{i}' for i in range(8)]
    assert sum(len(x['packets']) for x in defs['stages'])==99
    assert len(list((ROOT/'skills').glob('*/SKILL.md')))==33
