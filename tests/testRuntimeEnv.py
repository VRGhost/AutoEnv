
import unittest

import shutil

from . import unittestEnv

import AutoEnv

class TestBasicEnvGeneration(unittest.TestCase):
    """Test runtime environment modification."""

    def setUp(self):
        self.envDir = unittestEnv.mkTempDir()
        self.env = AutoEnv.Environment(self.envDir)
        self.env.activate()

    def tearDown(self):
        shutil.rmtree(self.envDir)

    def testInstall(self):
        with self.assertRaises(ImportError):
            import wget

        self.env.install("wget")

        self.assertEqual(self.env.getPkgInfo("wget")["installed"], True)

        import wget
        self.assertNotEqual(wget, None, "Wget module must be present now")

# vim: set sts=4 sw=4 et :
