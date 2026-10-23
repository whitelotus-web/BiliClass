import queue
from types import SimpleNamespace

import pytest

from app.powerpoint import PowerPointSession


@pytest.mark.parametrize('responsive', [True,False])
def test_startup_timeout_follows_real_progress_instead_of_total_deck_preparation(monkeypatch,tmp_path,responsive):
    clock=[0]
    commands=[]
    failures=[]
    states=[]
    process=SimpleNamespace(alive=True,terminated=False)
    timeline=iter([(0,dict(starting=True,message='Opening')),
                   (40,dict(starting=True,message='Speakers 1/2')),
                   (80,dict(starting=True,message='Speakers 2/2')),
                   (120,dict(opened=True,active=False,slide=1)),(121,None)] if responsive else
                  [(0,dict(starting=True,message='Opening')),(46,None),(52,None)])

    class Events:
        def get(self,timeout):
            clock[0],state=next(timeline)
            if state is None:
                if responsive:
                    process.alive=False
                raise queue.Empty
            return state

        def get_nowait(self):
            raise queue.Empty

        def close(self):
            pass

    def terminate():
        process.alive=False
        process.terminated=True

    process.start=lambda:None
    process.is_alive=lambda:process.alive
    process.join=lambda timeout:None
    process.terminate=terminate
    channel=SimpleNamespace(put=commands.append,close=lambda:None)
    channels=iter((channel,Events()))
    context=SimpleNamespace(Queue=lambda:next(channels),Process=lambda **kwargs:process)
    monkeypatch.setattr('app.powerpoint.multiprocessing.get_context',lambda _:context)
    monkeypatch.setattr('app.powerpoint.time.monotonic',lambda:clock[0])
    session=PowerPointSession(tmp_path/'fixture.pptx',autostart=False)
    session.failed.connect(failures.append)
    session.stateChanged.connect(states.append)
    session.run()
    if responsive:
        assert not failures and not process.terminated and not commands
        assert any(state.get('opened') for state in states)
    else:
        assert len(failures)==1 and 'Opening' in failures[0]
        assert commands==[('stop',None)] and process.terminated
