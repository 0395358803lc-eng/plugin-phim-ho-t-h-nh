"""Strict file/hash/sampling gate for ChatGPT-reported visual inspection.

IMPORTANT: This checks file integrity and receipt structure, NOT that an LLM
actually saw pixels. Only the assistant can truthfully attest image was surfaced
as multimodal content. JSON/log/paths alone cannot establish visual perception.
"""
from __future__ import annotations
import argparse,hashlib,json,re,struct,zlib
from pathlib import Path

HEX=re.compile(r"^[0-9a-fA-F]{64}$")
VIDEO={"M5","M6","M7"}

def _rel(p):
    if not isinstance(p,str) or not p or p.startswith(("/","\\")) or ":" in p or "\0" in p:
        return False
    return all(v not in ("","..") for v in p.replace("\\","/").split("/"))

def _file(root,p):
    if not _rel(p): raise ValueError(f"unsafe relative path: {p}")
    dest=(root/p.replace("\\","/")).resolve()
    if not dest.is_relative_to(root) or not dest.is_file(): raise ValueError(f"missing/outside workspace: {p}")
    return dest

def _file_hash(root,p,claimed,errors,label):
    if not isinstance(claimed,str) or not HEX.fullmatch(claimed):
        errors.append(f"{label} missing/invalid sha256");return None
    try:
        f=_file(root,p)
        real=hashlib.sha256(f.read_bytes()).hexdigest()
        if real.lower()!=claimed.lower():errors.append(f"{label} hash mismatch")
        return f
    except (ValueError,OSError,TypeError) as exc:
        errors.append(f"{label} {exc}");return None

def _png_dimensions(data):
    """Check PNG chunks, CRC and decompressible scanlines using Python stdlib.

    Deliberately limited to standard noninterlaced PNG screenshots from
    OpenFilm/FFmpeg; convert other input formats to PNG before QC.
    """
    if len(data)<45 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG image")
    offset=8; width=height=0; bit_depth=color_type=interlace=None
    seen_ihdr=seen_iend=False; idat=[]
    while offset + 12 <= len(data):
        size=struct.unpack(">I",data[offset:offset+4])[0]
        tag=data[offset+4:offset+8]
        end=offset+12+size
        if end>len(data):raise ValueError('truncated PNG chunk')
        chunk=data[offset+8:offset+8+size]
        crc=struct.unpack('>I',data[offset+8+size:end])[0]
        if zlib.crc32(tag+chunk)&0xffffffff != crc:raise ValueError('PNG CRC mismatch')
        if tag==b'IHDR':
            if seen_ihdr or size!=13:raise ValueError('invalid duplicate or short PNG IHDR')
            seen_ihdr=True
            width,height,bit_depth,color_type,compression,filter_method,interlace=struct.unpack('>IIBBBBB',chunk)
            if compression!=0 or filter_method!=0 or interlace!=0:
                raise ValueError('unsupported PNG image encoding; convert to standard PNG')
        elif tag==b'IDAT':idat.append(chunk)
        elif tag==b'IEND':
            seen_iend=True
            if size!=0:raise ValueError('PNG IEND invalid')
            break
        offset=end
    if not seen_ihdr or not seen_iend or not idat or width==0 or height==0:
        raise ValueError('incomplete PNG image')
    channels={0:1,2:3,3:1,4:2,6:4}.get(color_type)
    if channels is None or bit_depth not in (1,2,4,8,16):raise ValueError('unsupported PNG color format')
    row_bytes=(width*channels*bit_depth+7)//8+1
    target=row_bytes*height
    if target>140*1024*1024:raise ValueError('image too large for safe decode validation')
    try:
        d=zlib.decompressobj()
        payload=d.decompress(b''.join(idat),target+1)
        if not d.eof or len(payload)!=target:raise ValueError('PNG pixel stream malformed')
    except zlib.error as exc:raise ValueError('PNG IDAT cannot be decompressed') from exc
    return width,height

def validate(report:dict,policy:dict,workspace:Path,expected_targets:list|None=None)->list[str]:
    """Return blocking errors, not an automatic assertion of real visual perception."""
    errors=[]
    if not isinstance(report,dict):return ['visual report is not an object']
    mid=report.get('macroId'); cfg=policy.get('requiredMacros',{}).get(mid)
    if cfg is None:return ['macroId is not a mandatory visual macro']
    if report.get('schemaVersion')!=1:errors.append('visual report schemaVersion invalid')
    if report.get('status')!='VISUAL_PASS':errors.append('visual verdict not PASS')
    if report.get('reviewer')!='CHATGPT_VISION':errors.append('reviewer must be ChatGPT vision')
    if not isinstance(report.get('reviewId'),str) or len(report['reviewId'])<8:errors.append('missing reviewId')
    if report.get('reviewScope')!='SAMPLED_FRAMES_NOT_FULL_PLAYBACK':errors.append('cannot claim full playback from sampled frames')
    src=report.get('source',{})
    if not isinstance(src,dict):src={}
    if src.get('kind')!=cfg['sourceKind']:errors.append('source kind mismatch: draft/storyboard cannot replace master/smoke')
    root=Path(workspace).resolve()
    source_file=_file_hash(root,src.get('path'),src.get('sha256'),errors,'source media')
    if mid in VIDEO and source_file and source_file.suffix.lower()!='.mp4':errors.append('render visual source is not MP4')
    if mid in VIDEO and source_file:
        data=source_file.read_bytes()[:24]
        if len(data)<12 or data[4:8]!=b'ftyp':errors.append('source video is not an MP4 container')
    required=report.get('requiredTargets')
    if not isinstance(required,list) or not required or any(not isinstance(x,str) or not x.strip() for x in required):
        errors.append('missing actual target list');required=[]
    if len(set(required))!=len(required):errors.append('duplicate visual targets')
    if expected_targets is not None and set(required)!=set(expected_targets):errors.append('missing/extra targets compared with materialized shot/asset manifest')
    observations=report.get('observations',[])
    if not isinstance(observations,list) or not observations:errors.append('no image observations');observations=[]
    seen=set()
    for i,obs in enumerate(observations):
        label=f'observation {i}'
        if not isinstance(obs,dict):errors.append(f'{label} invalid');continue
        tid,role=obs.get('targetId'),obs.get('frameRole')
        if tid not in required:errors.append(f'{label} unregistered target')
        if role not in cfg['requiredFrameRoles']:errors.append(f'{label} unexpected frame role')
        if (tid,role) in seen:errors.append(f'{label} duplicate role')
        seen.add((tid,role))
        if obs.get('imageActuallyReceived') is not True:errors.append(f'{label} image was not actually received in multimodal model context')
        if obs.get('transferMethod') not in policy['imageTransferAllowed']:errors.append(f'{label} unsupported image transfer')
        receipt=obs.get('hostImageEvidence')
        if not isinstance(receipt,str) or len(receipt.strip())<8:errors.append(f'{label} no actual host image receipt')
        comment=obs.get('observation')
        if not isinstance(comment,str) or len(comment.strip())<40 or comment.strip().lower() in ('ok','pass','good','no issue'):
            errors.append(f'{label} requires scene-specific visual analysis')
        if obs.get('assessment')!='PASS' or obs.get('issues')!=[]:
            errors.append(f'{label} visual FAIL/BLOCKED/unresolved issues')
        if obs.get('sourceSha256')!=src.get('sha256'):errors.append(f'{label} stale source/shot/render hash')
        image=_file_hash(root,obs.get('imagePath'),obs.get('imageSha256'),errors,f'{label} image')
        if image:
            try:
                w,h=_png_dimensions(image.read_bytes())
                if w<int(policy['minimumImageWidth']) or h<int(policy['minimumImageHeight']):
                    errors.append(f'{label} image too small for visual QC')
            except ValueError as e:errors.append(f'{label} image decode/header invalid: {e}')
    for tid in required:
        for role in cfg['requiredFrameRoles']:
            if (tid,role) not in seen:errors.append(f'missing frame sample {tid}/{role}')
    if mid in VIDEO or mid=='M4':
        extract=_file_hash(root,report.get('extractionEvidencePath'),report.get('extractionEvidenceSha256'),errors,'extraction evidence')
        if extract:
            try:
                log=json.loads(extract.read_text(encoding='utf-8'))
                engine='OPENFILM_CLI' if mid=='M4' else 'FFMPEG_FROM_RENDERED_MP4'
                if log.get('sourcePath')!=src.get('path') or log.get('sourceSha256')!=src.get('sha256') or log.get('exitCode')!=0 or log.get('engine')!=engine:
                    errors.append('image extraction provenance mismatch')
                log_images=log.get('imagePaths',[])
                if not isinstance(log_images,list) or set(log_images)!=set(obs.get('imagePath') for obs in observations if isinstance(obs,dict)):
                    errors.append('extraction log not matched to delivered image paths')
            except (ValueError,TypeError,KeyError) as e:errors.append(f'bad extraction log: {e}')
    return errors

def validate_report_file(report_path:Path,policy:dict,workspace:Path,expected_targets:list|None=None)->list[str]:
    root=Path(workspace).resolve()
    try:
        p=Path(report_path).resolve()
        if not p.is_relative_to(root):return ['visual report outside workspace']
        obj=json.loads(p.read_text(encoding='utf-8'))
        return validate(obj,policy,root,expected_targets)
    except (OSError,ValueError,TypeError) as e:
        return [f'visual report missing/unreadable: {e}']

if __name__=='__main__':
    ap=argparse.ArgumentParser(description='Validate actual PNG/frame/media hashes and visual QC receipt metadata. Does not see pixels for the model.')
    ap.add_argument('report',type=Path)
    ap.add_argument('--workspace',type=Path,required=True)
    ap.add_argument('--policy',type=Path,default=Path(__file__).with_name('VISUAL_QC_POLICY.json'))
    ap.add_argument('--targets-json',type=Path,help='JSON array of materialized scene/asset IDs that MUST all be reviewed')
    args=ap.parse_args()
    target_ids=json.loads(args.targets_json.read_text('utf-8')) if args.targets_json else None
    issues=validate_report_file(args.report,json.loads(args.policy.read_text('utf-8')),args.workspace,target_ids)
    print(json.dumps({'status':'QC_METADATA_AND_HASHES_PASS' if not issues else 'VISUAL_BLOCKED','errors':issues,'warning':'Only the model, after real multimodal image receipt, can honestly attest visual inspection; this script cannot verify that perception.'},ensure_ascii=False,indent=2))
    raise SystemExit(0 if not issues else 2)
