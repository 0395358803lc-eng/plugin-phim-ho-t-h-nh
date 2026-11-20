from pathlib import Path
import importlib.util,pytest
ROOT=Path(__file__).resolve().parents[1]
file=ROOT/'skills/openfilm-visual-inspection/references/sample_render_frames.py'
sp=importlib.util.spec_from_file_location('sampler',file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

film={'fps':30,'shots':[{'id':'C001','startFrame':0,'durationInFrames':60},{'id':'C002','startFrame':60,'durationInFrames':90}]}

def test_all_draft_and_master_shots_have_three_distinct_roles():
    for macro in ['M6','M7']:
        rows=m.sample_frames(film,macro,150)
        assert len(rows)==6
        assert rows[0]==('C001','START',0) and rows[1]==('C001','MID',29) and rows[2]==('C001','END',59)
        assert rows[3]==('C002','START',60) and rows[-1]==('C002','END',149)

def test_smoke_has_five_legal_frames_at_all_positions():
    rows=m.sample_frames(None,'M5',150)
    assert [x[1] for x in rows]==['START','Q1','MID','Q3','END']
    assert rows[0][-1]==0 and rows[-1][-1]==149

def test_no_fake_missing_scene_or_frame_spans():
    for shots in [[{'id':'C001','startFrame':0,'durationInFrames':200}],
                  [{'id':'C001','startFrame':0,'durationInFrames':60},{'id':'C001','startFrame':60,'durationInFrames':90}]]:
        with pytest.raises(ValueError):m.sample_frames({'shots':shots},'M6',150)
    with pytest.raises(ValueError):m.sample_frames(None,'M6',150)

def test_output_path_rejects_traversal_and_absolute(tmp_path):
    for path in ['../secret.png','C:/outside.png','/tmp/a.png','qc//bad.png','qc\\..\\bad.png']:
        with pytest.raises(ValueError):m.within_workspace(tmp_path,path)
    assert m.within_workspace(tmp_path,'qc/visual/M6/frames/C001.png').is_relative_to(tmp_path)
