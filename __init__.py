# A file that gets executed when this project is imported as a library

from . import AutoEnv as AutoEnv_pkg
from .AutoEnv import *

# override 'hotshot' function to make it even more hotshot
def hotshot(rootDir=None, envDirName="_env", relocatable=True, dynamicInstall=True):
    if not rootDir:
        import os
        _thisDir = os.path.realpath(os.path.dirname(__file__))
        _parent = os.path.dirname(_thisDir)
        rootDir = _parent
    return AutoEnv_pkg.hotshot(rootDir, envDirName, relocatable, dynamicInstall)

# vim: set sts=4 sw=4 et :
