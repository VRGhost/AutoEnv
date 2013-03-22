from .environment import Environment
from .package import Package
from .bootstrap import Bootstrap

from .cmd import Command
from .cmd import SuccessSequence as SuccessiveCmdSeq

def hotshot(rootDir, envDirName, relocatable, dynamicInstall):
    """Create/invoke virtualenv with a call of single function."""
    import os

    _envRoot = os.path.realpath(os.path.join(rootDir, envDirName))
    if not os.path.exists(_envRoot):
        os.makedirs(_envRoot)

    _env = Environment(_envRoot, relocatable=relocatable, dynamicInstall=dynamicInstall)
    _env.activate()
    return _env


# vim: set sts=4 sw=4 et :
