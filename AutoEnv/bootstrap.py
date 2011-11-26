import logging as loggingModule

from . import environment

class Bootstrap(object):
    """Bootstrap object that helps to automatically set up your applications environment."""

    _env = _logger = None

    def __init__(self, envDir, logging=False, reqFile=None, requirements=None):
        if logging:
            loggingModule.basicConfig()
            self._logger = loggingModule.getLogger()
            self._logger.setLevel(loggingModule.DEBUG)

        self._env = environment.Environment(envDir, createDir=True)
        self._env.activate()

        if reqFile:
            self.installFromReqFile(reqFile)

        if requirements:
            self.installFromReqStr(requirements)

    install = property(lambda s: s._env.install)
    installFromReqFile = property(lambda s: s._env.installFromReqFile)
    installFromReqStr = property(lambda s: s._env.installFromReqStr)

# vim: set sts=4 sw=4 et :
