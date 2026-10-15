"""One bounded recovery for a known result whose ordinary file transfer failed.

Use only the signed-in conversation's normal reply/image UI. The web exports
XML data; the local codec verifies it and keeps original binary media intact.
"""

import hashlib
import json
import re
import shutil
import time
from pathlib import Path
from uuid import uuid4

from . import browser_automation as web
from .pptx_text_transport import apply, decode_image


def recovery_key(source,record):
    with Path(source).open('rb') as stream:
        source_hash=hashlib.file_digest(stream,'sha256').hexdigest()
    key=hashlib.sha256((source_hash+record.get('send_sha256','')).encode()).hexdigest()[:24]
    return key,source_hash


def export_prompt(source_name,source_hash,nonce):
    return f'''Đường tải tệp PowerPoint kết quả vừa tạo bị lỗi. Chỉ xuất dữ liệu từ đúng bản kết quả mới nhất đó; KHÔNG dịch, dựng hoặc render lại bài.
Nguồn đối chiếu là {source_name} đính kèm ban đầu, SHA-256 phải đúng {source_hash}. Nếu không tìm thấy đúng nguồn hoặc kết quả, trả {json.dumps({'error':'source_or_result_missing','request':nonce})} rồi dừng; không dựng lại.
Dùng Python zipfile so sánh từng ZIP entry của nguồn và kết quả. Giữ nguyên bytes XML kết quả. Nếu có thêm, xóa hoặc thay đổi bất kỳ thành phần NHỊ PHÂN nào (hình, video, âm thanh, đối tượng nhúng), trả JSON error và dừng. Chỉ xuất entry .xml/.rels hoặc [Content_Types].xml thực sự thay đổi/thêm.
Lập inner={{"format":"biliclass-ooxml-text-v1","source_sha256":"{source_hash}","target_part_count":số entry ZIP kết quả,"removed":[tên entry XML nguồn bị xóa],"parts":[{{"name":tên entry,"sha256":SHA-256 bytes XML kết quả,"xml":decode UTF-8 strict của đúng bytes XML}}]}}. Giữ mọi prefix/namespace/ký tự, không rút gọn XML. Kiểm tra encode UTF-8 lại khớp hash của từng part.
Serialize inner JSON compact ensure_ascii=False thành UTF-8 bytes. Nén TOÀN BỘ bytes bằng lzma.compress(preset=6), base64; lập envelope={{"format":"biliclass-ooxml-xz-v1","sha256":SHA-256 inner bytes,"unpacked_bytes":len inner bytes,"data_b64":base64 XZ bytes}}. Serialize envelope compact thành UTF-8 data. Nếu len(data)>240000, trả JSON error transfer_too_large và dừng. Kiểm tra giải nén/hash/part count được trước khi xuất.
Không in base64 dài, không đưa liên kết tải. Truyền data qua ảnh PNG lossless rõ ràng cho BiliClass: packet=b"BLCIMG02"+bytes.fromhex("{nonce}")+len(data).to_bytes(4,"big")+hashlib.sha256(data).digest()+data. Numpy unpackbits big-endian packet; W=1024, H=ceil(len(bits)/(W*3)); pad zero đủ W*H*3; reshape(H,W,3)*255 uint8. Tạo RGB PNG với viền trắng chính xác 16 px ở cả bốn cạnh. Không resize/anti-alias/palette/alpha, không thêm chữ lên dữ liệu. Tự decode lại ảnh pixel>127 để xác minh magic/request/len/hash/data trùng trước khi gửi.
Lưu /mnt/data/BiliClass_transfer_{nonce}.png và chỉ hiển thị inline bằng ![BiliClass transfer {nonce}](sandbox:/mnt/data/BiliClass_transfer_{nonce}.png). Đây là ảnh truyền dữ liệu của bài giáo viên đã yêu cầu, không phải slide cho học sinh. Không sửa hay xóa file PowerPoint kết quả.'''


def _capture(image,path):
    element=image.element_handle()
    if element is None:
        raise ValueError('Ảnh dữ liệu chưa xuất hiện.')
    try:
        # Only enlarge this explicit generated artifact for a lossless normal
        # screenshot. Restore the element immediately; no network/CSP changes.
        element.evaluate('''e=>{e._biliclassView={parent:e.parentNode,next:e.nextSibling,style:e.getAttribute('style')};
document.body.appendChild(e);e.style.cssText='position:fixed;left:0;top:0;z-index:2147483647;width:'+e.naturalWidth+'px;height:'+e.naturalHeight+'px;max-width:none;max-height:none;object-fit:fill;image-rendering:pixelated;border:0;border-radius:0;opacity:1;filter:none;transform:none;display:block';}''')
        height=element.evaluate('e=>e.naturalHeight')
        # Capture the Chrome viewport directly: Playwright's screenshot helper
        # waits for unrelated web fonts/animation frames in hidden windows.
        # This is a normal screenshot, not a file request or a security change.
        import base64

        page=element.owner_frame().page
        session=page.context.new_cdp_session(page)
        try:
            viewport=session.send('Page.getLayoutMetrics')['cssVisualViewport']
            result=session.send('Page.captureScreenshot',{'format':'png','fromSurface':True,
                'captureBeyondViewport':False,'clip':{'x':viewport['pageX'],'y':viewport['pageY'],
                    'width':1056,'height':height,'scale':1}})
            Path(path).write_bytes(base64.b64decode(result['data'],validate=True))
        finally:
            session.detach()
    finally:
        element.evaluate('''e=>{const s=e._biliclassView;if(!s)return;
if(s.next&&s.next.parentNode===s.parent)s.parent.insertBefore(e,s.next);else s.parent.appendChild(e);
if(s.style===null)e.removeAttribute('style');else e.setAttribute('style',s.style);delete e._biliclassView;}''')


def _adopt(folder,record,recovery,receipt,target):
    """Keep later focused corrections bound to the last acknowledged tool turn."""
    from .browser_receipt import save_intent

    current=(recovery/'send-intent.txt').read_text(encoding='utf-8')
    if hashlib.sha256(current.encode()).hexdigest()!=receipt.get('send_sha256'):
        raise web.BrowserProblem('record','Thiếu xác nhận của bước nhận bài; giữ nguyên tác vụ.')
    record.setdefault('result_origin_sha256',record.get('send_sha256',''))
    save_intent(folder,record,current)
    for field in ('assistant_before','assistant_ids_before','user_before'):
        if field in receipt:
            record[field]=receipt[field]
    record.update(candidate_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  candidate_send_sha256=record['send_sha256'],receive_data_key='')
    web.write_record(folder,record)


def receive(context,page,folder,record,request,target,cancel,progress,*,timeout=180):
    from .browser_receipt import recover_submission
    from .browser_wait import ResponseWait

    folder,target=Path(folder),Path(target)
    source=folder/request['config']['source_file']
    key,source_hash=recovery_key(source,record)
    recovery=folder/'receive-data'/key
    recovery.mkdir(parents=True,exist_ok=True)
    receipt=web.read_record(recovery,record['account_id'])
    nonce=receipt.setdefault('nonce',uuid4().hex)
    if not re.fullmatch(r'[0-9a-f]{32}',nonce):
        raise web.BrowserProblem('record','Mã nhận dữ liệu bài giảng không hợp lệ.')
    saved=recovery/'result.pptx'
    try:
        if receipt['state']=='completed' and saved.is_file():
            if (receipt.get('source_sha256')!=source_hash
                    or hashlib.sha256(saved.read_bytes()).hexdigest()!=receipt.get('sha256')):
                raise web.BrowserProblem('record','Bài giảng đã nhận bị thay đổi; giữ tác vụ để kiểm tra.')
            shutil.copyfile(saved,target)
            _adopt(folder,record,recovery,receipt,target)
            return target
        record['receive_data_key']=key
        web.write_record(folder,record)
        receipt.update(source_sha256=source_hash,require_highest_model=record.get('require_highest_model',True))
        if receipt['state']=='prepared':
            receipt['url']=record['url']
            web.write_record(recovery,receipt)
            progress('Đang nhận và hoàn thiện dữ liệu bài giảng…')
            try:
                web.submit(page,recovery,receipt,export_prompt(source.name,source_hash,nonce),cancel)
            except web.BrowserProblem as exc:
                if exc.code not in {'receipt','submission'} or receipt['state']!='submitting':
                    raise
                page=recover_submission(context,page,recovery,receipt,request,cancel)
        elif receipt['state']=='submitting':
            page=recover_submission(context,page,recovery,receipt,request,cancel)
        elif page.url!=receipt['url']:
            web.navigate(page,receipt['url'],cancel)
            web.require_account(page,cancel)
        last_notice=0
        with ResponseWait(recovery,receipt,timeout) as budget:
            while budget.checkpoint()>0:
                web.check_cancel(cancel)
                web.page_problem(page)
                reply=web.latest_reply(page,receipt.get('assistant_before',0),receipt.get('assistant_ids_before'))
                if reply is not None and not web.visible(page,web.STOP):
                    reply.scroll_into_view_if_needed(timeout=5000)
                    # The web may reuse a generic alt label for an artifact.
                    # The packet's nonce and hash, not an editable image label,
                    # establish that these bytes belong to this exact request.
                    images=reply.get_by_role('img',name=re.compile(r'^BiliClass transfer (?:'+nonce+r'|data)$'))
                    for image in images.all():
                        if not image.evaluate('e=>e.complete&&e.naturalWidth===1056&&e.naturalHeight>32'):
                            continue
                        screenshot=recovery/'received.png'
                        _capture(image,screenshot)
                        envelope=decode_image(screenshot,nonce)
                        apply(source,saved,envelope)
                        (recovery/'received.json').write_text(envelope,encoding='utf-8')
                        receipt.update(state='completed',error='',sha256=hashlib.sha256(saved.read_bytes()).hexdigest())
                        web.write_record(recovery,receipt)
                        shutil.copyfile(saved,target)
                        _adopt(folder,record,recovery,receipt,target)
                        return target
                    # A concrete refusal/size failure is terminal for this export.
                    text=reply.inner_text()
                    if re.search(r'"error"\s*:\s*"(?:source_or_result_missing|transfer_too_large|binary_changed)',text):
                        raise ValueError('Chưa xuất được dữ liệu phù hợp để nhận bài.')
                if time.monotonic()-last_notice>=5:
                    progress('Đang nhận và kiểm tra dữ liệu bài giảng…')
                    last_notice=time.monotonic()
                page.wait_for_timeout(250)
        raise ValueError('Hết khoảng theo dõi bước nhận dữ liệu bài giảng.')
    except web.BrowserProblem:
        raise
    except Exception as exc:
        receipt.update(error='file_transfer',failure_type=type(exc).__name__)
        web.write_record(recovery,receipt)
        raise web.BrowserProblem('file_transfer','Chưa nhận đủ dữ liệu bài giảng; phần đã hoàn tất được giữ để tiếp tục.') from exc
