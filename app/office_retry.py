"""Retry only explicit temporary COM call rejection, on the Office worker."""

import time


def is_busy(error):
    code = getattr(error, 'hresult', error.args[0] if error.args else None)
    return isinstance(code, int) and code & 0xffffffff in {0x80010001, 0x8001010a, 0x8001010b}


def call(action, *, timeout=2.5):
    deadline = time.monotonic() + timeout
    while True:
        try:
            return action()
        except Exception as error:
            if not is_busy(error) or time.monotonic() >= deadline:
                raise
            import pythoncom

            pythoncom.PumpWaitingMessages()
            time.sleep(min(.1, max(0, deadline - time.monotonic())))
