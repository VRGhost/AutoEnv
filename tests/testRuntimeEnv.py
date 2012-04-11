
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

        self.assertTrue(self.env.getSinglePkgInfo("wget"))

        import wget
        self.assertTrue(wget, "Wget module must be present now")

    def testInstallIfMissing(self):
        with self.assertRaises(ImportError):
            import bliss

        # Test that successive calls do not have any effect
        for _x in xrange(10):
            self.assertTrue(self.env.installIfMissing("bliss"))

        import bliss
        self.assertTrue(bliss, "Bliss module must be present now")

        # Test that successive calls do not have any effect
        for _x in xrange(10):
            self.env.installIfMissing("bliss")


# vim: set sts=4 sw=4 et :
