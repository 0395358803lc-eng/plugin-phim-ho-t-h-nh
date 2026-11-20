"""Build a real, local three-scene OpenFilm sample from already synthesized WAV.

No model/network/install operations. Separate immutable version source folders.
"""
import argparse, hashlib, html, importlib.util, json, math, shutil, wave
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(root,path,text):
    p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:f.write(text)
def record(root,path,data):write(root,path,json.dumps(data,ensure_ascii=False,indent=2))
def timestamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

ROBOT='''<g id="robot"><ellipse cx="0" cy="4" rx="64" ry="12" fill="#163c3a" opacity=".14"/>
<g id="body"><path d="M-32-68L-49-22M32-68L50-30" stroke="#284d4b" stroke-width="13" stroke-linecap="round"/>
<path d="M-20-25L-25-3M20-25L25-3" stroke="#284d4b" stroke-width="17" stroke-linecap="round"/>
<rect x="-38" y="-90" width="76" height="68" rx="22" fill="#f7b653" stroke="#284d4b" stroke-width="4"/>
<rect x="-47" y="-156" width="94" height="70" rx="25" fill="#f9cb72" stroke="#284d4b" stroke-width="4"/>
<rect x="-34" y="-141" width="68" height="38" rx="15" fill="#234f50"/>
<path d="M-20-123L-13-123M13-123L20-123" stroke="#cefcdb" stroke-width="7" stroke-linecap="round"/>
<path d="M-6-111Q0-106 6-111" fill="none" stroke="#cefcdb" stroke-width="3"/>
<path d="M0-157V-176M0-172Q-17-195-25-179Q-16-166 0-172M0-172Q17-196 25-180Q17-166 0-172" fill="#469d69" stroke="#284d4b" stroke-width="3"/>
<g id="seed"><circle cy="-61" r="18" fill="#fff5d4"/><path d="M-5-52Q-16-68 0-73Q17-65 4-52Z" fill="#87532e"/><path d="M0-53V-64" stroke="#d3a66e" stroke-width="2"/></g></g></g>'''

def scene(sid,duration,cues,revised=False):
    titles={'S01':('01 / LÊN ĐƯỜNG','Một nhiệm vụ nhỏ'), 'S02':('02 / QUA CẦU','Chậm lại để đi xa'), 'S03':('03 / KHU VƯỜN','Bắt đầu từ một hạt mầm')}
    number,title=titles[sid]
    common='''<rect width="1280" height="720" fill="#eaf3db"/><circle cx="1070" cy="154" r="62" fill="#f8d784"/>
<g id="clouds" fill="#fffdf0" opacity=".9"><ellipse cx="310" cy="150" rx="88" ry="22"/><ellipse cx="280" cy="130" rx="37" ry="30"/><ellipse cx="900" cy="235" rx="85" ry="20"/></g>
<path d="M0 425Q220 180 480 420Q740 250 1000 420Q1180 330 1280 405V720H0Z" fill="#b3cba1"/>
<path d="M0 470Q250 330 540 470Q870 330 1280 455V720H0Z" fill="#779d7c"/>
<path d="M0 515Q420 460 1280 510V720H0Z" fill="#d1dcb2"/>'''
    setpieces=''
    if sid=='S01':
        setpieces='''<path d="M0 583Q430 470 1280 560" fill="none" stroke="#edd8a6" stroke-width="57"/>
<g transform="translate(1030 485)"><path d="M0 0V-125" stroke="#79644b" stroke-width="13"/><path d="M-70-130H60L85-105 60-80H-70Z" fill="#fff3cf"/><text x="-51" y="-96" fill="#36564b" font-size="20">KHU VƯỜN</text></g>'''
        motion="tl.fromTo('#robot',{x:160,y:530},{x:940,y:530,duration:D,ease:'none'},0);"
    elif sid=='S02':
        setpieces='''<path d="M520 450Q650 455 700 720H410Q580 560 520 450" fill="#7cbfc2"/>
<path d="M480 588L610 588M465 634L641 634M490 681L646 681" stroke="#d5eff0" stroke-width="5" stroke-linecap="round"/>
<path d="M265 520H510M610 520H950" stroke="#936b47" stroke-width="26"/>
<path id="plank" d="M510 520H610" stroke="#d6a963" stroke-width="26"/>
<path d="M315 520V580M870 520V580" stroke="#765339" stroke-width="16"/>
<path id="rail" d="M330 515V425M870 515V425M330 445H870" stroke="RAIL" stroke-width="12" fill="none" stroke-linecap="round"/>
<g id="spark" stroke="#fff8c4" stroke-width="5"><path d="M560 450V428M530 463L514 451M591 463L607 451"/></g>'''.replace('RAIL','#f6bc42' if revised else '#9e7956')
        motion="tl.fromTo('#robot',{x:190,y:510},{x:438,y:510,duration:D*.3,ease:'power1.inOut'},0).to('#robot',{x:970,duration:D*.36,ease:'power1.inOut'},D*.62);tl.fromTo('#plank',{y:-150,opacity:0},{y:0,opacity:1,duration:D*.18,ease:'power2.out'},D*.36);tl.fromTo('#spark',{opacity:0},{opacity:1,duration:.3},D*.54).to('#spark',{opacity:0,duration:.5},D*.62);"
        if revised:motion+="tl.fromTo('#rail',{opacity:.25},{opacity:1,duration:.8},D*.60);"
    else:
        setpieces='''<ellipse cx="745" cy="527" rx="165" ry="38" fill="#9c7450"/>
<g id="sprout" transform="translate(740 520)"><path d="M0 0Q-16-95 0-158" stroke="#386d49" stroke-width="13" fill="none"/>
<path d="M-3-70Q-110-160-120-72Q-75-20-3-70M-6-112Q95-207 112-120Q60-55-6-112" fill="#5d9b60" stroke="#386d49" stroke-width="3"/></g>
<g id="water" fill="#86d1da"><ellipse cx="673" cy="455" rx="5" ry="12"/><ellipse cx="702" cy="474" rx="5" ry="12"/><ellipse cx="728" cy="485" rx="5" ry="12"/></g>
<path d="M215 526H420M1010 526H1220" stroke="#9c7450" stroke-width="7" stroke-dasharray="18 12"/>'''
        motion="tl.fromTo('#robot',{x:190,y:510},{x:615,y:510,duration:D*.32,ease:'power1.inOut'},0);tl.to('#seed',{opacity:0,duration:.6},D*.34);tl.fromTo('#water',{opacity:0,y:-25},{opacity:1,y:0,duration:.6},D*.42).to('#water',{opacity:0,duration:.6},D*.62);tl.fromTo('#sprout',{scale:0,svgOrigin:'740 520'},{scale:1,duration:D*.37,ease:'back.out(1.2)'},D*.5);"
    return '''<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;width:1280px;height:720px;overflow:hidden;font-family:Arial,sans-serif;background:#eaf3db}svg{position:absolute;inset:0;width:1280px;height:720px}.chapter{position:absolute;left:68px;top:48px;font-size:15px;letter-spacing:4px;color:#527265}.title{position:absolute;left:64px;top:78px;color:#244e45;font-size:45px;font-weight:700}#caption{position:absolute;left:110px;right:110px;bottom:42px;text-align:center;font-size:27px;line-height:1.35;color:#fffaf0;background:rgba(29,60,51,.90);border-radius:15px;padding:15px 24px;min-height:65px}.brand{position:absolute;right:55px;top:54px;color:#527265;font-size:15px;letter-spacing:2px}</style></head><body>
<svg viewBox="0 0 1280 720">'''+common+setpieces+ROBOT+'''</svg><div class="chapter">'''+number+'''</div><div class="title">'''+title+'''</div><div class="brand">MẦM / CHUYẾN ĐI ĐẦU TIÊN</div><div id="caption"></div>
<script src="../assets/gsap.min.js"></script><script>const D='''+str(duration)+''';const cues='''+json.dumps(cues,ensure_ascii=False)+''';const tl=gsap.timeline({paused:true});tl.fromTo('#clouds',{x:-35},{x:40,duration:D,ease:'none'},0);'''+motion+'''
window.film={duration:D,frame(t){t=Math.max(0,Math.min(D,t));tl.seek(t);document.querySelector('#body').setAttribute('transform',`translate(0 ${Math.sin(t*7)*2.4})`);const c=cues.find(c=>t>=c.start&&t<c.end);document.querySelector('#caption').textContent=c?c.text:'';document.querySelector('#caption').style.opacity=c?1:0;}};window.film.frame(0);</script></body></html>'''

def build(root,gsap):
    root=root.resolve();jobs=json.loads((root/'dialogue-jobs.json').read_text(encoding='utf-8'))
    if isinstance(jobs,dict):jobs=jobs['jobs']
    gpu=json.loads((root/'GPU_EXECUTION.json').read_text(encoding='utf-8'))
    if gpu['device']['backbone']!='cuda:0' or len(gpu['wav'])!=3:raise ValueError('actual GPU WAV evidence required')
    allcues=[];shots=[];dialogues=[];start=0
    for j in jobs:
        p=root/j['output']
        with wave.open(str(p),'rb') as w:duration=w.getnframes()/w.getframerate()
        length=math.ceil((duration+1.8)*24);sid=j['id'];parts=[]
        for sentence in j['text'].split('. '):
            words=sentence.split()
            # Short readable caption phrases, proportional timing from measured WAV.
            groups=math.ceil(len(words)/12);size=math.ceil(len(words)/groups)
            parts.extend(' '.join(words[k:k+size]) for k in range(0,len(words),size))
        n=sum(len(x.split()) for x in parts);cursor=.7;cues=[]
        for text in parts:
            end=cursor+duration*len(text.split())/n;cues.append({'start':cursor,'end':end,'text':text});cursor=end
        allcues.append(cues)
        shots.append({'id':sid,'startFrame':start,'durationInFrames':length,'type':'2d','scene':f'scenes/{sid}.html'})
        dialogues.append({'id':'D-'+sid,'shotId':sid,'speaker':j['voice'],'text':j['text'],'startFrame':start+17,'endFrame':start+17+math.ceil(duration*24),'audio':j['output']})
        start+=length
    film={'schemaVersion':1,'filmId':'mam-first-journey','masterEngine':'openfilm','fps':24,'width':1280,'height':720,'durationInFrames':start,'shots':shots,'dialogues':dialogues}
    validator=load(REPO/'skills/openfilm-filmdata/references/validate_filmdata.py','fv')
    errors=validator.validate(film,root)
    if errors:raise ValueError(errors)
    record(root,'film.json',film)
    source={
      'COT_TRUYEN.md':'# Chuyến đi đầu tiên của Mầm\nMầm mang hạt giống đến khu vườn. Chiếc cầu hỏng khiến bạn dừng lại để sửa. Một mầm cây xanh khép lại chuyến đi và mở ra sự sống mới.\n',
      'NHAN_VAT.md':'# Mầm\nRô bốt nhỏ màu vàng mật ong, mắt xanh sáng, hai lá trên đầu. Tính cách kiên nhẫn, biết chăm sóc. Hạt giống được mang trong hộp tròn trước ngực.\n',
      'KICH_BAN_HOAN_CHINH.md':'# Mầm — Chuyến đi đầu tiên\n'+ '\n\n'.join(j['id']+'\n'+j['text'] for j in jobs),
      'LOI_THOAI.md':'# Người kể chuyện — preset Hải Đăng\n'+ '\n\n'.join(j['id']+': '+j['text'] for j in jobs),
      'DANH_SACH_CANH.csv':'shotId,location,action\nS01,Đồi xanh,Mang hạt giống lên đường\nS02,Cầu gỗ,Dừng lại sửa cầu rồi đi tiếp\nS03,Khu vườn,Gieo hạt tưới nước và cây nảy mầm\n',
      'HUONG_DAN_HINH_ANH_AM_THANH.md':'# Thiết kế\n2D SVG + GSAP, 1280×720, 24 fps. Bảng màu xanh lá / mật ong. Ba góc máy toàn cảnh. VieNeu v3turbo PyTorch CUDA, preset Hải Đăng, WAV 48 kHz. Phụ đề câu ngắn theo thời lượng WAV; chưa forced alignment cấp từ. Không cần nhạc nền.\n',
      'BAO_CAO_NGHIEM_THU.md':'# Trạng thái đầu vào\nKịch bản mẫu do tác vụ kỹ thuật T31 tạo. Đủ bảy tệp; đây là ghi nhận chuẩn bị đầu vào, không phải người dùng chấp nhận chất lượng phim. Phim chờ đánh giá sau bàn giao.\n'}
    for name,text in source.items():write(root,'source/'+name,text)
    audit=load(REPO/'skills/openfilm-script-input/references/audit_seven_files.py','audit')
    record(root,'source-manifest.json',audit.audit(root/'source'))
    write(root,'storyboard.md','# Storyboard\n\n| Cảnh | Bố cục | Chuyển động | Điểm kết |\n|---|---|---|---|\n| S01 | Đồi xanh, biển chỉ vườn | Mầm đi từ trái sang phải; mây trôi | Đến phía cầu |\n| S02 | Suối chia đôi khung hình, cầu thiếu ván | Dừng, đặt ván, đi qua | Qua cầu an toàn |\n| S03 | Luống đất, khu vườn | Gieo, tưới, cây mọc | Cây mở hai lá |\n')
    write(root,'character.svg','<svg xmlns="http://www.w3.org/2000/svg" viewBox="-80 -210 160 240">'+ROBOT+'</svg>')
    record(root,'profile.json',{'engine':'OpenFilm CLI','animation':'SVG + local GSAP','fps':24,'width':1280,'height':720,'speech':'VieNeu CUDA','duration':start/24})
    versions={}
    for version in ('V01','V02'):
        folder=root/version;folder.mkdir();(folder/'assets').mkdir();shutil.copyfile(gsap,folder/'assets/gsap.min.js')
        body=[];audio=[];vtt=['WEBVTT\n'];srt=[];cue_id=0
        for shot,j,cues in zip(shots,jobs,allcues):
            sid=shot['id'];length=shot['durationInFrames']/24;at=shot['startFrame']/24
            write(folder,f'scenes/{sid}.html',scene(sid,length,cues,version=='V02' and sid=='S02'))
            body.append(f'<iframe src="scenes/{sid}.html#t=0,{length}" at="{at}" style="width:1280px;height:720px"></iframe>')
            with wave.open(str(root/j['output']),'rb') as w:duration=w.getnframes()/w.getframerate()
            # Copy WAV into version to keep every OpenFilm media URL inside its project root.
            (folder/'audio').mkdir(exist_ok=True);shutil.copyfile(root/j['output'],folder/j['output'])
            audio.append(f'<audio src="{j["output"]}#t=0,{duration}" at="{at+.7}"></audio>')
            for c in cues:
                cue_id+=1;line=timestamp(at+c['start'])+' --> '+timestamp(at+c['end'])
                vtt.append(line+'\n'+c['text']+'\n');srt.append(str(cue_id)+'\n'+line.replace('.',',')+'\n'+c['text']+'\n')
        write(folder,'captions.vtt','\n'.join(vtt));write(folder,'captions.srt','\n'.join(srt))
        write(folder,'film.html','<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=1280, height=720"></head><body><section>'+''.join(body)+'</section><section>'+''.join(audio)+'</section><section><track kind="captions" src="captions.vtt"></section></body></html>')
        record(folder,'film.json',film)
        versions[version]={p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*') if p.is_file()}
    changed=[p for p in versions['V01'] if versions['V01'][p]!=versions['V02'][p]]
    if changed!=['scenes/S02.html']:raise ValueError('unexpected revision changes '+str(changed))
    record(root,'SOURCE_VERSIONS.json',{'versions':versions,'changedFiles':changed,'feedback':{'simulated':True,'category':'effect','targetIds':['S02'],'request':'Đổi lan can cầu sang vàng và cho sáng dần sau khi sửa cầu; giữ nguyên cảnh khác, lời thoại và phụ đề.'}})
    print(json.dumps({'duration':start/24,'frames':start,'scenes':len(shots),'revisionChanges':changed},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--gsap',type=Path,required=True);a=p.parse_args();build(a.workspace,a.gsap)
