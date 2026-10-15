"""Reconstruct XML-only OOXML changes; original binary media never leaves its ZIP.

The payload is data, never executable Python or a request to a private endpoint.
Every source part and resulting XML is checked before writing a candidate deck.
"""

import base64
import hashlib
import json
import lzma
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4

from lxml import etree

MAX_PAYLOAD = 2_000_000
MAX_IMAGE_PAYLOAD = 240_000
MAX_UNPACKED = 64 * 1024**2
MAX_XML = 16 * 1024**2
SHA = re.compile(r'[0-9a-f]{64}\Z')


def decode_image(path,nonce):
    """Read an explicit RGB data image, rejecting scaling/corruption/stale jobs."""
    import struct

    import numpy as np
    from PIL import Image

    if not isinstance(nonce,str) or not re.fullmatch(r'[0-9a-f]{32}',nonce):
        raise ValueError('Mã nhận bài giảng không hợp lệ.')
    with Image.open(path) as image:
        width,height=image.size
        if width!=1056 or not 33<=height<=700:
            raise ValueError('Ảnh dữ liệu bài giảng không đúng kích thước.')
        body=np.asarray(image.convert('RGB'))[16:-16,16:-16,:]
        raw=np.packbits((body.reshape(-1)>127).astype(np.uint8),bitorder='big').tobytes()
    if raw[:8]!=b'BLCIMG02' or raw[8:24]!=bytes.fromhex(nonce):
        raise ValueError('Ảnh nhận về không thuộc lượt xử lý này.')
    size=struct.unpack('>I',raw[24:28])[0]
    if not 0<size<=MAX_IMAGE_PAYLOAD:
        raise ValueError('Dữ liệu nhận bài giảng vượt giới hạn.')
    data=raw[60:60+size]
    if len(data)!=size or hashlib.sha256(data).digest()!=raw[28:60]:
        raise ValueError('Ảnh dữ liệu bị thay đổi; chưa dùng để ghép bài.')
    return data.decode('utf-8')


def decode(text):
    if len(text)>MAX_PAYLOAD:
        raise ValueError('Dữ liệu nhận bài giảng vượt giới hạn.')
    text=re.sub(r'^(?:ChatGPT said|ChatGPT đã nói|ChatGPT nói)\s*:\s*','',text.strip(),count=1)
    fence=re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```',text,re.I)
    if fence:
        text=fence[1]
    envelope=json.loads(text)
    if (not isinstance(envelope,dict) or set(envelope)!={'format','sha256','unpacked_bytes','data_b64'}
            or envelope['format'] not in {'biliclass-ooxml-patch-xz-v1','biliclass-ooxml-xz-v1'}
            or not isinstance(envelope['sha256'],str) or not SHA.fullmatch(envelope['sha256'])
            or type(envelope['unpacked_bytes']) is not int or not 0<envelope['unpacked_bytes']<=MAX_UNPACKED
            or not isinstance(envelope['data_b64'],str)):
        raise ValueError('Gói nội dung bài giảng chưa đúng định dạng.')
    compressed=base64.b64decode(envelope['data_b64'],validate=True)
    decoder=lzma.LZMADecompressor(memlimit=128*1024**2)
    raw=decoder.decompress(compressed,max_length=envelope['unpacked_bytes']+1)
    if (not decoder.eof or decoder.unused_data or len(raw)!=envelope['unpacked_bytes']
            or hashlib.sha256(raw).hexdigest()!=envelope['sha256']):
        raise ValueError('Nội dung bài giảng chưa khớp kiểm tra toàn vẹn.')
    payload=json.loads(raw)
    if (not isinstance(payload,dict) or set(payload)!={'format','source_sha256','target_part_count','removed','parts'}
            or payload['format']!=('biliclass-ooxml-patch-v1' if envelope['format']=='biliclass-ooxml-patch-xz-v1'
                                  else 'biliclass-ooxml-text-v1')
            or not isinstance(payload['source_sha256'],str) or not SHA.fullmatch(payload['source_sha256'])
            or type(payload['target_part_count']) is not int or not 1<=payload['target_part_count']<=10000
            or not isinstance(payload['removed'],list) or not isinstance(payload['parts'],list)
            or len(payload['parts'])>10000 or len(payload['removed'])>10000):
        raise ValueError('Danh sách thay đổi bài giảng không hợp lệ.')
    return payload


def _xml_name(name):
    if not isinstance(name,str) or not name or len(name)>300 or '\\' in name or ':' in name:
        raise ValueError('Tên thành phần bài giảng không hợp lệ.')
    path=PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts or str(path)!=name
            or not (name=='[Content_Types].xml' or path.suffix in {'.xml','.rels'})):
        raise ValueError('Chỉ được nhận thay đổi XML, không sửa hình/video/âm thanh.')
    return name


def _xml(data):
    if len(data)>MAX_XML:
        raise ValueError('Một thành phần bài giảng quá lớn.')
    root=etree.fromstring(data,etree.XMLParser(resolve_entities=False,no_network=True))
    if root.getroottree().docinfo.doctype:
        raise ValueError('Không nhận XML có khai báo thực thể ngoài.')
    return root


def _external(root):
    return {(n.get('Type',''),n.get('Target','')) for n in root.iter()
            if etree.QName(n).localname=='Relationship' and n.get('TargetMode')=='External'}


def apply(source,destination,text):
    from .importers import inspect_zip
    from .source_deck import source_slide_parts

    source,destination=Path(source),Path(destination)
    if source.resolve()==destination.resolve():
        raise ValueError('Không ghi đè PowerPoint nguồn khi nhận bài.')
    payload=decode(text)
    with source.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=payload['source_sha256']:
            raise ValueError('Bản nhận không thuộc đúng PowerPoint nguồn của nhóm này.')
    inspect_zip(source)
    changed={}
    with zipfile.ZipFile(source) as old:
        infos=old.infolist()
        names={i.filename for i in infos}
        if len(names)!=len(infos):
            raise ValueError('PowerPoint nguồn có thành phần trùng tên.')
        removed={_xml_name(n) for n in payload['removed']}
        if (len(removed)!=len(payload['removed']) or not removed<=names
                or removed & {'[Content_Types].xml','ppt/presentation.xml','_rels/.rels'}):
            raise ValueError('Danh sách thành phần bị loại bỏ không hợp lệ.')
        allowed_external=set()
        for name in names:
            if name.endswith('.rels'):
                allowed_external.update(_external(_xml(old.read(name))))
        for part in payload['parts']:
            if isinstance(part,dict) and payload['format']=='biliclass-ooxml-text-v1':
                if set(part)!={'name','sha256','xml'} or not isinstance(part['xml'],str):
                    raise ValueError('Một thành phần nhận về chưa đủ thông tin.')
                name=_xml_name(part['name'])
                original=old.read(name) if name in names else b''
                part={'name':name,'sha256':part['sha256'],'source_sha256':hashlib.sha256(original).hexdigest(),
                      'edits':[[0,len(original),base64.b64encode(part['xml'].encode('utf-8')).decode('ascii')]]}
            if not isinstance(part,dict) or set(part)!={'name','source_sha256','sha256','edits'}:
                raise ValueError('Một thành phần nhận về chưa đủ thông tin.')
            name=_xml_name(part['name'])
            if name in changed or name in removed or not isinstance(part['edits'],list):
                raise ValueError('Thay đổi thành phần bị trùng hoặc mâu thuẫn.')
            original=old.read(name) if name in names else b''
            if len(original)>MAX_XML or hashlib.sha256(original).hexdigest()!=part['source_sha256']:
                raise ValueError('Thành phần nguồn đã thay đổi.')
            chunks=[]
            cursor=0
            size=0
            for edit in part['edits']:
                if (not isinstance(edit,list) or len(edit)!=3 or type(edit[0]) is not int or type(edit[1]) is not int
                        or not cursor<=edit[0]<=edit[1]<=len(original) or not isinstance(edit[2],str)):
                    raise ValueError('Vị trí thay đổi bị chồng lấn hoặc không thuộc nguồn.')
                replacement=base64.b64decode(edit[2],validate=True)
                size+=edit[0]-cursor+len(replacement)
                if size>MAX_XML:
                    raise ValueError('Thành phần nhận về vượt giới hạn.')
                chunks.extend((original[cursor:edit[0]],replacement))
                cursor=edit[1]
            chunks.append(original[cursor:])
            data=b''.join(chunks)
            if len(data)>MAX_XML or hashlib.sha256(data).hexdigest()!=part['sha256']:
                raise ValueError('Thành phần nhận về chưa khớp checksum.')
            root=_xml(data)
            if original and _xml(original).tag!=root.tag:
                raise ValueError('Loại thành phần bài giảng đã bị thay đổi.')
            if name.endswith('.rels') and not _external(root)<=allowed_external:
                raise ValueError('Không nhận liên kết ngoài mới trong bản ghép bài.')
            if name=='[Content_Types].xml':
                before={n.get('ContentType','').casefold() for n in _xml(original)}
                for node in root:
                    kind=node.get('ContentType','').casefold()
                    if re.search(r'vba|macroenabled|activex|oleobject|script',kind) and kind not in before:
                        raise ValueError('Không nhận thành phần thực thi mới trong bài giảng.')
            changed[name]=data
        if len((names-removed)|set(changed))!=payload['target_part_count']:
            raise ValueError('Bản nhận chưa đủ thành phần bài giảng.')
        destination.parent.mkdir(parents=True,exist_ok=True)
        pending=destination.with_name(destination.stem+'.'+uuid4().hex+'.pending.pptx')
        try:
            with zipfile.ZipFile(pending,'w',compression=zipfile.ZIP_DEFLATED) as output:
                for info in infos:
                    if info.filename in removed:
                        continue
                    if info.filename in changed:
                        output.writestr(info,changed[info.filename])
                    else:
                        with old.open(info) as reader,output.open(info,'w') as writer:
                            shutil.copyfileobj(reader,writer)
                for name in sorted(set(changed)-names):
                    output.writestr(name,changed[name])
            inspect_zip(pending)
            if len(source_slide_parts(source))!=len(source_slide_parts(pending)):
                raise ValueError('Bản nhận đã thay đổi số slide của nhóm.')
            pending.replace(destination)
        finally:
            pending.unlink(missing_ok=True)
    return destination
