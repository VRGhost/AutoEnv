import os
import sys
import subprocess
import tempfile
import shutil

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
TMP_DIR = os.path.join(PROJECT_ROOT, "tmp")

def execTestCode(code, install_packages=()):
    _args = [sys.executable, "-m", "AutoEnv", "--exec", code]
    
    if install_packages:
        _args.extend(("--install", ) + tuple(install_packages))

    _testDir = tempfile.mkdtemp(dir=TMP_DIR)
    _args += ["--env_dir", _testDir]

    try:
        return subprocess.call(_args, cwd=PROJECT_ROOT)
    finally:
        shutil.rmtree(_testDir)

# vim: set sts=4 sw=4 et :
