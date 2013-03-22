"""Subprocess wrapping."""

import logging
import subprocess
import threading

class _StreamHandler(threading.Thread):

    def __init__(self, handledPipe, newDataCallback):
        super(_StreamHandler, self).__init__()
        self.daemon = True

        self.pipe = handledPipe
        self.cb = newDataCallback

        self.start()

    def run(self):
        try:
            while True:
                _msg = self.pipe.readline()
                if not _msg:
                    break
                
                self.cb(self, _msg)
        finally:
            self.cb(self, '')

class Popen(subprocess.Popen):
    
    def __init__(self, cmd, forceNoStdRedirect=False, **kwargs):
        # stdout & stderr arguments are ignored.
        kwargs.pop("stdout", None)
        kwargs.pop("stderr", None)

        if not forceNoStdRedirect:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.PIPE

        super(Popen, self).__init__(cmd, **kwargs)

        if not forceNoStdRedirect:
            self._stdoutProc = _StreamHandler(self.stdout, self.cb)
            self._stderrProc = _StreamHandler(self.stderr, self.cb)

            self.stdout = None
            self.stderr = None

    def cb(self, handler, msg):
        if not msg:
            # End of stream
            return
        
        if handler is self._stdoutProc:
            _handler = lambda msg: logging.debug("subproc stdout> {0}".format(msg))
        else:
            _handler = lambda msg: logging.warning("subproc stderr> {0}".format(msg))
        _handler(msg.rstrip())


def call(*args, **kwargs):
    return Popen(*args, **kwargs).wait()

# vim: set sts=4 sw=4 et :
