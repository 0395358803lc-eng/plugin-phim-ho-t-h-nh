"""One-time safe FilmData->OpenFilm placeholder scaffold. No renderer; no overwrite.

Requires explicit --create for writes. Does not copy/edit users' existing files.
"""
import argparse,html,json,re
from pathlib import Path

def within(path,root):
 return path.resolve().is_relative_to(root.resolve())

def plan(workspace,project,data):
 root=Path(workspace).resolve();project=Path(project).resolve()
 if not root.is_dir():raise ValueError('workspace does not exist')
 if not within(project,root):raise ValueError('project outside workspace')
 if not within(data,root):raise ValueError('film data outside workspace')
 f=json.loads(Path(data).read_text(encoding='utf-8'))
 fps=f.get('fps');shots=f.get('shots');width=f.get('width');height=f.get('height')
 if not isinstance(fps,int) or fps<=0 or not isinstance(width,int) or width<=0 or not isinstance(height,int) or height<=0 or not isinstance(shots,list) or not shots:raise ValueError('invalid FilmData metadata')
 rows=[];used=set();ends=0
 for s in shots:
  i=s.get('id');start=s.get('startFrame');dur=s.get('durationInFrames')
  if not isinstance(i,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,90}',i) or i in used:raise ValueError('unsafe/duplicate shot id')
  if not isinstance(start,int) or not isinstance(dur,int) or start<0 or dur<=0 or start<ends:raise ValueError('invalid/overlapping shot frames')
  used.add(i);ends=start+dur;rows.append((i,start,dur))
 if f.get('durationInFrames')!=ends:raise ValueError('shot frames do not match full duration')
 return width,height,fps,rows

def build(workspace,project,data,create=False):
 width,height,fps,rows=plan(workspace,project,data)
 root=Path(workspace).resolve();project=Path(project).resolve();d=project/'openfilm';scenes=d/'scenes';film=d/'film.html'
 if any(not within(path,root) for path in (d,scenes,film)):
  raise ValueError('output path resolves outside workspace')
 generated=[]
 parts=[f'<meta charset="utf-8"><meta name="viewport" content="width={width}, height={height}">', '<section>']
 for i,start,dur in rows:
  src=f'scenes/{i}.html#t=0,{dur/fps:.6f}'.rstrip('0').rstrip('.')
  parts.append(f'<iframe id="{i}" src="{src}" at="{start/fps:.6f}" style="width:{width}px;height:{height}px"></iframe>')
 parts.append('</section>')
 film_html='<!doctype html><html lang="vi"><head>'+parts[0]+'</head><body>\n'+'\n'.join(parts[1:])+'\n</body></html>\n'
 to_write=[(film,film_html)]
 for i,start,dur in rows:
  page=f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>body{{margin:0;width:{width}px;height:{height}px;background:#252537;color:#fff;font:32px system-ui}}main{{padding:48px}}</style></head><body data-vhh-placeholder="true"><main>PLACEHOLDER — {html.escape(i)} (chưa dựng cảnh)</main><script>window.film={{duration:{dur/fps:.6f},frame(t){{}}}};</script></body></html>\n'''
  to_write.append((scenes/f'{i}.html',page))
 existing=[str(p) for p,_ in to_write if p.exists()]
 if create:
  if existing:raise FileExistsError('refuse overwrite existing: '+', '.join(existing))
  scenes.mkdir(parents=True,exist_ok=True)
  for p,t in to_write:
   with p.open('x',encoding='utf-8') as out:out.write(t)
  generated=[str(p) for p,_ in to_write]
 return {'status':'CREATED' if create else 'PLAN','sceneCount':len(rows),'paths':[str(p) for p,_ in to_write],'existing':existing,'generated':generated,'placeholderCount':len(rows)}

def check_ready(project,data=None):
 project=Path(project).resolve();d=project/'openfilm';film=d/'film.html'
 if not d.resolve().is_relative_to(project) or not film.resolve().is_relative_to(project):return ['project OpenFilm path resolves outside project']
 if not film.is_file():return ['missing film.html']
 issues=[]
 if data:
  f=json.loads(Path(data).read_text(encoding='utf-8'))
  for s in f['shots']:
   i=s['id'];p=d/'scenes'/f'{i}.html'
   if not p.resolve().is_relative_to(project):issues.append(f'scene resolves outside project: {i}');continue
   if not p.is_file():issues.append(f'missing scene {i}');continue
   t=p.read_text(encoding='utf-8')
   if 'data-vhh-placeholder="true"' in t:issues.append(f'placeholder still present: {i}')
  txt=film.read_text(encoding='utf-8')
  for s in f['shots']:
   if f'id="{s["id"]}"' not in txt:issues.append('missing timeline shot '+s['id'])
 return issues

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--project',type=Path,required=True);p.add_argument('--film-data',type=Path,required=True);p.add_argument('--create',action='store_true');p.add_argument('--check-ready',action='store_true')
 a=p.parse_args()
 try:
  if a.check_ready:
   e=check_ready(a.project,a.film_data);print(json.dumps({'status':'PASS' if not e else 'BLOCKED','errors':e},ensure_ascii=False));raise SystemExit(0 if not e else 2)
  print(json.dumps(build(a.workspace,a.project,a.film_data,a.create),ensure_ascii=False,indent=2))
 except Exception as e:
  print(json.dumps({'status':'BLOCKED','reason':str(e)},ensure_ascii=False));raise SystemExit(2)
