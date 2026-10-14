import io
import json
from pathlib import Path
from threading import Event
from urllib.parse import urlsplit

import pytest
from PIL import Image
from pptx import Presentation
from pptx.util import Inches

from app import browser_automation as web
from app.browser_accounts import BrowserAccounts
from app.chatgpt_handoff import prepare_request
from app.conversion_progress import ConversionProgress

HTML = '''<html><head><meta charset="utf-8"></head><body><button data-testid="accounts-profile-button">Fixture</button>
<textarea id="prompt-textarea"></textarea><input type="file" multiple><div id="attached"></div>
<button data-testid="send-button" id="send">Send</button>
<button data-testid="stop-button" id="stop" hidden>Stop</button><div id="messages"></div>
<script>
const initial=INITIAL, chat=CHAT, bad=BAD; let count=0;
function finish(prompt){
 const native=prompt.includes('NỘI DUNG:');
 const answer=document.createElement('div');answer.dataset.messageAuthorRole='assistant';
 answer.dataset.messageId='answer-'+count;
 if(native){const data=JSON.parse(prompt.split('NỘI DUNG:').at(-1));
  const batch=prompt.match(/"batch": *"([^"]+)"/)[1];
  const result={batch,items:data.map(i=>({id:i.id,en:bad&&count===1?'Missing number':'The object has a velocity of ⟦BLC0⟧ m/s.'}))};
  const pre=document.createElement('pre'),code=document.createElement('code');code.textContent=JSON.stringify(result);pre.append(code);answer.append(pre);
 }else{answer.innerHTML='<a href="/backend-api/files/result.pptx">bai-giang-song-ngu.pptx</a>';}
 document.querySelector('#messages').append(answer);document.querySelector('#stop').hidden=true;
 console.log('DONE:'+JSON.stringify({native,url:location.pathname}));
}
function addUser(prompt){const user=document.createElement('div');user.dataset.messageAuthorRole='user';user.textContent=prompt;document.querySelector('#messages').append(user);}
if(initial){count=initial.count;addUser(initial.prompt);finish(initial.prompt);}
document.querySelector('input').onchange=e=>{document.querySelector('#attached').replaceChildren();for(const f of e.target.files){const n=document.createElement('span');n.textContent=f.name;document.querySelector('#attached').append(n);}};
document.querySelector('#send').onclick=()=>{count++;const prompt=document.querySelector('textarea').value;
 addUser(prompt);history.pushState({},'',chat);document.querySelector('#stop').hidden=false;
 console.log('SENT:'+JSON.stringify({prompt,count,url:location.pathname,files:[...document.querySelector('input').files].map(f=>f.name)}));
 setTimeout(()=>finish(prompt),prompt.includes('NỘI DUNG:')?2500:1200);
};</script></body></html>'''


@pytest.fixture
def translation_site(tmp_path,monkeypatch):
    from app import browser_capabilities

    source=tmp_path/'source.pptx'
    deck=Presentation()
    deck.slide_width,deck.slide_height=Inches(13.333),Inches(7.5)
    first=deck.slides.add_slide(deck.slide_layouts[6])
    first.shapes.add_textbox(Inches(.5),Inches(2),Inches(12),Inches(3)).text='Vật có vận tốc 12 m/s.'
    second=deck.slides.add_slide(deck.slide_layouts[6])
    second.shapes.add_textbox(Inches(.5),Inches(.5),Inches(8),Inches(1)).text='Năng lượng của vật'
    image=io.BytesIO()
    Image.new('RGB',(800,400),'red').save(image,format='PNG')
    second.shapes.add_picture(io.BytesIO(image.getvalue()),Inches(1),Inches(2),width=Inches(10),height=Inches(4))
    deck.save(source)
    returned=tmp_path/'returned.pptx'
    from app.pptx_parts import subset
    subset(source,[2],returned)
    candidate=Presentation(returned)
    candidate.slides[0].shapes[0].text='Năng lượng của vật\nEnergy of the object'
    candidate.slides[0].notes_slide.notes_text_frame.text='VI: Năng lượng của vật\nEN: Energy of the object'
    candidate.save(returned)
    store=BrowserAccounts(tmp_path/'library')
    account=store.add('Fixture')
    store.observe(account['id'],'free')
    request=prepare_request(tmp_path/'library',{'title':'Vận tốc','subject':'Vật lý','education_level':'THPT','grade':'10',
        'conversion_format':'english_only','preset':'standard','style':'source','provider':'browser_web',
        'require_highest_model':True,'speed_pipeline':1,'prompt_speed_version':1},source)
    capture={'sent':[],'done':[],'chats':{},'pages':0,'bad':False,'in_flight':0,'maximum':0,'contexts':0,'errors':[]}
    original=web.open_context

    def opening(playwright,account,**kwargs):
        context=original(playwright,account,**kwargs)
        capture['contexts']+=1

        def watch(page):
            page.on('pageerror',lambda error:capture['errors'].append(str(error)))
            def console(message):
                if message.text.startswith('SENT:'):
                    value=json.loads(message.text[5:])
                    capture['sent'].append(value)
                    capture['chats'][value['url']]=value
                    capture['in_flight']+=1
                    capture['maximum']=max(capture['maximum'],capture['in_flight'])
                elif message.text.startswith('DONE:'):
                    capture['done'].append(json.loads(message.text[5:]))
                    capture['in_flight']=max(0,capture['in_flight']-1)
            page.on('console',console)
        context.on('page',watch)
        for page in context.pages:
            watch(page)

        def route(req):
            path=urlsplit(req.request.url).path
            if path=='/backend-api/files/result.pptx':
                req.fulfill(body=returned.read_bytes(),headers={
                    'Content-Type':'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'Content-Disposition':'attachment; filename="result.pptx"'})
            else:
                capture['pages']+=1
                chat='/c/batch-'+str(capture['pages'])
                body=HTML.replace('INITIAL',json.dumps(capture['chats'].get(path))).replace('CHAT',json.dumps(chat)).replace('BAD',json.dumps(capture['bad']))
                req.fulfill(content_type='text/html; charset=utf-8',body=body)
        context.route('**/*',route)
        return context
    monkeypatch.setattr(web,'open_context',opening)
    monkeypatch.setattr(browser_capabilities,'detect_plan',lambda *_:'free')
    monkeypatch.setattr(browser_capabilities,'select_best_model',lambda *_:'Thinking')
    monkeypatch.setattr(browser_capabilities,'select_reasoning',lambda *_:'Suy luận trên web: High')
    # Geometry is separately checked against real Office by the Qt/native smoke.
    # Keep browser protocol fixtures independent of Office process availability.
    monkeypatch.setattr('app.slide_repair.repair_and_inspect',lambda path,*a,**kw:{'path':str(path)})
    return store,request,capture,source


def test_parallel_text_and_visual_receive_out_of_order_and_merge_correctly(translation_site):
    store,request,capture,source=translation_site
    progress=ConversionProgress(request['folder'],lambda _:None)
    try:
        result=web.convert(store.get(),store.root,request['folder'],Event(),progress,timeout=20)
    except Exception:
        assert not capture['errors'],capture['errors']
        raise
    assert capture['maximum']==2
    assert len(capture['sent'])==2 and len(capture['sent'][0]['files'])==0
    assert capture['done'][0]['native'] is False
    deck=Presentation(result['path'])
    assert len(deck.slides)==2
    assert 'velocity' in deck.slides[0].shapes[0].text
    assert 'Energy of the object' in deck.slides[1].shapes[0].text
    assert len(Presentation(source).slides)==2
    for journal in Path(request['folder']).glob('*-batches/*/browser-job.json'):
        record=json.loads(journal.read_text(encoding='utf-8'))
        assert record['highest_model_verified'] and record['reasoning_verified']
    again=web.convert(store.get(),store.root,request['folder'],Event(),progress,timeout=20)
    assert again['cached'] and len(capture['sent'])==2


def test_lost_receipt_resumes_old_chat_without_duplicate_send(translation_site,monkeypatch):
    store,request,capture,_=translation_site
    original=web.submit
    failed=[]

    def lose_receipt(*args,**kwargs):
        original(*args,**kwargs)
        if not failed:
            failed.append(True)
            raise web.BrowserProblem('receipt','Fixture lost acknowledgement')

    monkeypatch.setattr(web,'submit',lose_receipt)
    with pytest.raises(web.BrowserProblem):
        web.convert(store.get(),store.root,request['folder'],Event(),lambda _:None,timeout=20)
    assert len(capture['sent'])==1
    result=web.convert(store.get(),store.root,request['folder'],Event(),lambda _:None,timeout=20)
    assert Path(result['path']).is_file() and len(capture['sent'])==2


def test_invalid_numeric_translation_gets_only_one_focused_correction(translation_site):
    store,request,capture,_=translation_site
    capture['bad']=True
    result=web.convert(store.get(),store.root,request['folder'],Event(),lambda _:None,timeout=20)
    native=[row for row in capture['sent'] if not row['files']]
    assert len(native)==2 and 'Sửa JSON' in native[1]['prompt']
    assert '12 m/s.' in Presentation(result['path']).slides[0].shapes[0].text


def test_received_batches_resume_local_merge_without_new_browser_or_send(translation_site,monkeypatch):
    store,request,capture,_=translation_site
    from app import pptx_parts
    original=pptx_parts.merge

    def fail(*args,**kwargs):
        raise OSError('Fixture local merge failure after all batches received')

    monkeypatch.setattr(pptx_parts,'merge',fail)
    with pytest.raises(OSError):
        web.convert(store.get(),store.root,request['folder'],Event(),lambda _:None,timeout=20)
    contexts=capture['contexts']
    monkeypatch.setattr(pptx_parts,'merge',original)
    result=web.convert(store.get(),store.root,request['folder'],Event(),lambda _:None,timeout=20)
    assert Path(result['path']).is_file()
    assert len([row for row in capture['sent'] if not row['files']])==1
    assert len([row for row in capture['sent'] if row['files']])==1
    assert capture['contexts']==contexts
