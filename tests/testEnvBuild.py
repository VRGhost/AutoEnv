import unittest

from . import unittestEnv

class TestBasicEnvGeneration(unittest.TestCase):

    def te2stPipInstall(self):
        _rc = unittestEnv.execTestCode(';'.join([
            "import pip, os",
            "assert {0} in os.path.abspath(pip.__file__)".format(unittestEnv.TMP_DIR),
        ]))
        self.assertEqual(_rc, 0)

    def testInstallWithPip(self):
        _rc = unittestEnv.execTestCode(';'.join([
            "import wget",
            "print wget",
            "assert wget is not None",
        ]), install_packages=["wget", "antigravity"])
        self.assertEqual(_rc, 0)

# vim: set sts=4 sw=4 et :
