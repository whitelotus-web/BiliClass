"""Native PowerPoint speaker buttons, separate from the hidden media object."""

import copy

from lxml import etree

from .source_deck import NS


def _node(parent, tag, **attributes):
    return etree.SubElement(parent, f"{{{NS['p']}}}{tag}", **{k: str(v) for k, v in attributes.items()})


def picture(media, identity, language, icon_relation, *, paused=False):
    result = copy.deepcopy(media)
    props = result.find('p:nvPicPr/p:cNvPr', NS)
    props.set('id', str(identity))
    props.set('name', 'BiliClass ' + ('pause ' if paused else 'control ') + language.upper())
    # Selection-pane hiding wins over animation visibility in PowerPoint.
    # The timing tree hides the pause button when the slide starts instead.
    props.set('hidden', '0')
    props.set('descr', ('Tạm dừng ' if paused else 'Đọc / đọc tiếp ') + language.upper())
    for link in props.findall('a:hlinkClick', NS):
        props.remove(link)
    application = result.find('p:nvPicPr/p:nvPr', NS)
    for child in list(application):
        application.remove(child)
    result.find('p:blipFill/a:blip', NS).set(f"{{{NS['r']}}}embed", icon_relation)
    return result


def add_controls(tree, controls, *, managed=False):
    """Each ready/pause click executes one short command sequence.

    The media node lives outside these sequences, so restarting a button's
    sequence does not restart audio that togglePause is meant to resume.
    """
    timing = tree.find('p:timing', NS)
    if timing is None:
        timing = etree.Element(f"{{{NS['p']}}}timing")
        following = tree.find('p:extLst', NS)
        tree.append(timing) if following is None else following.addprevious(timing)
    next_id = max([int(v) for v in timing.xpath('.//p:cTn/@id', namespaces=NS)] + [0])

    def clock(parent, **attributes):
        nonlocal next_id
        next_id += 1
        return _node(parent, 'cTn', id=next_id, **attributes)

    root = timing.find('p:tnLst/p:par/p:cTn[@nodeType="tmRoot"]', NS)
    if root is None:
        nodes = timing.find('p:tnLst', NS)
        if nodes is None:
            nodes = etree.Element(f"{{{NS['p']}}}tnLst")
            timing.insert(0, nodes)
        root = clock(_node(nodes, 'par'), dur='indefinite', restart='never', nodeType='tmRoot')
    children = root.find('p:childTnLst', NS)
    if children is None:
        children = _node(root, 'childTnLst')

    def target(parent, identity):
        _node(_node(parent, 'tgtEl'), 'spTgt', spid=identity)

    def visibility(parent, identity, visible):
        setter = _node(parent, 'set')
        behavior = _node(setter, 'cBhvr')
        clock(behavior, dur='1', fill='hold')
        target(behavior, identity)
        _node(_node(behavior, 'attrNameLst'), 'attrName').text = 'style.visibility'
        _node(_node(setter, 'to'), 'strVal', val='visible' if visible else 'hidden')

    def command(parent, identity, action):
        behavior = _node(_node(parent, 'cmd', type='call', cmd=action), 'cBhvr')
        clock(behavior, dur='1', fill='hold')
        target(behavior, identity)

    def effects(parent):
        effect = clock(_node(parent, 'par'), dur='1', fill='hold')
        _node(_node(effect, 'stCondLst'), 'cond', delay='0')
        return _node(effect, 'childTnLst')

    initial = effects(children) if not managed else None
    for media_id, ready_id, pause_id, _duration in controls:
        if not managed:
            visibility(initial, ready_id, True)
            visibility(initial, pause_id, False)
        media = _node(_node(children, 'audio'), 'cMediaNode', vol='80000')
        media_clock = clock(media, fill='hold', display='0')
        _node(_node(media_clock, 'stCondLst'), 'cond', delay='indefinite')
        target(media, media_id)
        if managed:
            # The bound Mascot session owns click/pause state. Native picture
            # animations must not hide its pause badge or start a second voice.
            # A neutral trigger gives PowerPoint its normal hand cursor. If a
            # hook is unavailable, clicking neither advances a build nor plays
            # audio: the only effect targets the already transparent media host.
            for trigger in (ready_id, pause_id):
                sequence = clock(_node(children, 'seq', concurrent='1'), restart='always', fill='hold',
                                 evtFilter='cancelBubble', nodeType='interactiveSeq')
                condition = _node(_node(sequence, 'stCondLst'), 'cond', evt='onClick', delay='0')
                target(condition, trigger)
                visibility(effects(_node(sequence, 'childTnLst')), media_id, True)
            continue
        for trigger, pause in ((ready_id, False), (pause_id, True)):
            sequence = clock(_node(children, 'seq', concurrent='1'), restart='always', fill='hold',
                             evtFilter='cancelBubble', nodeType='interactiveSeq')
            condition = _node(_node(sequence, 'stCondLst'), 'cond', evt='onClick', delay='0')
            target(condition, trigger)
            actions = effects(_node(sequence, 'childTnLst'))
            if not pause:
                for other_media, other_ready, other_pause, _ in controls:
                    if other_media != media_id:
                        command(actions, other_media, 'stop')
                        visibility(actions, other_ready, True)
                        visibility(actions, other_pause, False)
            command(actions, media_id, 'pause' if pause else 'togglePause')
            visibility(actions, ready_id, pause)
            visibility(actions, pause_id, not pause)
        finished = clock(_node(children, 'par'), restart='always', fill='hold', dur='1')
        condition = _node(_node(finished, 'stCondLst'), 'cond', evt='onEnd', delay='0')
        _node(condition, 'tn', val=media_clock.get('id'))
        reset = _node(finished, 'childTnLst')
        visibility(reset, ready_id, True)
        visibility(reset, pause_id, False)
