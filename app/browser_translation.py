"""Read compact, durable translation batches through the signed-in web UI."""

import hashlib
import json
import shutil
import time
from pathlib import Path

from . import browser_automation as web
from .conversion_progress import emit_progress, measured, scoped_progress
from .translation_batches import TranslationCache, batch_items, parse_response, prompt, signature


def _read_text(page, record):
    message = web.latest_reply(page, record.get('assistant_before',0), record.get('assistant_ids_before'))
    if message is None:
        return ''
    blocks = message.locator('pre code').all()
    if len(blocks) == 1:
        return blocks[0].inner_text()
    prose = message.locator('[data-markdown-text-style="assistant-message"]:not([data-markdown-text-tone="tertiary"])')
    if prose.count() == 1:
        return prose.inner_text()
    return message.inner_text()


def _prepare_page(context, task, record, cancel):
    from .browser_capabilities import select_best_model, select_reasoning
    from .browser_receipt import recover_submission

    # Chrome restores this tool-owned profile's tabs. Reuse the saved task's
    # exact conversation instead of accumulating another copy on every retry.
    saved = record.get('url')
    page = next((p for p in context.pages if saved and not p.is_closed() and p.url == saved),None)
    if page is None:
        page = context.new_page()
    page.set_default_timeout(10000)
    folder,request = task['folder'],task['request']
    try:
        if record['state'] == 'submitting':
            page = recover_submission(context,page,folder,record,request,cancel)
        else:
            if page.url != (record['url'] or web.CHATGPT) or not web.signed_in(page):
                web.navigate(page,record['url'] or web.CHATGPT,cancel)
            web.require_account(page,cancel)
        if record['state'] == 'prepared':
            if web.conversation_url(page.url):
                raise web.BrowserProblem('interface','Chưa mở được phiên riêng cho cụm nội dung mới.')
            record.update(require_highest_model=True,model=select_best_model(page),reasoning=select_reasoning(page))
            web.write_record(folder,record)
            outgoing = (prompt(request['config'],task['items'],task['id']) if task['kind']=='language' else request['prompt'])
            files = [folder/request['config']['source_file']] if task['kind']=='visual' else []
            web.submit(page,folder,record,outgoing,cancel,files=files)
        return page
    except Exception:
        page.close()
        raise


def _visual_followup(task, cancel, message=None):
    """One known-result correction/export; never resend an uncertain turn."""
    from .browser_receipt import intent_prompt, matching_users

    page,record = task['page'],task['record']
    if record.get('followups'):
        raise web.BrowserProblem('result' if message else 'no_file',
            'Một nhóm slide chưa hoàn chỉnh; các phần đã nhận được giữ để tiếp tục.')
    sent = intent_prompt(task['folder'],record,task['request'])
    matches = matching_users(page,sent)
    if matches != [page.locator(web.USER).count()-1]:
        raise web.BrowserProblem('submission','Chưa xác nhận đúng lượt xử lý; giữ bài để kiểm tra, không gửi trùng.')
    record['followups']=1
    web.write_record(task['folder'],record)
    correction = ('Chỉ sửa các slide/lỗi cụ thể sau trong PowerPoint vừa trả về: '+message+
                  ' Giữ nguyên các slide khác; không kiểm kê hoặc render lại toàn bộ bài. '
                  'Giữ nguyên media thay thế nhẹ và quan hệ video/audio. '
                  'Dùng nguồn đã gửi trong cuộc trò chuyện này; không cần tải lại. Xuất lại đúng file .pptx tải được.'
                  if message else web.EXPORT_PROMPT)
    web.submit(page,task['folder'],record,correction,cancel)
    task.update(text='',stable=None)


def _correction_errors(quality):
    from .slide_quality import grouped_quality_messages

    # CHECK warnings on early slides must not crowd the actual FAIL errors
    # off a limited list, causing a costly correction that misses later slides.
    failures={'slides':[{'slide':row['slide'],'issues':[i for i in row['issues'] if i['severity']=='FAIL']}
                        for row in quality['slides']]}
    return '; '.join(grouped_quality_messages(failures))


def _visual_tasks(folder, request, account):
    from .chatgpt_handoff import load_request, make_prompt
    from .pptx_parts import subset
    from .pptx_transport import proxy

    config = request['config']
    manifest = json.loads((folder/'native-input.json').read_text(encoding='utf-8'))
    indices = manifest.get('visual_slides',[])
    plan_path = folder/'visual-plan.json'
    if plan_path.exists():
        groups = json.loads(plan_path.read_text(encoding='utf-8'))
        if sorted(i for group in groups for i in group) != indices:
            raise web.BrowserProblem('record','Nhóm slide không còn khớp tài liệu nguồn.')
    else:
        # Free/unknown plans use a single visual attachment, preserving scarce
        # upload allowances. Paid plans can process smaller visual decks.
        size = 8 if account.get('plan') in {'plus','pro','business','enterprise','edu'} else max(1,len(indices))
        groups = [indices[i:i+size] for i in range(0,len(indices),size)]
        plan_path.write_text(json.dumps(groups),encoding='utf-8')
    tasks = []
    for group in groups:
        key = signature({'source':config['source_sha256'],'slides':group,'mode':config['conversion_format']})[:24]
        subfolder = folder/'visual-batches'/key
        subfolder.mkdir(parents=True,exist_ok=True)
        if not (subfolder/'config.json').exists():
            original = subset(folder/config['source_file'],group,subfolder/'tai-lieu-day-du.pptx')
            source = subfolder/'tai-lieu-goc.pptx'
            transport = proxy(original,source)
            subconfig = {**config,'conversion_engine':'web_deck_v1','speed_pipeline':0,'quality_review_version':0,
                         'source_file':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                         'source_original_name':config.get('source_original_name','')+' · nhóm slide '+','.join(map(str,group))}
            subconfig['media_restore'] = transport['restore']
            subconfig['media_references'] = transport['media_references']
            subconfig['transport_bytes'] = {key:transport[key] for key in ('original_bytes','upload_bytes','offloaded_bytes')}
            subconfig.pop('native_input_sha256',None)
            (subfolder/'PROMPT.txt').write_text(make_prompt(subconfig,source.name),encoding='utf-8')
            (subfolder/'config.json').write_text(json.dumps(subconfig,ensure_ascii=False),encoding='utf-8')
        prepared = load_request(subfolder)
        tasks.append({'kind':'visual','id':key,'folder':subfolder,'indices':group,'request':prepared,
                      'restore':prepared['config'].get('media_restore',{}),'target':subfolder/'result.pptx'})
    return tasks


def convert_locked(account, request, cancel, progress, *, timeout=900, observed=None):
    """One account/context, up to two independent UI tabs.

    A crashed/uncertain send is reconciled, never replaced by a new prompt.
    Completed units are cached before a new chunk is started.
    """
    from playwright.sync_api import sync_playwright

    from .browser_capabilities import detect_plan
    from .browser_wait import ResponseWait, stale_refresh
    from .native_bilingual import assemble

    folder = Path(request['folder'])
    config = request['config']
    record = web.read_record(folder,account['id'])
    manifest_path = folder/'native-input.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if signature(manifest) != config.get('native_input_sha256'):
        raise web.BrowserProblem('record','Dữ liệu chuyển đổi đã thay đổi; giữ bài để kiểm tra.')
    items = manifest['units']
    cache = TranslationCache(folder.parent.parent,config)
    values, unique, aliases = {}, {}, {}
    for item in items:
        value = cache.get(item)
        if value is None and item['language'] == 'neutral':
            value = {'en':item['text']}
            if config['conversion_format'] == 'integrated_keywords':
                value['mixed'] = item['text']
        if value is not None:
            values[item['id']] = value
            continue
        key = signature({'text':item['text'],'numbers':item['numbers']})
        if key in unique:
            aliases.setdefault(unique[key]['id'],[]).append(item)
        else:
            unique[key] = item
    plan_path = folder/'language-plan.json'
    by_id = {item['id']:item for item in unique.values()}
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding='utf-8'))
        # Completed cached entries were removed from unique above. Recover the
        # immutable original plan from the verified source manifest instead.
        all_items = {item['id']:item for item in items}
        try:
            batches = [[all_items[key] for key in batch] for batch in plan]
        except (KeyError,TypeError) as exc:
            raise web.BrowserProblem('record','Bản ghi cụm nội dung không khớp nguồn.') from exc
    else:
        batches = batch_items(list(by_id.values()))
        plan_path.write_text(json.dumps([[item['id'] for item in batch] for batch in batches]),encoding='utf-8')
    pending, active, visual_results = [], [], []
    for batch in batches:
        if all(item['id'] in values for item in batch):
            continue
        key = signature({'version':1,'config':cache.policy,'items':batch})[:24]
        subfolder = folder/'translation-batches'/key
        subfolder.mkdir(parents=True,exist_ok=True)
        completed = web.read_record(subfolder,account['id'])
        saved_result = subfolder/'result.json'
        if completed['state']=='completed' and saved_result.is_file():
            try:
                saved = json.loads(saved_result.read_text(encoding='utf-8'))
                if signature(saved)!=completed.get('result_sha256') or not isinstance(saved,dict):
                    raise ValueError('Bản dịch đã lưu không khớp checksum.')
                verified = parse_response(json.dumps({'batch':key,'items':[{'id':k,**v} for k,v in saved.items()]},
                    ensure_ascii=False),batch,key,config['conversion_format'])
            except (ValueError,TypeError,AttributeError) as exc:
                raise web.BrowserProblem('record','Bản dịch đã lưu không còn hợp lệ; giữ bài để kiểm tra.') from exc
            for item in batch:
                value=verified[item['id']]
                cache.put(item,value)
                values[item['id']]=value
                for alias in aliases.get(item['id'],[]):
                    cache.put(alias,value)
                    values[alias['id']]=value
            continue
        pending.append({'kind':'language','id':key,'folder':subfolder,'items':batch,'request':request})
    visual_done = 0
    for task in _visual_tasks(folder,request,account):
        child = web.read_record(task['folder'],account['id'])
        if child['state']=='completed' and task['target'].is_file() and (
                child.get('sha256')==hashlib.sha256(task['target'].read_bytes()).hexdigest()):
            visual_results.append((task['target'],task['indices'],task['restore']))
            visual_done += len(task['indices'])
        else:
            pending.append(task)
    total = len(items)+len(manifest.get('visual_slides',[]))*3
    # Start the long visual task alongside the first language batch.
    if len(pending)>1:
        first_visual=next((i for i,task in enumerate(pending) if task['kind']=='visual'),None)
        if first_visual is not None and first_visual>1:
            pending.insert(1,pending.pop(first_visual))
    record.update(engine='hybrid_v1')

    def notify():
        done = len(values)+visual_done*3
        emit_progress(progress,'translate','Đang biên soạn từng phần bài giảng…',done,total)

    notify()
    try:
        if pending:
            with sync_playwright() as playwright:
                context = web.open_context(playwright,account,background=True,cancel=cancel)
                try:
                    probe = next((p for p in context.pages if not p.is_closed() and web.signed_in(p)),None)
                    if probe is None:
                        probe = context.new_page()
                        web.navigate(probe,web.CHATGPT,cancel)
                    web.require_account(probe,cancel)
                    plan = detect_plan(probe,web.PROFILE)
                    parallel = 2
                    record['plan'] = plan
                    web.write_record(folder,record)
                    if observed:
                        observed(account['id'],plan,record.get('model',''))
                    while pending or active:
                        web.check_cancel(cancel)
                        while pending and len(active) < parallel:
                            task = pending.pop(0)
                            subfolder = task['folder']
                            child = web.read_record(subfolder,account['id'])
                            previous=dict(record)
                            record.update(state='submitting' if child['state']=='prepared' else child['state'],error='')
                            web.write_record(folder,record)
                            try:
                                page = _prepare_page(context,task,child,cancel)
                            except web.BrowserProblem as exc:
                                if exc.code=='interface' and child['state']=='prepared' and active:
                                    record.clear()
                                    record.update(previous)
                                    web.write_record(folder,record)
                                    pending.insert(0,task)
                                    parallel=1  # A busy composer never causes another send/account switch.
                                    break
                                raise
                            record.update(state='waiting',url=child['url'],model=child.get('model',record.get('model','')))
                            web.write_record(folder,record)
                            budget = ResponseWait(subfolder,child,timeout)
                            budget.checkpoint(force=True)
                            active.append({**task,'page':page,'record':child,'budget':budget,'stable':None,'text':'','reconnects':0,
                                           'started':time.monotonic()})
                        for task in list(active):
                            page,child = task['page'],task['record']
                            web.page_problem(page)
                            generating = bool(web.visible(page,web.STOP))
                            text = _read_text(page,child)
                            if task['kind']=='visual' and not generating:
                                from . import browser_text_transport

                                candidate = task['target'].is_file() and child.get('candidate_send_sha256')==child.get('send_sha256')
                                if candidate and hashlib.sha256(task['target'].read_bytes()).hexdigest()!=child.get('candidate_sha256'):
                                    raise web.BrowserProblem('record','Bài giảng đã nhận bị thay đổi; giữ tác vụ để kiểm tra.')
                                recovering = bool(child.get('receive_data_key'))
                                link = web.result_link(page,child.get('assistant_before',0),
                                                       assistant_ids_before=child.get('assistant_ids_before'))
                                if link or candidate or recovering:
                                    if not candidate:
                                        if recovering:
                                            browser_text_transport.receive(context,page,task['folder'],child,task['request'],
                                                task['target'],cancel,scoped_progress(progress,'translate'))
                                        else:
                                            try:
                                                download = web.receive_download(page,link,cancel,progress=scoped_progress(progress,'translate'))
                                                if Path(download.suggested_filename).suffix.casefold()!='.pptx' or not download.path():
                                                    raise web.BrowserProblem('download','Một nhóm slide chưa nhận được PowerPoint hợp lệ.')
                                                from .document_limits import MAX_POWERPOINT_BYTES
                                                if Path(download.path()).stat().st_size>MAX_POWERPOINT_BYTES:
                                                    raise web.BrowserProblem('download','Nhóm PowerPoint kết quả vượt giới hạn.')
                                                download.save_as(str(task['target']))
                                                child.update(candidate_sha256=hashlib.sha256(task['target'].read_bytes()).hexdigest(),
                                                             candidate_send_sha256=child['send_sha256'])
                                                web.write_record(task['folder'],child)
                                            except web.BrowserProblem as exc:
                                                if exc.code!='file_transfer':
                                                    raise
                                                browser_text_transport.receive(context,page,task['folder'],child,task['request'],
                                                    task['target'],cancel,scoped_progress(progress,'translate'))
                                    inspection = web.inspect_returned_deck(task['target'],
                                        task['folder']/task['request']['config']['source_file'],
                                        config['conversion_format'],config['style'])
                                    if len(inspection['blocks']) < 1:
                                        raise web.BrowserProblem('download','Nhóm slide chưa có nội dung hợp lệ.')
                                    from pptx import Presentation

                                    from .pptx_transport import verify_media
                                    try:
                                        if len(Presentation(task['target']).slides)!=len(task['indices']):
                                            raise ValueError('Nhóm kết quả chưa giữ đủ số slide nguồn.')
                                        verify_media(task['target'],task['request']['config'].get('media_references',[]),task['restore'])
                                    except ValueError as exc:
                                        _visual_followup(task,cancel,str(exc))
                                        continue
                                    # A known incomplete result gets one focused correction, never
                                    # another whole-deck conversion or an unbounded repair loop.
                                    quality=inspection['slide_quality']
                                    failures=[(r['slide'],i['code']) for r in quality['slides'] for i in r['issues']
                                              if i['severity']=='FAIL']
                                    previous=task['folder']/'before-correction.pptx'
                                    if failures and not child.get('followups'):
                                        shutil.copyfile(task['target'],previous)
                                        child['quality_failures_before']=failures
                                        _visual_followup(task,cancel,_correction_errors(quality))
                                        continue
                                    old=child.get('quality_failures_before')
                                    if old and previous.is_file() and not set(failures)<set(map(tuple,old)):
                                        shutil.copyfile(previous,task['target'])
                                    child.update(state='completed',error='',sha256=hashlib.sha256(task['target'].read_bytes()).hexdigest())
                                    web.write_record(task['folder'],child)
                                    visual_results.append((task['target'],task['indices'],task['restore']))
                                    visual_done += len(task['indices'])
                                    task['budget'].checkpoint(force=True)
                                    page.close()
                                    active.remove(task)
                                    notify()
                                    continue
                                if text.strip():
                                    if text!=task['text']:
                                        task.update(text=text,stable=time.monotonic())
                                    elif task['stable'] is not None and time.monotonic()-task['stable']>=4:
                                        _visual_followup(task,cancel)
                                        continue
                                elif time.monotonic()-task['started'] >= 60 and web.latest_reply(
                                        page,child.get('assistant_before',0),child.get('assistant_ids_before')) is not None:
                                    _visual_followup(task,cancel)
                                    task['started']=time.monotonic()
                                    continue
                            if task['kind']=='language' and not generating and text.strip():
                                if text != task['text']:
                                    task.update(text=text,stable=time.monotonic())
                                # A complete validated JSON needs no stability delay.
                                # Save it before another finished task can fail its
                                # download and close this shared browser context.
                                if task['stable'] is not None:
                                    try:
                                        result = parse_response(text,task['items'],task['id'],config['conversion_format'])
                                    except (ValueError,TypeError) as exc:
                                        if time.monotonic()-task['stable'] < 1:
                                            task['budget'].checkpoint()
                                            continue  # Let a partially rendered reply finish.
                                        if child.get('followups'):
                                            raise web.BrowserProblem('translation_result',
                                                'Một cụm nội dung chưa đủ bản dịch hợp lệ; các phần đã xong được giữ lại.') from exc
                                        # The invalid reply is known, so one correction is safe. An uncertain
                                        # submission remains under the normal durable receipt mechanism.
                                        child['followups'] = 1
                                        web.write_record(task['folder'],child)
                                        correction = 'Sửa JSON của cụm này: '+str(exc)+'\n'+prompt(config,task['items'],task['id'])
                                        web.submit(page,task['folder'],child,correction,cancel)
                                        task.update(text='',stable=None)
                                        continue
                                    for item in task['items']:
                                        value = result[item['id']]
                                        cache.put(item,value)
                                        values[item['id']] = value
                                        for alias in aliases.get(item['id'],[]):
                                            cache.put(alias,value)
                                            values[alias['id']] = value
                                    child.update(state='completed',error='',result_sha256=signature(result))
                                    web.write_record(task['folder'],child)
                                    task['budget'].checkpoint(force=True)
                                    (task['folder']/'result.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
                                    page.close()
                                    active.remove(task)
                                    notify()
                                    continue
                            remaining = task['budget'].checkpoint()
                            if remaining <= 0 and not task['budget'].extend_active(generating):
                                child['wait_exhausted'] = True
                                web.write_record(task['folder'],child)
                                record.update(wait_exhausted=True,response_wait=child.get('response_wait',{}),
                                              send_sha256=child.get('send_sha256',''))
                                raise web.BrowserProblem('timeout','Một phần nội dung cần thêm thời gian; bản dịch đã nhận được giữ để tiếp tục.')
                            interrupted=web.interrupted_answer(page)
                            stale=stale_refresh(child,text,generating=generating,after=120)
                            if interrupted or stale:
                                if interrupted and task['reconnects'] >= 2:
                                    raise web.BrowserProblem('network','Kết nối tạm gián đoạn; các phần đã hoàn tất được giữ lại.')
                                # A quiet but active thinking turn is not proof
                                # of a broken connection. After bounded passive
                                # refreshes, keep observing the original wait
                                # budget instead of falsely pausing as network.
                                if task['reconnects'] < 2:
                                    task['reconnects'] += 1
                                    web.write_record(task['folder'],child)
                                    web.navigate(page,child['url'],cancel)
                                    web.require_account(page,cancel)
                                    task.update(text='',stable=None)
                            task['budget'].checkpoint()
                        notify()
                        if cancel.wait(.5):
                            web.check_cancel(cancel)
                finally:
                    for task in active:
                        task['budget'].checkpoint(force=True)
                    context.close()
        web.check_cancel(cancel)
        emit_progress(progress,'assemble','Đang hoàn thiện PowerPoint và nội dung trợ giảng…')
        target = folder/'bai-giang-song-ngu.pptx'
        native = folder/'native-result.pptx'
        with measured(progress, 'local.assemble'):
            if items:
                assemble(folder/config['source_file'],native,manifest,values,config['conversion_format'])
            else:
                shutil.copyfile(folder/config['source_file'],native)
            if visual_results:
                from .pptx_parts import merge
                merge(native,visual_results,target)
            else:
                native.replace(target)
        from .slide_repair import repair_and_inspect
        with measured(progress, 'local.repair'):
            checked = repair_and_inspect(target,folder,source=folder/config['source_file'],
                mode=config['conversion_format'],style=config['style'],cancel=cancel,progress=progress)
        if Path(checked['path'])!=target:
            Path(checked['path']).replace(target)
        record.update(state='completed',error='',stage='completed',sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        web.write_record(folder,record)
        return {'path':str(target),'url':record['url'],'cached':False,'inspection':checked.get('inspection')}
    except Exception as exc:
        record.update(error=exc.code if isinstance(exc,web.BrowserProblem) else 'browser',stage='translate')
        web.write_record(folder,record)
        raise
